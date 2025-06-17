from django.urls import path
from . import views

urlpatterns = [
    # AI Content Requests
    path('requests/', views.AIContentRequestListView.as_view(), name='ai-request-list'),
    path('requests/<int:request_id>/feedback/', views.submit_feedback_view, name='ai-request-feedback'),
    
    # AI Generation Endpoints
    path('generate/workout/', views.generate_workout_view, name='generate-workout'),
    path('generate/nutrition/', views.generate_nutrition_plan_view, name='generate-nutrition'),
    path('analyze/health/', views.analyze_health_data_view, name='analyze-health'),
    
    # Nutrition Plans
    path('nutrition/', views.NutritionPlanListCreateView.as_view(), name='nutrition-plan-list'),
    path('nutrition/<int:pk>/', views.NutritionPlanDetailView.as_view(), name='nutrition-plan-detail'),
    
    # Health Insights
    path('insights/', views.HealthInsightListView.as_view(), name='health-insight-list'),
    path('insights/<int:pk>/', views.HealthInsightDetailView.as_view(), name='health-insight-detail'),
    
    # Usage Statistics
    path('usage-stats/', views.ai_usage_stats_view, name='ai-usage-stats'),
]