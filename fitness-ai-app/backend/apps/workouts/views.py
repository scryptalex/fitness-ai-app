from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Exercise, WorkoutTemplate, Workout, WorkoutSession, 
    WorkoutPlan, WorkoutPlanWorkout
)
from .serializers import (
    ExerciseSerializer, WorkoutTemplateSerializer, WorkoutTemplateCreateSerializer,
    WorkoutSerializer, WorkoutCreateSerializer, WorkoutSessionSerializer,
    WorkoutPlanSerializer, WorkoutStatsSerializer, AIWorkoutRequestSerializer,
    TodayWorkoutSerializer
)
from core.ai_integrations.claude_client import ClaudeClient


class ExerciseListView(generics.ListAPIView):
    queryset = Exercise.objects.filter(is_active=True)
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        muscle_group = self.request.query_params.get('muscle_group')
        equipment = self.request.query_params.get('equipment')
        difficulty = self.request.query_params.get('difficulty')
        
        if muscle_group:
            queryset = queryset.filter(muscle_groups=muscle_group)
        if equipment:
            queryset = queryset.filter(equipment_required=equipment)
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
            
        return queryset


class WorkoutTemplateListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkoutTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = WorkoutTemplate.objects.filter(
            Q(is_public=True) | Q(created_by=self.request.user)
        )
        
        workout_type = self.request.query_params.get('type')
        difficulty = self.request.query_params.get('difficulty')
        duration = self.request.query_params.get('max_duration')
        
        if workout_type:
            queryset = queryset.filter(workout_type=workout_type)
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        if duration:
            queryset = queryset.filter(estimated_duration__lte=int(duration))
            
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkoutTemplateCreateSerializer
        return WorkoutTemplateSerializer


class WorkoutTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkoutTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutTemplate.objects.filter(
            Q(is_public=True) | Q(created_by=self.request.user)
        )


class WorkoutListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Workout.objects.filter(user=self.request.user)
        
        status_filter = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if date_from:
            queryset = queryset.filter(scheduled_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(scheduled_date__lte=date_to)
            
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkoutCreateSerializer
        return WorkoutSerializer


class WorkoutDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)


class WorkoutSessionListView(generics.ListAPIView):
    serializer_class = WorkoutSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        workout_id = self.kwargs['workout_id']
        return WorkoutSession.objects.filter(
            workout_id=workout_id,
            workout__user=self.request.user
        )


class WorkoutSessionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = WorkoutSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutSession.objects.filter(workout__user=self.request.user)


class WorkoutPlanListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkoutPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutPlan.objects.filter(user=self.request.user)


class WorkoutPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkoutPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutPlan.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def today_workout_view(request):
    """Get today's scheduled workout or suggestions"""
    user = request.user
    today = timezone.now().date()
    
    # Check for scheduled workout today
    today_workout = Workout.objects.filter(
        user=user,
        scheduled_date__date=today
    ).first()
    
    if today_workout:
        workout_serializer = WorkoutSerializer(today_workout)
        data = {
            'has_workout': True,
            'workout': workout_serializer.data,
            'motivational_message': f"Ready for your {today_workout.name}? Let's crush it!"
        }
    else:
        # Provide suggestions based on user's history and preferences
        suggestions = []
        
        # Get user's favorite workout types
        favorite_types = Workout.objects.filter(
            user=user,
            status='completed'
        ).values('template__workout_type').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        for fav_type in favorite_types:
            if fav_type['template__workout_type']:
                templates = WorkoutTemplate.objects.filter(
                    workout_type=fav_type['template__workout_type'],
                    is_public=True
                )[:2]
                
                for template in templates:
                    suggestions.append({
                        'id': template.id,
                        'name': template.name,
                        'type': template.workout_type,
                        'duration': template.estimated_duration,
                        'difficulty': template.difficulty_level
                    })
        
        # If no favorites, suggest popular beginner workouts
        if not suggestions:
            popular_templates = WorkoutTemplate.objects.filter(
                is_public=True,
                difficulty_level='beginner'
            )[:5]
            
            for template in popular_templates:
                suggestions.append({
                    'id': template.id,
                    'name': template.name,
                    'type': template.workout_type,
                    'duration': template.estimated_duration,
                    'difficulty': template.difficulty_level
                })
        
        data = {
            'has_workout': False,
            'workout': None,
            'suggestions': suggestions[:5],
            'motivational_message': "No workout scheduled for today. How about starting with one of these?"
        }
    
    serializer = TodayWorkoutSerializer(data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_workout_view(request, workout_id):
    """Start a workout session"""
    try:
        workout = Workout.objects.get(id=workout_id, user=request.user)
    except Workout.DoesNotExist:
        return Response({'error': 'Workout not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if workout.status == 'in_progress':
        return Response({'error': 'Workout already in progress'}, status=status.HTTP_400_BAD_REQUEST)
    
    workout.status = 'in_progress'
    workout.started_at = timezone.now()
    workout.save()
    
    return Response({
        'message': 'Workout started successfully',
        'started_at': workout.started_at
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_workout_view(request, workout_id):
    """Complete a workout session"""
    try:
        workout = Workout.objects.get(id=workout_id, user=request.user)
    except Workout.DoesNotExist:
        return Response({'error': 'Workout not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if workout.status != 'in_progress':
        return Response({'error': 'Workout is not in progress'}, status=status.HTTP_400_BAD_REQUEST)
    
    workout.status = 'completed'
    workout.completed_at = timezone.now()
    
    # Update user's workout streak and last workout date
    user = request.user
    user.last_workout_date = workout.completed_at
    
    # Calculate streak
    yesterday = timezone.now().date() - timedelta(days=1)
    last_completed = Workout.objects.filter(
        user=user,
        status='completed',
        completed_at__date=yesterday
    ).exists()
    
    if last_completed:
        user.workout_streak += 1
    else:
        user.workout_streak = 1
    
    user.save()
    workout.save()
    
    return Response({
        'message': 'Workout completed successfully',
        'completed_at': workout.completed_at,
        'duration_minutes': workout.duration_minutes,
        'current_streak': user.workout_streak
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def workout_stats_view(request):
    """Get user's workout statistics"""
    user = request.user
    now = timezone.now()
    week_start = now - timedelta(days=now.weekday())
    month_start = now.replace(day=1)
    
    # Calculate various stats
    total_workouts = Workout.objects.filter(user=user, status='completed').count()
    workouts_this_week = Workout.objects.filter(
        user=user,
        status='completed',
        completed_at__gte=week_start
    ).count()
    workouts_this_month = Workout.objects.filter(
        user=user,
        status='completed',
        completed_at__gte=month_start
    ).count()
    
    # Calories and duration stats
    completed_workouts = Workout.objects.filter(user=user, status='completed')
    total_calories = sum([w.calories_burned or 0 for w in completed_workouts])
    
    durations = [w.duration_minutes for w in completed_workouts if w.duration_minutes]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Favorite workout type
    favorite_type = Workout.objects.filter(
        user=user,
        status='completed',
        template__isnull=False
    ).values('template__workout_type').annotate(
        count=Count('id')
    ).order_by('-count').first()
    
    favorite_workout_type = favorite_type['template__workout_type'] if favorite_type else 'Mixed'
    
    # Completion rate
    total_scheduled = Workout.objects.filter(user=user).count()
    completion_rate = (total_workouts / total_scheduled * 100) if total_scheduled > 0 else 0
    
    stats = {
        'total_workouts': total_workouts,
        'workouts_this_week': workouts_this_week,
        'workouts_this_month': workouts_this_month,
        'total_calories_burned': total_calories,
        'avg_workout_duration': round(avg_duration, 1),
        'favorite_workout_type': favorite_workout_type,
        'current_streak': user.workout_streak,
        'longest_streak': user.workout_streak,  # TODO: Track separately
        'completion_rate': round(completion_rate, 1)
    }
    
    serializer = WorkoutStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_ai_workout_view(request):
    """Generate a personalized workout using AI"""
    serializer = AIWorkoutRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    preferences = serializer.validated_data
    
    # Build user profile for AI
    user_profile = {
        'age': user.get_age(),
        'gender': user.get_gender_display() if user.gender else 'Not specified',
        'fitness_level': user.get_fitness_level_display(),
        'goals': user.get_fitness_goals(),
        'workout_duration': preferences.get('duration_minutes', user.preferred_workout_duration),
        'equipment': preferences.get('equipment_available', user.get_available_equipment()),
        'activity_level': user.get_activity_level_display()
    }
    
    # Use Claude to generate workout
    claude_client = ClaudeClient()
    workout_type = preferences.get('workout_type', 'general')
    
    try:
        ai_response = claude_client.generate_workout(user_profile, workout_type)
        
        if ai_response['success']:
            # Create a custom workout from AI response
            workout_name = f"AI Generated {workout_type.title()} Workout"
            
            workout = Workout.objects.create(
                user=user,
                name=workout_name,
                scheduled_date=timezone.now(),
                ai_prompt_context=str(preferences)
            )
            
            return Response({
                'success': True,
                'workout_id': workout.id,
                'workout_content': ai_response['workout'],
                'tokens_used': ai_response.get('tokens_used', 0),
                'message': 'Workout generated successfully!'
            })
        else:
            return Response({
                'success': False,
                'error': ai_response['error'],
                'message': 'Failed to generate workout. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'AI service unavailable. Please try again later.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def workout_history_view(request):
    """Get user's workout history with analytics"""
    user = request.user
    days = int(request.query_params.get('days', 30))
    
    start_date = timezone.now() - timedelta(days=days)
    workouts = Workout.objects.filter(
        user=user,
        completed_at__gte=start_date,
        status='completed'
    ).order_by('-completed_at')
    
    serializer = WorkoutSerializer(workouts, many=True)
    
    # Calculate summary stats for the period
    total_workouts = workouts.count()
    total_time = sum([w.duration_minutes or 0 for w in workouts])
    total_calories = sum([w.calories_burned or 0 for w in workouts])
    
    return Response({
        'workouts': serializer.data,
        'summary': {
            'total_workouts': total_workouts,
            'total_time_minutes': total_time,
            'total_calories_burned': total_calories,
            'avg_workouts_per_week': round((total_workouts / days) * 7, 1),
            'period_days': days
        }
    })
