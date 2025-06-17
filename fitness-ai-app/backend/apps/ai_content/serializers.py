from rest_framework import serializers
from .models import (
    AIContentRequest, NutritionPlan, HealthInsight, 
    AIUsageStats, ContentTemplate
)


class AIContentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIContentRequest
        fields = [
            'id', 'content_type', 'status', 'user_context', 'prompt_context',
            'generated_content', 'tokens_used', 'generation_time_seconds',
            'user_rating', 'user_feedback', 'error_message', 'retry_count',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'generated_content', 'tokens_used', 'generation_time_seconds',
            'error_message', 'retry_count', 'created_at', 'updated_at', 'completed_at'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NutritionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionPlan
        fields = [
            'id', 'name', 'description', 'daily_calories', 'protein_grams',
            'carbs_grams', 'fats_grams', 'meal_plan', 'shopping_list',
            'preparation_tips', 'duration_days', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class HealthInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthInsight
        fields = [
            'id', 'insight_type', 'priority', 'title', 'content',
            'recommendations', 'data_sources', 'confidence_score',
            'is_read', 'is_dismissed', 'user_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AIUsageStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIUsageStats
        fields = [
            'date', 'total_requests', 'successful_requests', 'failed_requests',
            'total_tokens_used', 'workout_requests', 'nutrition_requests',
            'health_analysis_requests', 'avg_response_time', 'avg_user_rating'
        ]


class ContentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentTemplate
        fields = [
            'id', 'name', 'template_type', 'prompt_template',
            'required_parameters', 'optional_parameters', 'usage_count',
            'success_rate', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'success_rate', 'created_at', 'updated_at']


class WorkoutGenerationRequestSerializer(serializers.Serializer):
    workout_type = serializers.ChoiceField(
        choices=['strength', 'cardio', 'hiit', 'yoga', 'pilates', 'mixed'],
        required=False
    )
    duration_minutes = serializers.IntegerField(min_value=10, max_value=120, required=False)
    difficulty_level = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced'],
        required=False
    )
    equipment_available = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    target_muscle_groups = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    specific_goals = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    exclude_exercises = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    custom_requirements = serializers.CharField(required=False)


class NutritionGenerationRequestSerializer(serializers.Serializer):
    goals = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    dietary_restrictions = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    allergies = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    preferred_foods = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    disliked_foods = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    meal_count = serializers.IntegerField(min_value=3, max_value=6, default=3)
    plan_duration_days = serializers.IntegerField(min_value=1, max_value=30, default=7)
    budget_level = serializers.ChoiceField(
        choices=['low', 'medium', 'high'],
        required=False
    )
    cooking_time = serializers.ChoiceField(
        choices=['minimal', 'moderate', 'extensive'],
        required=False
    )


class HealthAnalysisRequestSerializer(serializers.Serializer):
    include_medical_data = serializers.BooleanField(default=True)
    include_workout_data = serializers.BooleanField(default=True)
    include_nutrition_data = serializers.BooleanField(default=False)
    focus_areas = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    specific_concerns = serializers.CharField(required=False)


class AIGenerationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    request_id = serializers.IntegerField(required=False)
    content = serializers.CharField(required=False)
    structured_data = serializers.DictField(required=False)
    tokens_used = serializers.IntegerField(required=False)
    generation_time = serializers.FloatField(required=False)
    error_message = serializers.CharField(required=False)
    recommendations = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class FeedbackSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(required=False, allow_blank=True)
    helpful = serializers.BooleanField(required=False)
    accurate = serializers.BooleanField(required=False)
    would_use_again = serializers.BooleanField(required=False)