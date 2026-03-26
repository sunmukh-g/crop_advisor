"""
Weather Service - Fetches weather data from OpenWeatherMap API
Falls back to estimated data based on location if API key not available
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_weather_data(location: str) -> dict:
    """
    Fetch current weather data for the given location.
    
    Args:
        location: City/district name (can be in Hindi or English)
    
    Returns:
        Dict with temperature, humidity, condition, rainfall
    """
    api_key = settings.OPENWEATHERMAP_API_KEY
    
    if not api_key or api_key == 'your_openweathermap_api_key_here':
        logger.warning("No OpenWeatherMap API key. Using estimated weather data.")
        return _get_estimated_weather(location)
    
    try:
        # Clean location name (handle Hindi text)
        clean_location = _clean_location_name(location)
        
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': f"{clean_location},IN",
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temperature': round(data['main']['temp'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'humidity': data['main']['humidity'],
                'condition': data['weather'][0]['description'].capitalize(),
                'wind_speed': data['wind']['speed'],
                'rainfall': data.get('rain', {}).get('1h', 0),
                'location_found': data['name'],
                'source': 'openweathermap'
            }
        else:
            logger.warning(f"Weather API returned {response.status_code} for {clean_location}: {response.text}")
            return _get_estimated_weather(location)
    
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return _get_estimated_weather(location)


def _clean_location_name(location: str) -> str:
    """Convert Hindi location names to English approximation"""
    hindi_to_english = {
        'पंजाब': 'Punjab', 'उत्तर प्रदेश': 'Lucknow', 'मध्य प्रदेश': 'Bhopal',
        'राजस्थान': 'Jaipur', 'महाराष्ट्र': 'Mumbai', 'गुजरात': 'Ahmedabad',
        'बिहार': 'Patna', 'हरियाणा': 'Chandigarh', 'दिल्ली': 'Delhi',
        'कर्नाटक': 'Bangalore', 'तमिलनाडु': 'Chennai', 'केरल': 'Kochi',
        'पश्चिम बंगाल': 'Kolkata', 'ओडिशा': 'Bhubaneswar', 'असम': 'Guwahati'
    }
    
    for hindi, english in hindi_to_english.items():
        if hindi in location:
            return english
    
    # If already in English or unknown, return as-is
    return location


def _get_estimated_weather(location: str) -> dict:
    """Return estimated weather based on current month and region"""
    from datetime import datetime
    month = datetime.now().month
    
    # Seasonal temperature estimates for India
    if month in [12, 1, 2]:  # Winter
        temp, humidity, condition = 15, 55, "Cool and partly cloudy"
    elif month in [3, 4, 5]:  # Summer
        temp, humidity, condition = 35, 30, "Hot and sunny"
    elif month in [6, 7, 8, 9]:  # Monsoon
        temp, humidity, condition = 28, 80, "Warm and rainy"
    else:  # Post-monsoon Oct-Nov
        temp, humidity, condition = 25, 60, "Pleasant and clear"
    
    return {
        'temperature': temp,
        'feels_like': temp + 2,
        'humidity': humidity,
        'condition': condition,
        'wind_speed': 12,
        'rainfall': 5 if month in [6, 7, 8, 9] else 0,
        'location_found': location,
        'source': 'estimated'
    }
