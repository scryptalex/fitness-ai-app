from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, MedicalData, WorkoutGoal


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 'password', 
            'password_confirm', 'date_of_birth', 'gender', 'height', 'weight',
            'fitness_level', 'activity_level', 'preferred_workout_duration',
            'available_equipment', 'dietary_restrictions'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField(source='get_age')
    bmi = serializers.ReadOnlyField(source='get_bmi')
    fitness_goals = serializers.JSONField(source='get_fitness_goals', read_only=True)
    equipment_list = serializers.ListField(source='get_available_equipment', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 
            'date_of_birth', 'age', 'gender', 'height', 'weight', 'bmi',
            'fitness_level', 'activity_level', 'preferred_workout_duration',
            'available_equipment', 'equipment_list', 'fitness_goals',
            'dietary_restrictions', 'last_workout_date', 'workout_streak',
            'profile_visibility', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        # Handle fitness goals if provided
        if 'fitness_goals' in self.initial_data:
            instance.set_fitness_goals(self.initial_data['fitness_goals'])
        
        return super().update(instance, validated_data)


class UserProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'avatar_url', 'bio', 'location', 'timezone',
            'email_notifications', 'push_notifications', 'workout_reminders',
            'is_coach', 'coach_certification'
        ]


class MedicalDataSerializer(serializers.ModelSerializer):
    # Use custom methods for encrypted fields
    medical_conditions_decrypted = serializers.SerializerMethodField()
    medications_decrypted = serializers.SerializerMethodField()
    allergies_decrypted = serializers.SerializerMethodField()
    emergency_contact_decrypted = serializers.SerializerMethodField()

    class Meta:
        model = MedicalData
        fields = [
            'id', 'resting_heart_rate', 'blood_pressure_systolic', 
            'blood_pressure_diastolic', 'sleep_hours', 'stress_level', 
            'energy_level', 'medical_conditions_decrypted', 
            'medications_decrypted', 'allergies_decrypted', 
            'emergency_contact_decrypted', 'recorded_at', 'updated_at'
        ]
        read_only_fields = ['id', 'recorded_at', 'updated_at']

    def get_medical_conditions_decrypted(self, obj):
        try:
            return obj.get_medical_conditions()
        except:
            return ""

    def get_medications_decrypted(self, obj):
        try:
            return obj.get_medications()
        except:
            return ""

    def get_allergies_decrypted(self, obj):
        try:
            return obj.get_allergies()
        except:
            return ""

    def get_emergency_contact_decrypted(self, obj):
        try:
            return obj.get_emergency_contact()
        except:
            return ""

    def create(self, validated_data):
        # Handle encrypted fields from initial_data
        medical_data = MedicalData.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
        
        # Set encrypted fields if provided
        if 'medical_conditions' in self.initial_data:
            medical_data.set_medical_conditions(self.initial_data['medical_conditions'])
        if 'medications' in self.initial_data:
            medical_data.set_medications(self.initial_data['medications'])
        if 'allergies' in self.initial_data:
            medical_data.set_allergies(self.initial_data['allergies'])
        if 'emergency_contact' in self.initial_data:
            medical_data.set_emergency_contact(self.initial_data['emergency_contact'])
        
        medical_data.save()
        return medical_data

    def update(self, instance, validated_data):
        # Update encrypted fields if provided
        if 'medical_conditions' in self.initial_data:
            instance.set_medical_conditions(self.initial_data['medical_conditions'])
        if 'medications' in self.initial_data:
            instance.set_medications(self.initial_data['medications'])
        if 'allergies' in self.initial_data:
            instance.set_allergies(self.initial_data['allergies'])
        if 'emergency_contact' in self.initial_data:
            instance.set_emergency_contact(self.initial_data['emergency_contact'])
        
        return super().update(instance, validated_data)


class WorkoutGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutGoal
        fields = [
            'id', 'goal_type', 'target_value', 'target_unit', 
            'target_date', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        return WorkoutGoal.objects.create(
            user=self.context['request'].user,
            **validated_data
        )


class UserStatsSerializer(serializers.Serializer):
    workouts_this_week = serializers.IntegerField()
    workouts_this_month = serializers.IntegerField()
    calories_burned_week = serializers.IntegerField()
    calories_burned_month = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    total_workouts = serializers.IntegerField()
    avg_workout_duration = serializers.FloatField()
    favorite_workout_type = serializers.CharField()