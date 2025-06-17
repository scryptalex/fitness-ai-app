from rest_framework import serializers
from .models import (
    Exercise, WorkoutTemplate, WorkoutExercise, Workout, 
    WorkoutSession, WorkoutPlan, WorkoutPlanWorkout
)


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            'id', 'name', 'description', 'instructions', 'muscle_groups',
            'equipment_required', 'difficulty_level', 'calories_per_minute',
            'image_url', 'video_url', 'is_active'
        ]


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = WorkoutExercise
        fields = [
            'id', 'exercise', 'exercise_id', 'order', 'sets', 'reps', 
            'duration_seconds', 'rest_seconds', 'weight_kg', 'notes'
        ]


class WorkoutTemplateSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(many=True, read_only=True)
    equipment_list = serializers.ListField(source='get_equipment_list', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = WorkoutTemplate
        fields = [
            'id', 'name', 'description', 'workout_type', 'difficulty_level',
            'estimated_duration', 'intensity_level', 'equipment_needed',
            'equipment_list', 'space_required', 'is_public', 'is_ai_generated',
            'created_by_name', 'exercises', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class WorkoutTemplateCreateSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(many=True, write_only=True)

    class Meta:
        model = WorkoutTemplate
        fields = [
            'name', 'description', 'workout_type', 'difficulty_level',
            'estimated_duration', 'intensity_level', 'equipment_needed',
            'space_required', 'is_public', 'exercises'
        ]

    def create(self, validated_data):
        exercises_data = validated_data.pop('exercises', [])
        validated_data['created_by'] = self.context['request'].user
        
        template = WorkoutTemplate.objects.create(**validated_data)
        
        for exercise_data in exercises_data:
            WorkoutExercise.objects.create(workout_template=template, **exercise_data)
        
        return template


class WorkoutSessionSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    reps_list = serializers.ListField(source='get_reps_list', read_only=True)
    weight_list = serializers.ListField(source='get_weight_list', read_only=True)

    class Meta:
        model = WorkoutSession
        fields = [
            'id', 'exercise', 'order', 'planned_sets', 'completed_sets',
            'reps_completed', 'reps_list', 'weight_used', 'weight_list',
            'duration_seconds', 'difficulty_rating', 'notes'
        ]

    def update(self, instance, validated_data):
        # Handle reps and weights lists if provided in initial_data
        if 'reps_list' in self.initial_data:
            instance.set_reps_list(self.initial_data['reps_list'])
        if 'weight_list' in self.initial_data:
            instance.set_weight_list(self.initial_data['weight_list'])
        
        return super().update(instance, validated_data)


class WorkoutSerializer(serializers.ModelSerializer):
    template = WorkoutTemplateSerializer(read_only=True)
    template_id = serializers.IntegerField(write_only=True, required=False)
    sessions = WorkoutSessionSerializer(many=True, read_only=True)
    duration_minutes = serializers.ReadOnlyField()

    class Meta:
        model = Workout
        fields = [
            'id', 'template', 'template_id', 'name', 'status', 'scheduled_date',
            'started_at', 'completed_at', 'actual_duration', 'duration_minutes',
            'calories_burned', 'average_heart_rate', 'max_heart_rate',
            'perceived_exertion', 'user_rating', 'notes', 'ai_prompt_context',
            'sessions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WorkoutCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = [
            'template_id', 'name', 'scheduled_date', 'ai_prompt_context'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        template_id = validated_data.get('template_id')
        
        if template_id:
            try:
                template = WorkoutTemplate.objects.get(id=template_id)
                validated_data['template'] = template
                if not validated_data.get('name'):
                    validated_data['name'] = template.name
            except WorkoutTemplate.DoesNotExist:
                pass
        
        workout = Workout.objects.create(**validated_data)
        
        # Create workout sessions from template exercises
        if workout.template:
            for workout_exercise in workout.template.exercises.all():
                WorkoutSession.objects.create(
                    workout=workout,
                    exercise=workout_exercise.exercise,
                    order=workout_exercise.order,
                    planned_sets=workout_exercise.sets,
                    reps_completed="[]",
                    weight_used="[]"
                )
        
        return workout


class WorkoutPlanWorkoutSerializer(serializers.ModelSerializer):
    template = WorkoutTemplateSerializer(read_only=True)

    class Meta:
        model = WorkoutPlanWorkout
        fields = ['id', 'template', 'week_number', 'day_of_week']


class WorkoutPlanSerializer(serializers.ModelSerializer):
    plan_workouts = WorkoutPlanWorkoutSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutPlan
        fields = [
            'id', 'name', 'description', 'duration_weeks', 'workouts_per_week',
            'start_date', 'end_date', 'is_active', 'completion_percentage',
            'ai_generated', 'generation_context', 'plan_workouts',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['completion_percentage', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WorkoutStatsSerializer(serializers.Serializer):
    total_workouts = serializers.IntegerField()
    workouts_this_week = serializers.IntegerField()
    workouts_this_month = serializers.IntegerField()
    total_calories_burned = serializers.IntegerField()
    avg_workout_duration = serializers.FloatField()
    favorite_workout_type = serializers.CharField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    completion_rate = serializers.FloatField()


class AIWorkoutRequestSerializer(serializers.Serializer):
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


class TodayWorkoutSerializer(serializers.Serializer):
    has_workout = serializers.BooleanField()
    workout = WorkoutSerializer(required=False, allow_null=True)
    suggestions = serializers.ListField(child=serializers.DictField(), required=False)
    motivational_message = serializers.CharField(required=False)