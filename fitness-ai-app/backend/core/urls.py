"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.authtoken.views import obtain_auth_token


def health_check(request):
    """Health check endpoint for load balancers"""
    return JsonResponse({'status': 'healthy', 'service': 'fitness-ai-backend'})


def api_root(request):
    """API documentation root"""
    return JsonResponse({
        'message': 'Fitness AI API',
        'version': '1.0.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'users': '/api/users/',
            'workouts': '/api/workouts/',
            'ai_content': '/api/ai/',
            'avatars': '/api/avatars/',
            'medical': '/api/medical/'
        },
        'docs': '/admin/',
        'health': '/health/'
    })


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health-check'),
    
    # API root
    path('api/', api_root, name='api-root'),
    
    # Authentication
    path('api/auth/token/', obtain_auth_token, name='api-token'),
    
    # API endpoints
    path('api/users/', include('apps.users.urls')),
    path('api/workouts/', include('apps.workouts.urls')),
    path('api/ai/', include('apps.ai_content.urls')),
    path('api/avatars/', include('apps.avatars.urls')),
    
    # Root redirect
    path('', api_root, name='root'),
]
