from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Count
from datetime import datetime, timedelta
import time

from .models import (
    AIContentRequest, NutritionPlan, HealthInsight,
    AIUsageStats, ContentTemplate
)
from .serializers import (
    AIContentRequestSerializer, NutritionPlanSerializer, HealthInsightSerializer,
    AIUsageStatsSerializer, ContentTemplateSerializer, WorkoutGenerationRequestSerializer,
    NutritionGenerationRequestSerializer, HealthAnalysisRequestSerializer,
    AIGenerationResponseSerializer, FeedbackSerializer
)
from core.ai_integrations.claude_client import ClaudeClient
from apps.users.models import MedicalData


class AIContentRequestListView(generics.ListAPIView):
    serializer_class = AIContentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AIContentRequest.objects.filter(user=self.request.user)
        content_type = self.request.query_params.get('content_type')
        status_filter = self.request.query_params.get('status')
        
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset


class NutritionPlanListCreateView(generics.ListCreateAPIView):
    serializer_class = NutritionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NutritionPlan.objects.filter(user=self.request.user, is_active=True)


class NutritionPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NutritionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NutritionPlan.objects.filter(user=self.request.user)


class HealthInsightListView(generics.ListAPIView):
    serializer_class = HealthInsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = HealthInsight.objects.filter(user=self.request.user)
        
        insight_type = self.request.query_params.get('type')
        priority = self.request.query_params.get('priority')
        unread_only = self.request.query_params.get('unread_only')
        
        if insight_type:
            queryset = queryset.filter(insight_type=insight_type)
        if priority:
            queryset = queryset.filter(priority=priority)
        if unread_only == 'true':
            queryset = queryset.filter(is_read=False, is_dismissed=False)
            
        return queryset


class HealthInsightDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = HealthInsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HealthInsight.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_workout_view(request):
    """Generate AI-powered workout plan"""
    serializer = WorkoutGenerationRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    preferences = serializer.validated_data
    start_time = time.time()
    
    # Build user profile
    user_profile = {
        'age': user.get_age(),
        'gender': user.get_gender_display() if user.gender else 'Not specified',
        'fitness_level': user.get_fitness_level_display(),
        'goals': user.get_fitness_goals(),
        'workout_duration': preferences.get('duration_minutes', user.preferred_workout_duration),
        'equipment': preferences.get('equipment_available', user.get_available_equipment()),
        'activity_level': user.get_activity_level_display(),
        'medical_conditions': 'None specified'  # Would integrate with medical data
    }
    
    # Create AI request record
    ai_request = AIContentRequest.objects.create(
        user=user,
        content_type='workout',
        status='processing',
        user_context=user_profile,
        prompt_context=preferences
    )
    
    try:
        # Use Claude to generate workout
        claude_client = ClaudeClient()
        workout_type = preferences.get('workout_type', 'general')
        
        ai_response = claude_client.generate_workout(user_profile, workout_type)
        generation_time = time.time() - start_time
        
        if ai_response['success']:
            # Update request record
            ai_request.status = 'completed'
            ai_request.generated_content = ai_response['workout']
            ai_request.tokens_used = ai_response.get('tokens_used', 0)
            ai_request.generation_time_seconds = round(generation_time, 2)
            ai_request.completed_at = timezone.now()
            ai_request.save()
            
            # Update usage stats
            update_ai_usage_stats(user, 'workout', True, ai_response.get('tokens_used', 0), generation_time)
            
            response_data = {
                'success': True,
                'request_id': ai_request.id,
                'content': ai_response['workout'],
                'tokens_used': ai_response.get('tokens_used', 0),
                'generation_time': round(generation_time, 2)
            }
        else:
            # Handle failure
            ai_request.status = 'failed'
            ai_request.error_message = ai_response['error']
            ai_request.save()
            
            update_ai_usage_stats(user, 'workout', False, 0, generation_time)
            
            response_data = {
                'success': False,
                'error_message': ai_response['error']
            }
            
    except Exception as e:
        # Handle unexpected errors
        ai_request.status = 'failed'
        ai_request.error_message = str(e)
        ai_request.save()
        
        update_ai_usage_stats(user, 'workout', False, 0, time.time() - start_time)
        
        response_data = {
            'success': False,
            'error_message': 'AI service temporarily unavailable'
        }
    
    serializer = AIGenerationResponseSerializer(response_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_nutrition_plan_view(request):
    """Generate AI-powered nutrition plan"""
    serializer = NutritionGenerationRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    preferences = serializer.validated_data
    start_time = time.time()
    
    # Build user profile for nutrition
    user_profile = {
        'age': user.get_age(),
        'gender': user.get_gender_display() if user.gender else 'Not specified',
        'weight': float(user.weight) if user.weight else None,
        'height': user.height,
        'activity_level': user.get_activity_level_display(),
        'fitness_goals': user.get_fitness_goals(),
        'dietary_restrictions': user.dietary_restrictions or 'None specified'
    }
    
    # Add request-specific preferences
    user_profile.update(preferences)
    
    # Create AI request record
    ai_request = AIContentRequest.objects.create(
        user=user,
        content_type='nutrition',
        status='processing',
        user_context=user_profile,
        prompt_context=preferences
    )
    
    try:
        # Use Claude to generate nutrition plan
        claude_client = ClaudeClient()
        goals = preferences.get('goals', user.get_fitness_goals())
        
        ai_response = claude_client.generate_nutrition_plan(user_profile, goals)
        generation_time = time.time() - start_time
        
        if ai_response['success']:
            # Update request record
            ai_request.status = 'completed'
            ai_request.generated_content = ai_response['nutrition_plan']
            ai_request.tokens_used = ai_response.get('tokens_used', 0)
            ai_request.generation_time_seconds = round(generation_time, 2)
            ai_request.completed_at = timezone.now()
            ai_request.save()
            
            # Create structured nutrition plan
            nutrition_plan = NutritionPlan.objects.create(
                user=user,
                ai_request=ai_request,
                name=f"AI Nutrition Plan - {timezone.now().strftime('%Y-%m-%d')}",
                description="Personalized nutrition plan generated by AI",
                meal_plan={},  # Would parse from AI response
                duration_days=preferences.get('plan_duration_days', 7)
            )
            
            # Update usage stats
            update_ai_usage_stats(user, 'nutrition', True, ai_response.get('tokens_used', 0), generation_time)
            
            response_data = {
                'success': True,
                'request_id': ai_request.id,
                'content': ai_response['nutrition_plan'],
                'structured_data': {
                    'nutrition_plan_id': nutrition_plan.id
                },
                'tokens_used': ai_response.get('tokens_used', 0),
                'generation_time': round(generation_time, 2)
            }
        else:
            # Handle failure
            ai_request.status = 'failed'
            ai_request.error_message = ai_response['error']
            ai_request.save()
            
            update_ai_usage_stats(user, 'nutrition', False, 0, generation_time)
            
            response_data = {
                'success': False,
                'error_message': ai_response['error']
            }
            
    except Exception as e:
        # Handle unexpected errors
        ai_request.status = 'failed'
        ai_request.error_message = str(e)
        ai_request.save()
        
        update_ai_usage_stats(user, 'nutrition', False, 0, time.time() - start_time)
        
        response_data = {
            'success': False,
            'error_message': 'AI service temporarily unavailable'
        }
    
    serializer = AIGenerationResponseSerializer(response_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_health_data_view(request):
    """Generate AI-powered health insights"""
    serializer = HealthAnalysisRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    preferences = serializer.validated_data
    start_time = time.time()
    
    # Gather user's health data
    medical_data = {}
    if preferences.get('include_medical_data', True):
        latest_medical = MedicalData.objects.filter(user=user).first()
        if latest_medical:
            medical_data = {
                'heart_rate': latest_medical.resting_heart_rate,
                'blood_pressure': f"{latest_medical.blood_pressure_systolic}/{latest_medical.blood_pressure_diastolic}" if latest_medical.blood_pressure_systolic else None,
                'sleep_quality': latest_medical.sleep_hours,
                'stress_level': latest_medical.stress_level,
                'energy_level': latest_medical.energy_level
            }
    
    # Create AI request record
    ai_request = AIContentRequest.objects.create(
        user=user,
        content_type='health_analysis',
        status='processing',
        user_context={'medical_data': medical_data},
        prompt_context=preferences
    )
    
    try:
        # Use Claude to analyze health data
        claude_client = ClaudeClient()
        
        ai_response = claude_client.analyze_medical_data(medical_data)
        generation_time = time.time() - start_time
        
        if ai_response['success']:
            # Update request record
            ai_request.status = 'completed'
            ai_request.generated_content = ai_response['analysis']
            ai_request.tokens_used = ai_response.get('tokens_used', 0)
            ai_request.generation_time_seconds = round(generation_time, 2)
            ai_request.completed_at = timezone.now()
            ai_request.save()
            
            # Create health insight
            health_insight = HealthInsight.objects.create(
                user=user,
                ai_request=ai_request,
                insight_type='general',
                priority='medium',
                title=f"Health Analysis - {timezone.now().strftime('%Y-%m-%d')}",
                content=ai_response['analysis'],
                data_sources=medical_data,
                confidence_score=0.85  # Would be calculated based on data quality
            )
            
            # Update usage stats
            update_ai_usage_stats(user, 'health_analysis', True, ai_response.get('tokens_used', 0), generation_time)
            
            response_data = {
                'success': True,
                'request_id': ai_request.id,
                'content': ai_response['analysis'],
                'structured_data': {
                    'insight_id': health_insight.id
                },
                'tokens_used': ai_response.get('tokens_used', 0),
                'generation_time': round(generation_time, 2)
            }
        else:
            # Handle failure
            ai_request.status = 'failed'
            ai_request.error_message = ai_response['error']
            ai_request.save()
            
            update_ai_usage_stats(user, 'health_analysis', False, 0, generation_time)
            
            response_data = {
                'success': False,
                'error_message': ai_response['error']
            }
            
    except Exception as e:
        # Handle unexpected errors
        ai_request.status = 'failed'
        ai_request.error_message = str(e)
        ai_request.save()
        
        update_ai_usage_stats(user, 'health_analysis', False, 0, time.time() - start_time)
        
        response_data = {
            'success': False,
            'error_message': 'AI service temporarily unavailable'
        }
    
    serializer = AIGenerationResponseSerializer(response_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_feedback_view(request, request_id):
    """Submit feedback for AI-generated content"""
    try:
        ai_request = AIContentRequest.objects.get(id=request_id, user=request.user)
    except AIContentRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = FeedbackSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Update the AI request with feedback
    ai_request.user_rating = serializer.validated_data['rating']
    ai_request.user_feedback = serializer.validated_data.get('feedback', '')
    ai_request.save()
    
    return Response({
        'message': 'Feedback submitted successfully',
        'rating': ai_request.user_rating
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_usage_stats_view(request):
    """Get user's AI usage statistics"""
    user = request.user
    days = int(request.query_params.get('days', 30))
    
    start_date = timezone.now().date() - timedelta(days=days)
    stats = AIUsageStats.objects.filter(
        user=user,
        date__gte=start_date
    ).aggregate(
        total_requests=Count('total_requests'),
        successful_requests=Count('successful_requests'),
        total_tokens=Count('total_tokens_used'),
        avg_rating=Avg('avg_user_rating')
    )
    
    # Get recent requests breakdown
    recent_requests = AIContentRequest.objects.filter(
        user=user,
        created_at__gte=start_date
    ).values('content_type', 'status').annotate(
        count=Count('id')
    )
    
    return Response({
        'period_days': days,
        'total_requests': stats['total_requests'] or 0,
        'successful_requests': stats['successful_requests'] or 0,
        'total_tokens_used': stats['total_tokens'] or 0,
        'average_rating': round(stats['avg_rating'] or 0, 2),
        'requests_breakdown': list(recent_requests)
    })


def update_ai_usage_stats(user, request_type, success, tokens_used, response_time):
    """Update daily AI usage statistics"""
    today = timezone.now().date()
    stats, created = AIUsageStats.objects.get_or_create(
        user=user,
        date=today,
        defaults={
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens_used': 0,
            'workout_requests': 0,
            'nutrition_requests': 0,
            'health_analysis_requests': 0,
        }
    )
    
    # Update counters
    stats.total_requests += 1
    if success:
        stats.successful_requests += 1
    else:
        stats.failed_requests += 1
    
    stats.total_tokens_used += tokens_used
    
    # Update request type counters
    if request_type == 'workout':
        stats.workout_requests += 1
    elif request_type == 'nutrition':
        stats.nutrition_requests += 1
    elif request_type == 'health_analysis':
        stats.health_analysis_requests += 1
    
    # Update average response time
    if stats.avg_response_time:
        stats.avg_response_time = (stats.avg_response_time + response_time) / 2
    else:
        stats.avg_response_time = response_time
    
    stats.save()
