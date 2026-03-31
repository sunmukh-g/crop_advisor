from django.db import models
from django.contrib.auth.models import User
import json


class FarmerQuery(models.Model):
    """Stores farmer input data for crop recommendation"""
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='queries')
    
    SOIL_CHOICES = [
        ('loamy', 'Loamy / दोमट'),
        ('sandy', 'Sandy / बलुई'),
        ('clay', 'Clay / चिकनी मिट्टी'),
        ('silt', 'Silty / गाद मिट्टी'),
        ('black', 'Black Cotton / काली मिट्टी'),
        ('red', 'Red / लाल मिट्टी'),
        ('alluvial', 'Alluvial / जलोढ़ मिट्टी'),
    ]
    
    SEASON_CHOICES = [
        ('kharif', 'Kharif (Jun-Nov) / खरीफ'),
        ('rabi', 'Rabi (Nov-Apr) / रबी'),
        ('zaid', 'Zaid (Apr-Jun) / जायद'),
        ('year_round', 'Year Round / साल भर'),
    ]
    
    WATER_CHOICES = [
        ('irrigated', 'Well Irrigated / सिंचित'),
        ('semi_irrigated', 'Semi Irrigated / अर्ध-सिंचित'),
        ('rainfed', 'Rain-fed Only / वर्षा आधारित'),
        ('drip', 'Drip Irrigation / ड्रिप सिंचाई'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'हिंदी (Hindi)'),
    ]
    
    location = models.CharField(max_length=200, verbose_name="Location / स्थान")
    soil_type = models.CharField(max_length=50, choices=SOIL_CHOICES, verbose_name="Soil Type / मिट्टी का प्रकार")
    season = models.CharField(max_length=50, choices=SEASON_CHOICES, verbose_name="Season / ऋतु")
    water_availability = models.CharField(max_length=50, choices=WATER_CHOICES, verbose_name="Water Availability / जल उपलब्धता")
    land_area = models.FloatField(default=1.0, verbose_name="Land Area (acres) / भूमि क्षेत्र (एकड़)")
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Weather data fetched
    weather_data = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Farmer Query"
        verbose_name_plural = "Farmer Queries"
    
    def __str__(self):
        return f"{self.location} - {self.soil_type} - {self.season}"


class CropRecommendation(models.Model):
    """AI-generated crop recommendations for a farmer query"""
    
    query = models.OneToOneField(FarmerQuery, on_delete=models.CASCADE, related_name='recommendation')
    
    # Raw AI response
    ai_response_raw = models.TextField(blank=True)
    
    # Parsed data
    crops_data = models.JSONField(default=list)            # List of recommended crops
    mandi_prices_data = models.JSONField(default=list)     # Price forecasts
    calendar_data = models.JSONField(default=list)          # Seasonal calendar
    farming_tips = models.TextField(blank=True)             # General tips
    summary = models.TextField(blank=True)                  # Overall summary
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Crop Recommendation"
    
    def __str__(self):
        return f"Recommendation for {self.query}"
    
    def get_top_crops(self):
        return self.crops_data[:3] if self.crops_data else []
