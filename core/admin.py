from django.contrib import admin
from .models import FarmerQuery, CropRecommendation


@admin.register(FarmerQuery)
class FarmerQueryAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'soil_type', 'season', 'water_availability', 'language', 'created_at']
    list_filter = ['soil_type', 'season', 'water_availability', 'language']
    search_fields = ['location']
    readonly_fields = ['created_at', 'weather_data']
    ordering = ['-created_at']


@admin.register(CropRecommendation)
class CropRecommendationAdmin(admin.ModelAdmin):
    list_display = ['id', 'query', 'created_at']
    readonly_fields = ['created_at', 'ai_response_raw', 'crops_data', 'mandi_prices_data', 'calendar_data']
    ordering = ['-created_at']
