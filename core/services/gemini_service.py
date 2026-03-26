"""
Gemini AI Service for Crop Recommendations
Integrates with Google Gemini to provide AI-powered agricultural advice
"""
import json
import re
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_crop_recommendations(farmer_data: dict, weather_data: dict, language: str = 'en') -> dict:
    """
    Use Google Gemini AI to get crop recommendations based on farmer inputs and weather.
    
    Args:
        farmer_data: Dict with location, soil_type, season, water_availability, land_area
        weather_data: Dict with temperature, humidity, rainfall, etc.
        language: 'en' for English, 'hi' for Hindi
    
    Returns:
        Dict with crops, mandi_prices, calendar, tips, summary
    """
    api_key = settings.GEMINI_API_KEY
    
    if not api_key or api_key == 'your_gemini_api_key_here':
        logger.warning("No Gemini API key found. Using mock data.")
        return _get_mock_recommendations(farmer_data, language)
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = _build_prompt(farmer_data, weather_data, language)
        response = model.generate_content(prompt)
        response_text = response.text
        
        result = _parse_ai_response(response_text, farmer_data, language)
        result['data_source'] = 'gemini-1.5-flash'
        return result
    
    except Exception as e:
        logger.error(f"Gemini API error: {e}", exc_info=True)
        return _get_mock_recommendations(farmer_data, language)


def _build_prompt(farmer_data: dict, weather_data: dict, language: str) -> str:
    """Build a detailed prompt for Gemini AI"""
    
    lang_instruction = ""
    if language == 'hi':
        lang_instruction = "IMPORTANT: Respond ENTIRELY in Hindi language (Devanagari script). All text including crop names, descriptions, tips must be in Hindi."
    
    weather_str = ""
    if weather_data:
        weather_str = f"""
Current Weather Conditions:
- Temperature: {weather_data.get('temperature', 'N/A')}°C
- Humidity: {weather_data.get('humidity', 'N/A')}%
- Condition: {weather_data.get('condition', 'N/A')}
- Rainfall (last 30 days): {weather_data.get('rainfall', 'N/A')} mm
"""
    
    prompt = f"""
You are an expert agricultural advisor for Indian farmers. {lang_instruction}

FARMER INFORMATION:
- Location: {farmer_data.get('location', 'India')}
- Soil Type: {farmer_data.get('soil_type', 'loamy')}
- Season: {farmer_data.get('season', 'kharif')}
- Water Availability: {farmer_data.get('water_availability', 'irrigated')}
- Land Area: {farmer_data.get('land_area', 1.0)} acres

{weather_str}

Based on this information, provide a COMPREHENSIVE crop recommendation report. You MUST respond with ONLY valid JSON in the following exact format:

{{
  "summary": "A brief 2-3 sentence overall recommendation summary",
  "crops": [
    {{
      "name": "Crop Name",
      "hindi_name": "फसल का हिंदी नाम",
      "confidence": 95,
      "duration_days": 120,
      "estimated_yield_per_acre": "25-30 quintals",
      "water_requirement": "Medium",
      "fertilizer": "NPK 120:60:40 kg/ha",
      "sowing_time": "June-July",
      "harvesting_time": "October-November",
      "pros": ["High market demand", "Suitable for soil type", "Good water efficiency"],
      "care_tips": "Key care instructions for this crop"
    }},
    {{
      "name": "Second Crop",
      "hindi_name": "दूसरी फसल",
      "confidence": 85,
      "duration_days": 90,
      "estimated_yield_per_acre": "15-20 quintals",
      "water_requirement": "Low",
      "fertilizer": "NPK 80:40:20 kg/ha",
      "sowing_time": "July",
      "harvesting_time": "October",
      "pros": ["Drought resistant", "Low cost", "Good profit margin"],
      "care_tips": "Key care instructions"
    }},
    {{
      "name": "Third Crop",
      "hindi_name": "तीसरी फसल",
      "confidence": 75,
      "duration_days": 60,
      "estimated_yield_per_acre": "10-15 quintals",
      "water_requirement": "Low",
      "fertilizer": "NPK 60:30:20 kg/ha",
      "sowing_time": "August",
      "harvesting_time": "November",
      "pros": ["Fast growing", "Versatile", "Easy to sell"],
      "care_tips": "Key care instructions"
    }}
  ],
  "mandi_prices": [
    {{
      "crop": "Crop Name",
      "current_price_per_quintal": 2500,
      "predicted_price_at_harvest": 2800,
      "trend": "rising",
      "msp": 2015,
      "best_market": "Nearby Mandi Name",
      "price_forecast_note": "Brief note on price trend"
    }},
    {{
      "crop": "Second Crop",
      "current_price_per_quintal": 3500,
      "predicted_price_at_harvest": 3200,
      "trend": "stable",
      "msp": 3000,
      "best_market": "Mandi Name",
      "price_forecast_note": "Brief note"
    }},
    {{
      "crop": "Third Crop",
      "current_price_per_quintal": 4500,
      "predicted_price_at_harvest": 5000,
      "trend": "rising",
      "msp": 4000,
      "best_market": "Mandi Name",
      "price_forecast_note": "Brief note"
    }}
  ],
  "seasonal_calendar": [
    {{"month": "January", "hindi_month": "जनवरी", "activities": ["Activity 1", "Activity 2"], "crops_stage": "Crop growth stage"}},
    {{"month": "February", "hindi_month": "फरवरी", "activities": ["Activity 1"], "crops_stage": "Stage"}},
    {{"month": "March", "hindi_month": "मार्च", "activities": ["Activity 1", "Activity 2"], "crops_stage": "Stage"}},
    {{"month": "April", "hindi_month": "अप्रैल", "activities": ["Activity 1"], "crops_stage": "Stage"}},
    {{"month": "May", "hindi_month": "मई", "activities": ["Activity 1"], "crops_stage": "Stage"}},
    {{"month": "June", "hindi_month": "जून", "activities": ["Sowing begins", "Land preparation"], "crops_stage": "Preparation"}},
    {{"month": "July", "hindi_month": "जुलाई", "activities": ["Activity 1", "Activity 2"], "crops_stage": "Germination"}},
    {{"month": "August", "hindi_month": "अगस्त", "activities": ["Activity 1"], "crops_stage": "Growth"}},
    {{"month": "September", "hindi_month": "सितंबर", "activities": ["Activity 1"], "crops_stage": "Flowering"}},
    {{"month": "October", "hindi_month": "अक्टूबर", "activities": ["Harvesting", "Activity 2"], "crops_stage": "Harvest"}},
    {{"month": "November", "hindi_month": "नवंबर", "activities": ["Post harvest", "Rabi preparation"], "crops_stage": "Complete"}},
    {{"month": "December", "hindi_month": "दिसंबर", "activities": ["Activity 1"], "crops_stage": "Rest period"}}
  ],
  "farming_tips": "5-6 important farming tips specific to the farmer's conditions, soil type and location. Include information about government schemes like PM-KISAN, crop insurance (PMFBY), soil health card etc.",
  "government_schemes": [
    {{"name": "Scheme name", "benefit": "Benefit description", "how_to_apply": "Application method"}},
    {{"name": "PM-KISAN", "benefit": "₹6000/year direct income support", "how_to_apply": "Apply at pmkisan.gov.in or nearest CSC"}},
    {{"name": "PMFBY", "benefit": "Crop insurance against natural disasters", "how_to_apply": "Contact nearest bank or insurance company before sowing"}}
  ]
}}

Provide realistic, location-specific recommendations for {farmer_data.get('location', 'India')}.
"""
    return prompt


