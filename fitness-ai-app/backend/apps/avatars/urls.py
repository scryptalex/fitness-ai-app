from django.urls import path
from . import views

urlpatterns = [
    # Available avatars
    path('', views.AvatarListView.as_view(), name='avatar-list'),
    path('<int:pk>/', views.AvatarDetailView.as_view(), name='avatar-detail'),
    
    # User's avatars for each day
    path('user/', views.UserAvatarListView.as_view(), name='user-avatar-list'),
    path('user/<int:day_of_week>/', views.UserAvatarDetailView.as_view(), name='user-avatar-detail'),
    path('user/current/', views.current_avatar_view, name='current-avatar'),
    
    # Avatar interactions
    path('interactions/', views.AvatarInteractionListView.as_view(), name='avatar-interaction-list'),
    path('interact/', views.create_interaction_view, name='create-interaction'),
    
    # Avatar presets
    path('presets/', views.AvatarPresetListView.as_view(), name='avatar-preset-list'),
]