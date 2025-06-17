from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class AIContentRequest(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('workout', 'Workout Plan'),
        ('nutrition', 'Nutrition Plan'),
        ('health_analysis', 'Health Analysis'),
        ('exercise_instructions', 'Exercise Instructions'),
        ('motivation', 'Motivational Content'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_requests')
    content_type = models.CharField(max_length=30, choices=CONTENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Request context
    user_context = models.JSONField(help_text="User profile data used for generation")
    prompt_context = models.JSONField(help_text="Specific request parameters")
    
    # Response data
    generated_content = models.TextField(blank=True)
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    generation_time_seconds = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Quality metrics
    user_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    user_feedback = models.TextField(blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ai_content_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.get_content_type_display()} ({self.status})"


class NutritionPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='nutrition_plans')
    ai_request = models.OneToOneField(AIContentRequest, on_delete=models.SET_NULL, null=True, blank=True)
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Plan details
    daily_calories = models.PositiveIntegerField(null=True, blank=True)
    protein_grams = models.PositiveIntegerField(null=True, blank=True)
    carbs_grams = models.PositiveIntegerField(null=True, blank=True)
    fats_grams = models.PositiveIntegerField(null=True, blank=True)
    
    # Plan content
    meal_plan = models.JSONField(help_text="Structured meal plan data")
    shopping_list = models.JSONField(blank=True, default=list)
    preparation_tips = models.TextField(blank=True)
    
    # Metadata
    duration_days = models.PositiveIntegerField(default=7)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nutrition_plans'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.name}"


class HealthInsight(models.Model):
    INSIGHT_TYPE_CHOICES = [
        ('general', 'General Health'),
        ('fitness', 'Fitness Related'),
        ('nutrition', 'Nutrition Related'),
        ('sleep', 'Sleep Related'),
        ('stress', 'Stress Related'),
        ('recovery', 'Recovery Related'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='health_insights')
    ai_request = models.ForeignKey(AIContentRequest, on_delete=models.SET_NULL, null=True, blank=True)
    
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    recommendations = models.JSONField(default=list)
    
    # Context data
    data_sources = models.JSONField(help_text="Medical/fitness data used for insight")
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    # User interaction
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    user_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'health_insights'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class AIUsageStats(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_usage_stats')
    
    # Daily stats
    date = models.DateField()
    total_requests = models.PositiveIntegerField(default=0)
    successful_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)
    total_tokens_used = models.PositiveIntegerField(default=0)
    
    # Request type breakdown
    workout_requests = models.PositiveIntegerField(default=0)
    nutrition_requests = models.PositiveIntegerField(default=0)
    health_analysis_requests = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    avg_response_time = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    avg_user_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_usage_stats'
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.date}"


class ContentTemplate(models.Model):
    TEMPLATE_TYPE_CHOICES = [
        ('workout_prompt', 'Workout Generation Prompt'),
        ('nutrition_prompt', 'Nutrition Plan Prompt'),
        ('health_prompt', 'Health Analysis Prompt'),
        ('motivation_prompt', 'Motivational Content Prompt'),
    ]

    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPE_CHOICES)
    prompt_template = models.TextField()
    
    # Template parameters
    required_parameters = models.JSONField(default=list)
    optional_parameters = models.JSONField(default=list)
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content_templates'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