def _parse_ai_response(response_text: str, farmer_data: dict, language: str) -> dict:
    """Parse the AI response and extract structured data"""
    try:
        # Try to find JSON in response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
            return data
    except (json.JSONDecodeError, AttributeError) as e:
        logger.error(f"Failed to parse AI response: {e}")
    
    return _get_mock_recommendations(farmer_data, language)


def _get_mock_recommendations(farmer_data: dict, language: str = 'en') -> dict:
    """Return realistic mock data when API is unavailable"""
    import random
    import hashlib
    
    location = farmer_data.get('location', 'India')
    season = farmer_data.get('season', 'kharif')
    soil = farmer_data.get('soil_type', 'loamy')
    
    # Create a deterministic random generator based on the location name
    seed_str = f"{location.lower().strip()}-{season}-{soil}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    
    # Base crops pool
    kharif_crops = [
        {"name": "Rice (Paddy)", "hindi_name": "धान", "duration_days": 120, "water_requirement": "High", "fertilizer": "NPK 120:60:40 kg/ha", "sowing_time": "June - July", "harvesting_time": "Oct - Nov", "pros": ["Staple food", "High yield", "MSP assured"], "care_tips": "Maintain 5cm standing water during vegetative stage."},
        {"name": "Maize (Corn)", "hindi_name": "मक्का", "duration_days": 90, "water_requirement": "Medium", "fertilizer": "NPK 150:75:50 kg/ha", "sowing_time": "June - July", "harvesting_time": "Sep - Oct", "pros": ["Drought tolerant", "Multiple uses"], "care_tips": "Irrigate at critical stages: germination, silking."},
        {"name": "Soybean", "hindi_name": "सोयाबीन", "duration_days": 100, "water_requirement": "Medium", "fertilizer": "NPK 25:60:40 kg/ha", "sowing_time": "June 20 - July 15", "harvesting_time": "October", "pros": ["Protein-rich", "Nitrogen fixing"], "care_tips": "Avoid waterlogging. Weed management critical."},
        {"name": "Cotton", "hindi_name": "कपास", "duration_days": 150, "water_requirement": "Medium", "fertilizer": "NPK 120:60:60 kg/ha", "sowing_time": "May - June", "harvesting_time": "Oct - Dec", "pros": ["Cash crop", "High profit"], "care_tips": "Monitor for pink bollworm. Use pheromone traps."},
        {"name": "Groundnut", "hindi_name": "मूंगफली", "duration_days": 110, "water_requirement": "Low", "fertilizer": "NPK 20:40:40 kg/ha", "sowing_time": "June - July", "harvesting_time": "October", "pros": ["Oilseed", "Good market"], "care_tips": "Apply gypsum at pegging stage."}
    ]
    
    rabi_crops = [
        {"name": "Wheat", "hindi_name": "गेहूं", "duration_days": 140, "water_requirement": "Medium", "fertilizer": "NPK 120:60:40 kg/ha", "sowing_time": "November", "harvesting_time": "March - April", "pros": ["High MSP", "Stable market"], "care_tips": "First irrigation at Crown Root Initiation is critical."},
        {"name": "Mustard", "hindi_name": "सरसों", "duration_days": 110, "water_requirement": "Low", "fertilizer": "NPK 80:40:25 kg/ha", "sowing_time": "October", "harvesting_time": "Feb - March", "pros": ["Oil crop", "Low water"], "care_tips": "Spray boron for better pod setting."},
        {"name": "Chickpea", "hindi_name": "चना", "duration_days": 100, "water_requirement": "Very Low", "fertilizer": "NPK 20:50:20 kg/ha", "sowing_time": "Oct - Nov", "harvesting_time": "Feb - Mar", "pros": ["Nitrogen fixing", "Export demand"], "care_tips": "Treat seeds with Rhizobium. Watch for pod borer."},
        {"name": "Barley", "hindi_name": "जौ", "duration_days": 120, "water_requirement": "Low", "fertilizer": "NPK 60:30:20 kg/ha", "sowing_time": "November", "harvesting_time": "April", "pros": ["Hardy crop", "Fodder & Grain"], "care_tips": "Needs less water than wheat."},
        {"name": "Lentil", "hindi_name": "मसूर", "duration_days": 110, "water_requirement": "Very Low", "fertilizer": "NPK 20:40:20 kg/ha", "sowing_time": "Nov", "harvesting_time": "March", "pros": ["High protein", "Short duration"], "care_tips": "Very sensitive to waterlogging."}
    ]
    
    pool = kharif_crops if season in ['kharif', 'zaid'] else rabi_crops
    rng.shuffle(pool)
    crops = pool[:3] # Select exactly 3 crops
    
    mandi_prices = []
    
    # Generate dynamic yields and prices
    for i, crop in enumerate(crops):
        base_yield = rng.randint(8, 26)
        crop["estimated_yield_per_acre"] = f"{base_yield}-{base_yield+4} quintals"
        crop["confidence"] = rng.randint(75, 96) - (i * 5)
        
        base_price = rng.randint(1800, 6500)
        trend = rng.choice(['rising', 'stable', 'falling'])
        harvest_price = base_price + rng.randint(100, 400) if trend == 'rising' else (base_price - rng.randint(100, 300) if trend == 'falling' else base_price)
        
        market_suffixes = ["Mandi", "APMC", "Main Market", "Trading Center"]
        mandi_prices.append({
            "crop": crop["name"],
            "current_price_per_quintal": base_price,
            "predicted_price_at_harvest": harvest_price,
            "trend": trend,
            "msp": base_price - rng.randint(50, 200),
            "best_market": f"{location} {rng.choice(market_suffixes)}",
            "price_forecast_note": f"Prices expected to {'rise' if trend=='rising' else 'fall'} due to market conditions."
        })
    
    return {
        "summary": f"Based on your {soil} soil type and location in {location}, we recommend focusing on {crops[0]['name']} as the primary crop. The current weather and soil conditions are optimal. Using our dynamic fallback data generation since API keys are missing.",
        "crops": crops,
        "mandi_prices": mandi_prices,
        "seasonal_calendar": _get_seasonal_calendar(season, location, rng),
        "farming_tips": _get_farming_tips(soil, location, rng),
        "government_schemes": _get_govt_schemes(rng),
        "data_source": "mock"
    }

