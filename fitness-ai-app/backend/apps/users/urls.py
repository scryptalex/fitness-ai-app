from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.login_view, name='user-login'),
    path('logout/', views.logout_view, name='user-logout'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/details/', views.UserProfileDetailView.as_view(), name='user-profile-details'),
    path('dashboard/', views.user_dashboard_view, name='user-dashboard'),
    path('stats/', views.user_stats_view, name='user-stats'),
    
    # Goals and Health
    path('goals/', views.WorkoutGoalListCreateView.as_view(), name='workout-goals'),
    path('goals/<int:pk>/', views.WorkoutGoalDetailView.as_view(), name='workout-goal-detail'),
    path('fitness-goals/', views.update_fitness_goals_view, name='update-fitness-goals'),
    
    # Medical Data
    path('medical/', views.MedicalDataListCreateView.as_view(), name='medical-data'),
    path('medical/<int:pk>/', views.MedicalDataDetailView.as_view(), name='medical-data-detail'),
    path('health-insights/', views.health_insights_view, name='health-insights'),
]