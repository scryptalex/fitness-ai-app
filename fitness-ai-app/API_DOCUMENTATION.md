# Fitness AI API Documentation

## Overview
A comprehensive REST API for an AI-powered fitness application built with Django REST Framework and Anthropic Claude integration.

## Base URL
- Development: `http://localhost:8000/api/`
- Health Check: `http://localhost:8000/health/`

## Authentication
The API uses Token-based authentication. Include the token in request headers:
```
Authorization: Token your-token-here
```

## API Endpoints

### Authentication (`/api/auth/`)
- `POST /api/auth/token/` - Get authentication token
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `POST /api/users/logout/` - User logout

### User Management (`/api/users/`)
- `GET /api/users/profile/` - Get user profile
- `PATCH /api/users/profile/` - Update user profile
- `GET /api/users/profile/details/` - Get detailed profile settings
- `GET /api/users/dashboard/` - Get dashboard data
- `GET /api/users/stats/` - Get user statistics
- `GET /api/users/health-insights/` - Get health insights

### Goals and Medical Data
- `GET /api/users/goals/` - Get workout goals
- `POST /api/users/goals/` - Create workout goal
- `GET /api/users/medical/` - Get medical data
- `POST /api/users/medical/` - Add medical data
- `POST /api/users/fitness-goals/` - Update fitness goals

### Workouts (`/api/workouts/`)
- `GET /api/workouts/` - List user workouts
- `POST /api/workouts/` - Create workout
- `GET /api/workouts/<id>/` - Get workout details
- `POST /api/workouts/<id>/start/` - Start workout
- `POST /api/workouts/<id>/complete/` - Complete workout
- `GET /api/workouts/today/` - Get today's workout
- `GET /api/workouts/stats/` - Get workout statistics
- `GET /api/workouts/history/` - Get workout history

### Workout Templates
- `GET /api/workouts/templates/` - List workout templates
- `POST /api/workouts/templates/` - Create workout template
- `GET /api/workouts/templates/<id>/` - Get template details

### Exercises
- `GET /api/workouts/exercises/` - List exercises (with filters)

### AI Content Generation (`/api/ai/`)
- `POST /api/ai/generate/workout/` - Generate AI workout
- `POST /api/ai/generate/nutrition/` - Generate nutrition plan
- `POST /api/ai/analyze/health/` - Analyze health data
- `GET /api/ai/requests/` - List AI requests
- `POST /api/ai/requests/<id>/feedback/` - Submit feedback
- `GET /api/ai/usage-stats/` - Get AI usage statistics

### Nutrition Plans
- `GET /api/ai/nutrition/` - List nutrition plans
- `POST /api/ai/nutrition/` - Create nutrition plan
- `GET /api/ai/nutrition/<id>/` - Get nutrition plan details

### Health Insights
- `GET /api/ai/insights/` - List health insights
- `GET /api/ai/insights/<id>/` - Get insight details

### Avatars (`/api/avatars/`)
- `GET /api/avatars/` - List available avatars
- `GET /api/avatars/<id>/` - Get avatar details
- `GET /api/avatars/user/` - List user's weekly avatars
- `GET /api/avatars/user/<day>/` - Get avatar for specific day
- `GET /api/avatars/user/current/` - Get current day's avatar
- `GET /api/avatars/interactions/` - List avatar interactions
- `POST /api/avatars/interact/` - Create avatar interaction
- `GET /api/avatars/presets/` - List avatar presets

## Request/Response Examples

### User Registration
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Generate AI Workout
```bash
curl -X POST http://localhost:8000/api/ai/generate/workout/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "workout_type": "strength",
    "duration_minutes": 45,
    "difficulty_level": "intermediate",
    "equipment_available": ["dumbbells", "resistance_bands"]
  }'
```

### Get Today's Workout
```bash
curl -H "Authorization: Token your-token" \
  http://localhost:8000/api/workouts/today/
```

## Features

### ✅ Complete MVP Features
1. **User Authentication & Profiles** - Registration, login, comprehensive profiles
2. **AI-Powered Workout Generation** - Using Anthropic Claude for personalized workouts
3. **Workout Tracking** - Full workout lifecycle management
4. **Health Data Management** - Encrypted medical data storage
5. **7-Day Avatar System** - VRM-based 3D avatars for each day
6. **Nutrition Planning** - AI-generated meal plans
7. **Health Insights** - AI analysis of health metrics
8. **Progress Analytics** - Comprehensive statistics and tracking

### 🔒 Security Features
- Medical data encryption using Fernet
- Token-based authentication
- CORS protection
- Input validation and sanitization
- Secure environment variable management

### 🤖 AI Integration
- Anthropic Claude for workout generation
- Personalized nutrition planning
- Health data analysis and insights
- Usage tracking and optimization
- Feedback collection for improvement

### 📱 Mobile-Ready
- React Native mobile app structure
- Cross-platform API compatibility
- Real-time workout tracking
- Avatar interaction system

## Environment Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys:**
   ```
   ANTHROPIC_API_KEY=your-actual-key-here
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Start development server:**
   ```bash
   python manage.py runserver
   ```

## Database Models

### Core Models
- **User** - Extended user model with fitness profiles
- **UserProfile** - Additional user settings and preferences
- **MedicalData** - Encrypted health information
- **WorkoutGoal** - User fitness goals

### Workout System
- **Exercise** - Exercise library with instructions
- **WorkoutTemplate** - Reusable workout structures
- **Workout** - User workout instances
- **WorkoutSession** - Individual exercise tracking

### AI Content
- **AIContentRequest** - AI generation tracking
- **NutritionPlan** - Meal plans and dietary guidance
- **HealthInsight** - AI-generated health recommendations

### Avatar System
- **Avatar** - VRM 3D avatar models
- **UserAvatar** - User's weekly avatar configuration
- **AvatarInteraction** - Motivational interactions

## API Status: ✅ FULLY FUNCTIONAL

The API is complete and ready for production use with:
- All MVP features implemented
- Comprehensive error handling
- Security best practices
- Scalable architecture
- Full documentation