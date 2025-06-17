import os
from anthropic import Anthropic
from django.conf import settings
from typing import Dict, List, Optional


class ClaudeClient:
    def __init__(self):
        self.client = Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )
        self.model = "claude-3-5-sonnet-latest"
    
    def generate_workout(self, user_profile: Dict, workout_type: str = "general") -> Dict:
        """Generate personalized workout based on user profile"""
        prompt = self._build_workout_prompt(user_profile, workout_type)
        
        try:
            message = self.client.messages.create(
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model
            )
            
            return {
                "success": True,
                "workout": message.content,
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workout": None
            }
    
    def generate_nutrition_plan(self, user_profile: Dict, goals: List[str]) -> Dict:
        """Generate personalized nutrition plan"""
        prompt = self._build_nutrition_prompt(user_profile, goals)
        
        try:
            message = self.client.messages.create(
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model
            )
            
            return {
                "success": True,
                "nutrition_plan": message.content,
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "nutrition_plan": None
            }
    
    def analyze_medical_data(self, medical_data: Dict) -> Dict:
        """Analyze medical data and provide health insights"""
        prompt = self._build_medical_analysis_prompt(medical_data)
        
        try:
            message = self.client.messages.create(
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model
            )
            
            return {
                "success": True,
                "analysis": message.content,
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    def _build_workout_prompt(self, user_profile: Dict, workout_type: str) -> str:
        """Build personalized workout generation prompt"""
        return f"""
        You are a certified fitness instructor creating a personalized workout plan.
        
        User Profile:
        - Age: {user_profile.get('age', 'Not specified')}
        - Gender: {user_profile.get('gender', 'Not specified')}
        - Fitness Level: {user_profile.get('fitness_level', 'Beginner')}
        - Goals: {', '.join(user_profile.get('goals', []))}
        - Available Time: {user_profile.get('workout_duration', '30')} minutes
        - Equipment: {user_profile.get('equipment', 'None')}
        - Medical Conditions: {user_profile.get('medical_conditions', 'None')}
        - Preferred Activities: {user_profile.get('preferred_activities', 'Any')}
        
        Workout Type: {workout_type}
        
        Please create a detailed workout plan with:
        1. Warm-up (5-10 minutes)
        2. Main workout with specific exercises, sets, reps, and rest periods
        3. Cool-down and stretching (5-10 minutes)
        4. Safety considerations and modifications
        5. Progress tracking suggestions
        
        Format the response as a structured workout plan with clear instructions.
        """
    
    def _build_nutrition_prompt(self, user_profile: Dict, goals: List[str]) -> str:
        """Build personalized nutrition plan prompt"""
        return f"""
        You are a certified nutritionist creating a personalized meal plan.
        
        User Profile:
        - Age: {user_profile.get('age', 'Not specified')}
        - Gender: {user_profile.get('gender', 'Not specified')}
        - Weight: {user_profile.get('weight', 'Not specified')} kg
        - Height: {user_profile.get('height', 'Not specified')} cm
        - Activity Level: {user_profile.get('activity_level', 'Moderate')}
        - Dietary Restrictions: {user_profile.get('dietary_restrictions', 'None')}
        - Food Allergies: {user_profile.get('food_allergies', 'None')}
        - Goals: {', '.join(goals)}
        
        Please create a comprehensive nutrition plan with:
        1. Daily calorie target and macronutrient breakdown
        2. Sample meal plan for 3 days
        3. Healthy snack options
        4. Hydration recommendations
        5. Supplement suggestions (if applicable)
        6. Meal prep tips
        
        Ensure all recommendations are safe and evidence-based.
        """
    
    def _build_medical_analysis_prompt(self, medical_data: Dict) -> str:
        """Build medical data analysis prompt"""
        return f"""
        You are a health data analyst providing insights on fitness metrics.
        
        IMPORTANT: This is for informational purposes only and should not replace professional medical advice.
        
        Health Data:
        - Heart Rate: {medical_data.get('heart_rate', 'Not provided')} bpm
        - Blood Pressure: {medical_data.get('blood_pressure', 'Not provided')}
        - Sleep Quality: {medical_data.get('sleep_quality', 'Not provided')}/10
        - Stress Level: {medical_data.get('stress_level', 'Not provided')}/10
        - Energy Level: {medical_data.get('energy_level', 'Not provided')}/10
        - Recent Symptoms: {medical_data.get('symptoms', 'None reported')}
        
        Please provide:
        1. General health trend analysis
        2. Fitness readiness assessment
        3. Lifestyle recommendations
        4. When to consult healthcare professionals
        5. Tracking suggestions for improvement
        
        Always include medical disclaimer and emphasize consulting healthcare providers for medical concerns.
        """