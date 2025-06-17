from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Avatar(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Non-binary'),
    ]
    
    BODY_TYPE_CHOICES = [
        ('slim', 'Slim'),
        ('athletic', 'Athletic'),
        ('muscular', 'Muscular'),
        ('curvy', 'Curvy'),
        ('plus_size', 'Plus Size'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    body_type = models.CharField(max_length=20, choices=BODY_TYPE_CHOICES)
    
    # VRM Model Data
    vrm_file_url = models.URLField()
    preview_image_url = models.URLField(blank=True)
    
    # Customization options
    skin_tones = models.JSONField(default=list, help_text="Available skin tone hex codes")
    hair_colors = models.JSONField(default=list, help_text="Available hair color hex codes")
    outfit_options = models.JSONField(default=list, help_text="Available outfit configurations")
    
    # Metadata
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'avatars'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"


class UserAvatar(models.Model):
    DAY_CHOICES = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_avatars')
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE)
    day_of_week = models.PositiveIntegerField(choices=DAY_CHOICES)
    
    # Customizations
    skin_tone = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    hair_color = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    outfit_config = models.JSONField(default=dict, help_text="Selected outfit configuration")
    
    # Personalization
    name = models.CharField(max_length=100, blank=True)
    motivation_message = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_interacted = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_avatars'
        unique_together = ['user', 'day_of_week']
        ordering = ['day_of_week']

    def __str__(self):
        return f"{self.user.email} - {self.get_day_of_week_display()}"


class AvatarInteraction(models.Model):
    INTERACTION_TYPE_CHOICES = [
        ('workout_start', 'Workout Started'),
        ('workout_complete', 'Workout Completed'),
        ('goal_achieved', 'Goal Achieved'),
        ('streak_milestone', 'Streak Milestone'),
        ('custom_message', 'Custom Message'),
        ('encouragement', 'Encouragement'),
    ]

    user_avatar = models.ForeignKey(UserAvatar, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=30, choices=INTERACTION_TYPE_CHOICES)
    
    # Message content
    message = models.TextField()
    animation_trigger = models.CharField(max_length=50, blank=True)
    
    # Context
    context_data = models.JSONField(default=dict, help_text="Additional data for the interaction")
    
    # Tracking
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'avatar_interactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_avatar} - {self.get_interaction_type_display()}"


class AvatarPreset(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE)
    
    # Preset configuration
    skin_tone = models.CharField(max_length=7)
    hair_color = models.CharField(max_length=7)
    outfit_config = models.JSONField()
    
    # Metadata
    is_featured = models.BooleanField(default=False)
    usage_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'avatar_presets'
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return f"{self.name} ({self.avatar.name})"
