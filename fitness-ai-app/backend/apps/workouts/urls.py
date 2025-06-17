from django.urls import path
from . import views

urlpatterns = [
    # Exercises
    path('exercises/', views.ExerciseListView.as_view(), name='exercise-list'),
    
    # Workout Templates
    path('templates/', views.WorkoutTemplateListCreateView.as_view(), name='workout-template-list'),
    path('templates/<int:pk>/', views.WorkoutTemplateDetailView.as_view(), name='workout-template-detail'),
    
    # Workouts
    path('', views.WorkoutListCreateView.as_view(), name='workout-list'),
    path('<int:pk>/', views.WorkoutDetailView.as_view(), name='workout-detail'),
    path('<int:workout_id>/start/', views.start_workout_view, name='workout-start'),
    path('<int:workout_id>/complete/', views.complete_workout_view, name='workout-complete'),
    
    # Workout Sessions
    path('<int:workout_id>/sessions/', views.WorkoutSessionListView.as_view(), name='workout-session-list'),
    path('sessions/<int:pk>/', views.WorkoutSessionDetailView.as_view(), name='workout-session-detail'),
    
    # Workout Plans
    path('plans/', views.WorkoutPlanListCreateView.as_view(), name='workout-plan-list'),
    path('plans/<int:pk>/', views.WorkoutPlanDetailView.as_view(), name='workout-plan-detail'),
    
    # Analytics and AI
    path('today/', views.today_workout_view, name='today-workout'),
    path('stats/', views.workout_stats_view, name='workout-stats'),
    path('history/', views.workout_history_view, name='workout-history'),
    path('generate/', views.generate_ai_workout_view, name='generate-ai-workout'),
]