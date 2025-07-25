# Generated by Django 5.2.3 on 2025-06-17 20:50

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AIContentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_type', models.CharField(choices=[('workout', 'Workout Plan'), ('nutrition', 'Nutrition Plan'), ('health_analysis', 'Health Analysis'), ('exercise_instructions', 'Exercise Instructions'), ('motivation', 'Motivational Content')], max_length=30)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('user_context', models.JSONField(help_text='User profile data used for generation')),
                ('prompt_context', models.JSONField(help_text='Specific request parameters')),
                ('generated_content', models.TextField(blank=True)),
                ('tokens_used', models.PositiveIntegerField(blank=True, null=True)),
                ('generation_time_seconds', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('user_rating', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('user_feedback', models.TextField(blank=True)),
                ('error_message', models.TextField(blank=True)),
                ('retry_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'ai_content_requests',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ContentTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('template_type', models.CharField(choices=[('workout_prompt', 'Workout Generation Prompt'), ('nutrition_prompt', 'Nutrition Plan Prompt'), ('health_prompt', 'Health Analysis Prompt'), ('motivation_prompt', 'Motivational Content Prompt')], max_length=30)),
                ('prompt_template', models.TextField()),
                ('required_parameters', models.JSONField(default=list)),
                ('optional_parameters', models.JSONField(default=list)),
                ('usage_count', models.PositiveIntegerField(default=0)),
                ('success_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'content_templates',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='HealthInsight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('insight_type', models.CharField(choices=[('general', 'General Health'), ('fitness', 'Fitness Related'), ('nutrition', 'Nutrition Related'), ('sleep', 'Sleep Related'), ('stress', 'Stress Related'), ('recovery', 'Recovery Related')], max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('recommendations', models.JSONField(default=list)),
                ('data_sources', models.JSONField(help_text='Medical/fitness data used for insight')),
                ('confidence_score', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('is_read', models.BooleanField(default=False)),
                ('is_dismissed', models.BooleanField(default=False)),
                ('user_rating', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ai_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ai_content.aicontentrequest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='health_insights', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'health_insights',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NutritionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('daily_calories', models.PositiveIntegerField(blank=True, null=True)),
                ('protein_grams', models.PositiveIntegerField(blank=True, null=True)),
                ('carbs_grams', models.PositiveIntegerField(blank=True, null=True)),
                ('fats_grams', models.PositiveIntegerField(blank=True, null=True)),
                ('meal_plan', models.JSONField(help_text='Structured meal plan data')),
                ('shopping_list', models.JSONField(blank=True, default=list)),
                ('preparation_tips', models.TextField(blank=True)),
                ('duration_days', models.PositiveIntegerField(default=7)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ai_request', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ai_content.aicontentrequest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nutrition_plans', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'nutrition_plans',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIUsageStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('total_requests', models.PositiveIntegerField(default=0)),
                ('successful_requests', models.PositiveIntegerField(default=0)),
                ('failed_requests', models.PositiveIntegerField(default=0)),
                ('total_tokens_used', models.PositiveIntegerField(default=0)),
                ('workout_requests', models.PositiveIntegerField(default=0)),
                ('nutrition_requests', models.PositiveIntegerField(default=0)),
                ('health_analysis_requests', models.PositiveIntegerField(default=0)),
                ('avg_response_time', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('avg_user_rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_usage_stats', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'ai_usage_stats',
                'ordering': ['-date'],
                'unique_together': {('user', 'date')},
            },
        ),
    ]
