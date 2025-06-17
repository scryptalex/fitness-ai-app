from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class Exercise(models.Model):
    MUSCLE_GROUP_CHOICES = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('shoulders', 'Shoulders'),
        ('biceps', 'Biceps'),
        ('triceps', 'Triceps'),
        ('legs', 'Legs'),
        ('glutes', 'Glutes'),
        ('core', 'Core'),
        ('cardio', 'Cardio'),
        ('full_body', 'Full Body'),
    ]
    
    EQUIPMENT_CHOICES = [
        ('bodyweight', 'Bodyweight'),
        ('dumbbells', 'Dumbbells'),
        ('barbells', 'Barbells'),
        ('resistance_bands', 'Resistance Bands'),
        ('kettlebells', 'Kettlebells'),
        ('machines', 'Machines'),
        ('cardio_equipment', 'Cardio Equipment'),
        ('yoga_mat', 'Yoga Mat'),
        ('pull_up_bar', 'Pull-up Bar'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    muscle_groups = models.CharField(max_length=50, choices=MUSCLE_GROUP_CHOICES)
    equipment_required = models.CharField(max_length=50, choices=EQUIPMENT_CHOICES, default='bodyweight')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    
    # Exercise metrics
    calories_per_minute = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Media
    image_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'exercises'
        ordering = ['name']

    def __str__(self):
        return self.name


class WorkoutTemplate(models.Model):
    WORKOUT_TYPE_CHOICES = [
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('hiit', 'HIIT'),
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('stretching', 'Stretching'),
        ('mixed', 'Mixed'),
        ('sports', 'Sports Specific'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPE_CHOICES)
    difficulty_level = models.CharField(max_length=20, choices=Exercise.DIFFICULTY_CHOICES)
    
    # Duration and intensity
    estimated_duration = models.PositiveIntegerField(help_text="Duration in minutes")
    intensity_level = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Requirements
    equipment_needed = models.TextField(help_text="Comma-separated list of equipment")
    space_required = models.CharField(max_length=100, default="Small indoor space")
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    is_ai_generated = models.BooleanField(default=False)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workout_templates'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.workout_type})"

    def get_equipment_list(self):
        if self.equipment_needed:
            return [item.strip() for item in self.equipment_needed.split(',')]
        return []


class WorkoutExercise(models.Model):
    workout_template = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    
    # Exercise parameters
    sets = models.PositiveIntegerField(default=1)
    reps = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    rest_seconds = models.PositiveIntegerField(default=60)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Notes for the exercise in this workout
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'workout_exercises'
        ordering = ['order']
        unique_together = ['workout_template', 'order']

    def __str__(self):
        return f"{self.workout_template.name} - {self.exercise.name}"


class Workout(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workouts')
    template = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE, null=True, blank=True)
    
    # Workout details
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Timing
    scheduled_date = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    actual_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Actual duration in minutes")
    
    # Performance metrics
    calories_burned = models.PositiveIntegerField(null=True, blank=True)
    average_heart_rate = models.PositiveIntegerField(null=True, blank=True)
    max_heart_rate = models.PositiveIntegerField(null=True, blank=True)
    perceived_exertion = models.PositiveIntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rate of Perceived Exertion (1-10)"
    )
    
    # Feedback
    user_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    notes = models.TextField(blank=True)
    
    # AI generation context
    ai_prompt_context = models.TextField(blank=True, help_text="Context used for AI generation")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workouts'
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.user.email} - {self.name} ({self.scheduled_date.date()})"

    @property
    def duration_minutes(self):
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() / 60
        return None


class WorkoutSession(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='sessions')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    
    # Planned vs actual
    planned_sets = models.PositiveIntegerField()
    completed_sets = models.PositiveIntegerField(default=0)
    
    # Performance tracking
    reps_completed = models.TextField(help_text="JSON array of reps per set")
    weight_used = models.TextField(help_text="JSON array of weights per set", blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Feedback
    difficulty_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workout_sessions'
        ordering = ['order']

    def __str__(self):
        return f"{self.workout.name} - {self.exercise.name}"

    def get_reps_list(self):
        try:
            return json.loads(self.reps_completed)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_reps_list(self, reps_list):
        self.reps_completed = json.dumps(reps_list)

    def get_weight_list(self):
        try:
            return json.loads(self.weight_used)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_weight_list(self, weight_list):
        self.weight_used = json.dumps(weight_list)


class WorkoutPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workout_plans')
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Plan details
    duration_weeks = models.PositiveIntegerField()
    workouts_per_week = models.PositiveIntegerField()
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Status
    is_active = models.BooleanField(default=True)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # AI generation
    ai_generated = models.BooleanField(default=False)
    generation_context = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workout_plans'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.name}"


class WorkoutPlanWorkout(models.Model):
    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='plan_workouts')
    template = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE)
    week_number = models.PositiveIntegerField()
    day_of_week = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)])
    
    class Meta:
        db_table = 'workout_plan_workouts'
        unique_together = ['plan', 'week_number', 'day_of_week']

    def __str__(self):
        return f"{self.plan.name} - Week {self.week_number}, Day {self.day_of_week}"