def _get_farming_tips(soil: str, location: str, rng) -> str:
    tips_pool = [
        f"**Local Adaptation**: Varieties suited for {location} perform 15% better than generic seeds.",
        f"**Soil Health**: {soil.capitalize()} soil requires regular organic matter additions to maintain fertility.",
        "**Seed Certification**: Always use certified/high-yielding variety (HYV) seeds.",
        "**Crop Insurance**: Apply for PMFBY (Pradhan Mantri Fasal Bima Yojana) before sowing deadline.",
        "**Water Management**: Install drip/sprinkler irrigation to save 40-50% water.",
        "**Integrated Pest Management**: Use neem-based pesticides and biological control.",
        "**Market Linkage**: Register on eNAM portal for better price discovery.",
        "**Nutrient Management**: Use soil test-based fertilizer application to reduce costs.",
        "**Weed Control**: Apply pre-emergence herbicides within 48 hours of sowing.",
        "**Storage Solutions**: Ensure grain moisture is below 12% before storage to prevent fungus."
    ]
    return "\n".join([f"{i+1}. {tip}" for i, tip in enumerate(rng.sample(tips_pool, 5))])

def _get_govt_schemes(rng) -> list:
    schemes_pool = [
        {"name": "PM-KISAN", "benefit": "₹6,000/year direct income support", "how_to_apply": "pmkisan.gov.in"},
        {"name": "PMFBY", "benefit": "Comprehensive crop insurance at low premium", "how_to_apply": "Nearest bank branch"},
        {"name": "Soil Health Card", "benefit": "Free soil testing to optimize fertilizer use", "how_to_apply": "Krishi Vigyan Kendra"},
        {"name": "Kisan Credit Card (KCC)", "benefit": "Low-interest loans up to ₹3 Lakh", "how_to_apply": "SBI/PNB/Cooperative Banks"},
        {"name": "PKVY", "benefit": "Support and subsidy for organic farming", "how_to_apply": "State Agriculture Dept"},
        {"name": "PMKSY", "benefit": "Subsidy on micro-irrigation systems", "how_to_apply": "Horticulture Department"},
        {"name": "eNAM", "benefit": "Online trading platform for better prices", "how_to_apply": "enam.gov.in portal"}
    ]
    return rng.sample(schemes_pool, 3)

