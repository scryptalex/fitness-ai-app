from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.db.models import Count, Avg
from datetime import datetime, timedelta
from .models import User, UserProfile, MedicalData, WorkoutGoal
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserProfileDetailSerializer, MedicalDataSerializer, WorkoutGoalSerializer,
    UserStatsSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user_id': user.id,
            'email': user.email,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    login(request, user)
    
    # Get or create auth token
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'user_id': user.id,
        'email': user.email,
        'token': token.key,
        'message': 'Login successful'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        # Delete the token
        token = Token.objects.get(user=request.user)
        token.delete()
    except Token.DoesNotExist:
        pass
    
    logout(request)
    return Response({'message': 'Logout successful'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class MedicalDataListCreateView(generics.ListCreateAPIView):
    serializer_class = MedicalDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MedicalData.objects.filter(user=self.request.user)


class MedicalDataDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MedicalDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MedicalData.objects.filter(user=self.request.user)


class WorkoutGoalListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkoutGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkoutGoal.objects.filter(user=self.request.user, is_active=True)


class WorkoutGoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkoutGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkoutGoal.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats_view(request):
    user = request.user
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())
    month_start = now.replace(day=1)
    
    # Calculate stats (placeholder values for now since workout models aren't created yet)
    stats = {
        'workouts_this_week': 0,  # Will be calculated when workout models exist
        'workouts_this_month': 0,
        'calories_burned_week': 0,
        'calories_burned_month': 0,
        'current_streak': user.workout_streak,
        'longest_streak': user.workout_streak,  # Will need separate tracking
        'total_workouts': 0,
        'avg_workout_duration': user.preferred_workout_duration,
        'favorite_workout_type': 'General Fitness'
    }
    
    serializer = UserStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_view(request):
    """Get dashboard data for the user"""
    user = request.user
    
    # Get user profile
    profile_serializer = UserProfileSerializer(user)
    
    # Get latest medical data
    latest_medical = MedicalData.objects.filter(user=user).first()
    medical_serializer = MedicalDataSerializer(latest_medical) if latest_medical else None
    
    # Get active goals
    goals = WorkoutGoal.objects.filter(user=user, is_active=True)
    goals_serializer = WorkoutGoalSerializer(goals, many=True)
    
    return Response({
        'profile': profile_serializer.data,
        'medical_data': medical_serializer.data if medical_serializer else None,
        'goals': goals_serializer.data,
        'recommendations': [
            "Stay hydrated during workouts",
            "Get 7-9 hours of sleep for optimal recovery",
            "Consider adding more protein to your diet"
        ]
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_fitness_goals_view(request):
    """Update user's fitness goals"""
    goals = request.data.get('goals', [])
    user = request.user
    user.set_fitness_goals(goals)
    user.save()
    
    return Response({
        'message': 'Fitness goals updated successfully',
        'goals': user.get_fitness_goals()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def health_insights_view(request):
    """Get AI-powered health insights based on user data"""
    user = request.user
    latest_medical = MedicalData.objects.filter(user=user).first()
    
    if not latest_medical:
        return Response({
            'insights': [],
            'message': 'No medical data available for insights'
        })
    
    # Basic insights based on data
    insights = []
    
    if latest_medical.stress_level and latest_medical.stress_level > 7:
        insights.append("Your stress levels are high. Consider meditation or yoga.")
    
    if latest_medical.sleep_hours and latest_medical.sleep_hours < 7:
        insights.append("You may need more sleep for optimal recovery.")
    
    if latest_medical.energy_level and latest_medical.energy_level < 5:
        insights.append("Low energy levels detected. Consider adjusting your nutrition.")
    
    if user.get_bmi():
        bmi = user.get_bmi()
        if bmi < 18.5:
            insights.append("Your BMI indicates you may be underweight.")
        elif bmi > 25:
            insights.append("Your BMI indicates you may be overweight.")
    
    return Response({
        'insights': insights,
        'last_updated': latest_medical.recorded_at if latest_medical else None
    })
