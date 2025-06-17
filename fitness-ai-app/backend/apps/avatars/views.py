from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from .models import Avatar, UserAvatar, AvatarInteraction, AvatarPreset


class AvatarListView(generics.ListAPIView):
    queryset = Avatar.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        avatars = self.get_queryset()
        data = []
        for avatar in avatars:
            data.append({
                'id': avatar.id,
                'name': avatar.name,
                'description': avatar.description,
                'gender': avatar.gender,
                'body_type': avatar.body_type,
                'vrm_file_url': avatar.vrm_file_url,
                'preview_image_url': avatar.preview_image_url,
                'is_premium': avatar.is_premium,
                'customization_options': {
                    'skin_tones': avatar.skin_tones,
                    'hair_colors': avatar.hair_colors,
                    'outfit_options': avatar.outfit_options
                }
            })
        return Response(data)


class AvatarDetailView(generics.RetrieveAPIView):
    queryset = Avatar.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]


class UserAvatarListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserAvatar.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        user_avatars = self.get_queryset()
        data = []
        for user_avatar in user_avatars:
            data.append({
                'day_of_week': user_avatar.day_of_week,
                'day_name': user_avatar.get_day_of_week_display(),
                'avatar': {
                    'id': user_avatar.avatar.id,
                    'name': user_avatar.avatar.name,
                    'vrm_file_url': user_avatar.avatar.vrm_file_url,
                    'preview_image_url': user_avatar.avatar.preview_image_url
                },
                'customizations': {
                    'skin_tone': user_avatar.skin_tone,
                    'hair_color': user_avatar.hair_color,
                    'outfit_config': user_avatar.outfit_config
                },
                'name': user_avatar.name,
                'motivation_message': user_avatar.motivation_message,
                'is_active': user_avatar.is_active,
                'last_interacted': user_avatar.last_interacted
            })
        return Response(data)


class UserAvatarDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        day_of_week = self.kwargs['day_of_week']
        try:
            return UserAvatar.objects.get(user=self.request.user, day_of_week=day_of_week)
        except UserAvatar.DoesNotExist:
            return None


class AvatarInteractionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AvatarInteraction.objects.filter(
            user_avatar__user=self.request.user
        ).select_related('user_avatar')


class AvatarPresetListView(generics.ListAPIView):
    queryset = AvatarPreset.objects.filter(is_featured=True)
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_avatar_view(request):
    """Get current day's avatar"""
    today = datetime.now().weekday() + 1  # Monday = 1
    
    try:
        user_avatar = UserAvatar.objects.get(
            user=request.user,
            day_of_week=today,
            is_active=True
        )
        
        # Update last interacted
        user_avatar.last_interacted = timezone.now()
        user_avatar.save()
        
        data = {
            'day_of_week': user_avatar.day_of_week,
            'day_name': user_avatar.get_day_of_week_display(),
            'avatar': {
                'id': user_avatar.avatar.id,
                'name': user_avatar.avatar.name,
                'vrm_file_url': user_avatar.avatar.vrm_file_url,
                'preview_image_url': user_avatar.avatar.preview_image_url
            },
            'customizations': {
                'skin_tone': user_avatar.skin_tone,
                'hair_color': user_avatar.hair_color,
                'outfit_config': user_avatar.outfit_config
            },
            'name': user_avatar.name or f"Your {user_avatar.get_day_of_week_display()} Avatar",
            'motivation_message': user_avatar.motivation_message or "Ready to crush today's workout!",
            'recent_interactions': []
        }
        
        # Get recent interactions
        recent_interactions = AvatarInteraction.objects.filter(
            user_avatar=user_avatar,
            is_read=False
        )[:3]
        
        for interaction in recent_interactions:
            data['recent_interactions'].append({
                'id': interaction.id,
                'type': interaction.interaction_type,
                'message': interaction.message,
                'animation_trigger': interaction.animation_trigger,
                'created_at': interaction.created_at
            })
        
        return Response(data)
        
    except UserAvatar.DoesNotExist:
        return Response({
            'error': 'No avatar configured for today',
            'day_of_week': today,
            'day_name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][today-1],
            'suggestion': 'Please configure your weekly avatars in the avatar section'
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_interaction_view(request):
    """Create an avatar interaction"""
    interaction_type = request.data.get('interaction_type')
    message = request.data.get('message')
    day_of_week = request.data.get('day_of_week', datetime.now().weekday() + 1)
    
    try:
        user_avatar = UserAvatar.objects.get(
            user=request.user,
            day_of_week=day_of_week
        )
        
        interaction = AvatarInteraction.objects.create(
            user_avatar=user_avatar,
            interaction_type=interaction_type,
            message=message,
            context_data=request.data.get('context_data', {})
        )
        
        return Response({
            'id': interaction.id,
            'message': interaction.message,
            'type': interaction.interaction_type,
            'created_at': interaction.created_at
        })
        
    except UserAvatar.DoesNotExist:
        return Response({
            'error': 'Avatar not found for specified day'
        }, status=404)
