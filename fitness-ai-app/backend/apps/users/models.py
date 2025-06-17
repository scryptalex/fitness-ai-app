from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from cryptography.fernet import Fernet
from django.conf import settings
import json


class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]
    
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary (little to no exercise)'),
        ('lightly_active', 'Lightly active (light exercise 1-3 days/week)'),
        ('moderately_active', 'Moderately active (moderate exercise 3-5 days/week)'),
        ('very_active', 'Very active (hard exercise 6-7 days/week)'),
        ('extremely_active', 'Extremely active (very hard exercise, physical job)'),
    ]
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('beginner', 'Beginner (0-6 months)'),
        ('intermediate', 'Intermediate (6 months - 2 years)'),
        ('advanced', 'Advanced (2+ years)'),
        ('expert', 'Expert (5+ years)'),
    ]

    # Extended profile fields
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    
    # Fitness profile
    fitness_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='beginner')
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, default='sedentary')
    
    # Preferences
    preferred_workout_duration = models.PositiveIntegerField(default=30, help_text="Preferred workout duration in minutes")
    available_equipment = models.TextField(blank=True, help_text="Available equipment (comma-separated)")
    
    # Goals and preferences
    fitness_goals = models.TextField(blank=True, help_text="Fitness goals (JSON format)")
    dietary_restrictions = models.TextField(blank=True, help_text="Dietary restrictions and preferences")
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_workout_date = models.DateTimeField(null=True, blank=True)
    workout_streak = models.PositiveIntegerField(default=0)
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=10,
        choices=[('public', 'Public'), ('private', 'Private')],
        default='private'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"

    def get_age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def get_bmi(self):
        if self.height and self.weight:
            height_m = self.height / 100
            return round(float(self.weight) / (height_m ** 2), 1)
        return None

    def get_fitness_goals(self):
        if self.fitness_goals:
            try:
                return json.loads(self.fitness_goals)
            except json.JSONDecodeError:
                return []
        return []

    def set_fitness_goals(self, goals_list):
        self.fitness_goals = json.dumps(goals_list)

    def get_available_equipment(self):
        if self.available_equipment:
            return [item.strip() for item in self.available_equipment.split(',')]
        return []


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    workout_reminders = models.BooleanField(default=True)
    
    # Social features
    is_coach = models.BooleanField(default=False)
    coach_certification = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"{self.user.email} Profile"


class MedicalData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_data')
    
    # Encrypted medical information
    medical_conditions = models.TextField(blank=True, help_text="Encrypted medical conditions")
    medications = models.TextField(blank=True, help_text="Encrypted medications")
    allergies = models.TextField(blank=True, help_text="Encrypted allergies")
    emergency_contact = models.TextField(blank=True, help_text="Encrypted emergency contact")
    
    # Vitals (can be stored unencrypted for analytics)
    resting_heart_rate = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(40), MaxValueValidator(120)])
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(80), MaxValueValidator(200)])
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(50), MaxValueValidator(120)])
    
    # Lifestyle factors
    sleep_hours = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(24)])
    stress_level = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    energy_level = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Tracking
    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medical_data'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"Medical Data for {self.user.email} - {self.recorded_at.date()}"

    def encrypt_field(self, data):
        """Encrypt sensitive data using Fernet encryption"""
        if not data:
            return ""
        
        if not settings.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY not configured")
        
        fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        return fernet.encrypt(data.encode()).decode()

    def decrypt_field(self, encrypted_data):
        """Decrypt sensitive data"""
        if not encrypted_data:
            return ""
        
        if not settings.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY not configured")
        
        fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        return fernet.decrypt(encrypted_data.encode()).decode()

    def set_medical_conditions(self, conditions):
        self.medical_conditions = self.encrypt_field(conditions)

    def get_medical_conditions(self):
        return self.decrypt_field(self.medical_conditions)

    def set_medications(self, medications):
        self.medications = self.encrypt_field(medications)

    def get_medications(self):
        return self.decrypt_field(self.medications)

    def set_allergies(self, allergies):
        self.allergies = self.encrypt_field(allergies)

    def get_allergies(self):
        return self.decrypt_field(self.allergies)

    def set_emergency_contact(self, contact):
        self.emergency_contact = self.encrypt_field(contact)

    def get_emergency_contact(self):
        return self.decrypt_field(self.emergency_contact)


class WorkoutGoal(models.Model):
    GOAL_TYPES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Endurance'),
        ('strength', 'Strength'),
        ('flexibility', 'Flexibility'),
        ('general_fitness', 'General Fitness'),
        ('rehabilitation', 'Rehabilitation'),
        ('sports_specific', 'Sports Specific'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    target_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_unit = models.CharField(max_length=20, blank=True)
    target_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workout_goals'

    def __str__(self):
        return f"{self.user.email} - {self.get_goal_type_display()}"