def _get_seasonal_calendar(season: str, location: str, rng) -> list:
    """Return a 12-month farming calendar with some variation"""
    activities_pool = [
        "Weed management", "Pest monitoring", "Apply basal fertilizer", "Irrigation scheduling", "Foliar spray"
    ]
    
    months = [
        {"month": "January", "hindi_month": "जनवरी", "activities": ["Rabi crop irrigation", rng.choice(activities_pool)], "crops_stage": "Rabi vegetative/flowering"},
        {"month": "February", "hindi_month": "फरवरी", "activities": ["Wheat heading", "Mustard pod filling"], "crops_stage": "Rabi grain/pod filling"},
        {"month": "March", "hindi_month": "मार्च", "activities": ["Harvest begins", "Threshing & storage"], "crops_stage": "Rabi harvest begins"},
        {"month": "April", "hindi_month": "अप्रैल", "activities": ["Post-harvest land preparation", "Market sales"], "crops_stage": "Rabi harvest complete"},
        {"month": "May", "hindi_month": "मई", "activities": ["Deep plowing", f"Procure {season} seeds in {location}"], "crops_stage": "Land preparation"},
        {"month": "June", "hindi_month": "जून", "activities": ["Nursery raising", "Apply basal fertilizer"], "crops_stage": "Kharif preparation"},
        {"month": "July", "hindi_month": "जुलाई", "activities": ["Transplanting/Sowing", rng.choice(activities_pool)], "crops_stage": "Kharif sowing season"},
        {"month": "August", "hindi_month": "अगस्त", "activities": ["Irrigation management", "Pest & disease monitoring"], "crops_stage": "Kharif vegetative growth"},
        {"month": "September", "hindi_month": "सितंबर", "activities": ["Foliar spray of nutrients", "Plan marketing channels"], "crops_stage": "Kharif flowering"},
        {"month": "October", "hindi_month": "अक्टूबर", "activities": ["Early harvest", "Post-harvest processing"], "crops_stage": "Kharif harvest begins"},
        {"month": "November", "hindi_month": "नवंबर", "activities": ["Rabi sowing", "Apply basal dose fertilizer"], "crops_stage": "Rabi sowing season"},
        {"month": "December", "hindi_month": "दिसंबर", "activities": ["Rabi crop care", rng.choice(activities_pool)], "crops_stage": "Rabi vegetative stage"}
    ]
    return months
