import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .forms import FarmerInputForm
from .models import FarmerQuery, CropRecommendation
from .services.gemini_service import get_crop_recommendations
from .services.weather_service import get_weather_data
from .services.report_service import generate_pdf_report

logger = logging.getLogger(__name__)


def advisor_view(request):
    """Advisor page — crop recommendation form (separate from home page)"""
    if request.method == 'POST':
        form = FarmerInputForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            if request.user.is_authenticated:
                query.user = request.user
            query.save()
            weather_data = get_weather_data(query.location)
            query.weather_data = weather_data
            query.save()
            farmer_data = {
                'location': query.location,
                'soil_type': query.soil_type,
                'season': query.season,
                'water_availability': query.water_availability,
                'land_area': query.land_area,
            }
            ai_result = get_crop_recommendations(farmer_data, weather_data, query.language)
            CropRecommendation.objects.create(
                query=query,
                summary=ai_result.get('summary', ''),
                crops_data=ai_result.get('crops', []),
                mandi_prices_data=ai_result.get('mandi_prices', []),
                calendar_data=ai_result.get('seasonal_calendar', []),
                farming_tips=ai_result.get('farming_tips', ''),
            )
            return redirect('results', query_id=query.id)
        else:
            return render(request, 'core/advisor.html', {'form': form})
    else:
        form = FarmerInputForm()
    return render(request, 'core/advisor.html', {'form': form})


def home_view(request):
    """Home page — gallery + how it works + recent queries"""
    recent_queries = FarmerQuery.objects.filter(
        recommendation__isnull=False
    ).select_related('recommendation')[:5]

    return render(request, 'core/home.html', {
        'recent_queries': recent_queries,
    })


def results_view(request, query_id):
    """Display AI crop recommendations"""
    query = get_object_or_404(FarmerQuery, id=query_id)
    
    try:
        recommendation = query.recommendation
    except CropRecommendation.DoesNotExist:
        messages.error(request, "Recommendation not found. Please try again.")
        return redirect('home')
    
    # Get government schemes from crops_data if available
    ai_result_mock = {}

    crops = recommendation.crops_data[:3]
    mandi_prices = [dict(p) for p in recommendation.mandi_prices_data[:3]]

    # For UI only: estimate gross income from predicted price * avg yield.
    # AI provides yield as a range like "15-20 quintals"; we take avg ~= low + 3 (same as PDF logic).
    for i, p in enumerate(mandi_prices):
        crop = crops[i] if i < len(crops) else {}
        yield_str = crop.get('estimated_yield_per_acre', '')
        try:
            yield_low = float(yield_str.split('-')[0].replace('quintals', '').strip())
            yield_avg = yield_low + 3
        except Exception:
            yield_avg = 18

        predicted_price = p.get('predicted_price_at_harvest', 0)
        try:
            income = float(yield_avg) * float(predicted_price)
        except Exception:
            income = 0

        p['estimated_income_per_acre'] = income

    context = {
        'query': query,
        'recommendation': recommendation,
        'crops': crops,
        'mandi_prices': mandi_prices,
        'calendar': recommendation.calendar_data,
        'weather': query.weather_data,
        'tips': recommendation.farming_tips,
    }
    
    return render(request, 'core/results.html', context)


def download_report_view(request, query_id):
    """Generate and download PDF report"""
    query = get_object_or_404(FarmerQuery, id=query_id)
    
    try:
        recommendation = query.recommendation
    except CropRecommendation.DoesNotExist:
        return HttpResponse("Recommendation not found", status=404)
    
    try:
        pdf_bytes = generate_pdf_report(query, recommendation)
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f"KisanAI_CropReport_{query.location.replace(' ', '_')}_{query.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        messages.error(request, f"Error generating PDF report: {str(e)}")
        return redirect('results', query_id=query_id)


def view_report_view(request, query_id):
    """Preview report in browser"""
    query = get_object_or_404(FarmerQuery, id=query_id)
    
    try:
        recommendation = query.recommendation
    except CropRecommendation.DoesNotExist:
        return redirect('home')
    
    context = {
        'query': query,
        'recommendation': recommendation,
        'crops': recommendation.crops_data[:3],
        'mandi_prices': recommendation.mandi_prices_data[:3],
        'calendar': recommendation.calendar_data,
        'weather': query.weather_data,
    }
    
    return render(request, 'core/report_preview.html', context)


@require_http_methods(["GET"])
def api_weather_view(request):
    """API endpoint to get weather for a location"""
    location = request.GET.get('location', '')
    if not location:
        return JsonResponse({'error': 'Location required'}, status=400)
    
    weather = get_weather_data(location)
    return JsonResponse(weather)


def _validate_api_payload(payload: dict) -> tuple[bool, dict]:
    """
    Validate the POST payload for crop recommendation API.
    Returns: (is_valid, errors_dict)
    """
    errors = {}

    required_fields = ['location', 'soil_type', 'season', 'water_availability', 'land_area']
    for field in required_fields:
        if field not in payload or payload.get(field) in (None, ''):
            errors[field] = 'This field is required.'

    if 'language' in payload and payload.get('language') not in ('en', 'hi'):
        errors['language'] = "Language must be 'en' or 'hi'."

    # Validate soil/season/water against model choices
    if not errors.get('soil_type'):
        allowed_soils = {k for k, _ in FarmerQuery.SOIL_CHOICES}
        if payload.get('soil_type') not in allowed_soils:
            errors['soil_type'] = 'Invalid soil_type choice.'

    if not errors.get('season'):
        allowed_seasons = {k for k, _ in FarmerQuery.SEASON_CHOICES}
        if payload.get('season') not in allowed_seasons:
            errors['season'] = 'Invalid season choice.'

    if not errors.get('water_availability'):
        allowed_water = {k for k, _ in FarmerQuery.WATER_CHOICES}
        if payload.get('water_availability') not in allowed_water:
            errors['water_availability'] = 'Invalid water_availability choice.'

    # Validate land_area numeric range (same idea as clean_land_area)
    if not errors.get('land_area'):
        try:
            land_area = float(payload.get('land_area'))
        except (TypeError, ValueError):
            errors['land_area'] = 'land_area must be a number.'
        else:
            if land_area <= 0 or land_area > 10000:
                errors['land_area'] = 'land_area must be between 0.1 and 10,000 acres.'

    return (len(errors) == 0), errors


@csrf_exempt
@require_http_methods(["POST"])
def api_crop_recommendation_create_view(request):
    """
    Create a FarmerQuery + generate CropRecommendation.

    POST JSON body:
    {
      "location": "...",
      "soil_type": "loamy|sandy|...",
      "season": "kharif|rabi|...",
      "water_availability": "irrigated|semi_irrigated|...",
      "land_area": 2.5,
      "language": "en|hi"   // optional
    }
    """
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    is_valid, errors = _validate_api_payload(payload)
    if not is_valid:
        return JsonResponse({'error': 'Invalid payload.', 'fields': errors}, status=400)

    language = payload.get('language', 'en')
    land_area = float(payload.get('land_area'))

    location = payload.get('location', '').strip()
    soil_type = payload.get('soil_type')
    season = payload.get('season')
    water_availability = payload.get('water_availability')

    # Create query record first (so recommendation is linked)
    query = FarmerQuery(
        location=location,
        soil_type=soil_type,
        season=season,
        water_availability=water_availability,
        land_area=land_area,
        language=language,
    )
    if request.user.is_authenticated:
        query.user = request.user
    query.save()

    # Fetch weather and generate AI recommendation (Gemini may fall back to mock)
    weather_data = get_weather_data(location)
    query.weather_data = weather_data
    query.save(update_fields=['weather_data'])

    farmer_data = {
        'location': query.location,
        'soil_type': query.soil_type,
        'season': query.season,
        'water_availability': query.water_availability,
        'land_area': query.land_area,
    }

    ai_result = get_crop_recommendations(farmer_data, weather_data, query.language)

    recommendation = CropRecommendation.objects.create(
        query=query,
        summary=ai_result.get('summary', ''),
        crops_data=ai_result.get('crops', []),
        mandi_prices_data=ai_result.get('mandi_prices', []),
        calendar_data=ai_result.get('seasonal_calendar', []),
        farming_tips=ai_result.get('farming_tips', ''),
        ai_response_raw=json.dumps(ai_result, ensure_ascii=False),
    )

    return JsonResponse({
        'query_id': query.id,
        'recommendation_id': recommendation.id,
        'weather': weather_data,
        'recommendation': {
            'summary': recommendation.summary,
            'crops': recommendation.crops_data,
            'mandi_prices': recommendation.mandi_prices_data,
            'calendar': recommendation.calendar_data,
            'farming_tips': recommendation.farming_tips,
        }
    }, status=201)


@require_http_methods(["GET"])
def api_crop_recommendation_detail_view(request, query_id: int):
    """Fetch the saved recommendation for a given FarmerQuery id."""
    query = get_object_or_404(FarmerQuery, id=query_id)
    try:
        recommendation = query.recommendation
    except CropRecommendation.DoesNotExist:
        return JsonResponse({'error': 'Recommendation not found.'}, status=404)

    return JsonResponse({
        'query_id': query.id,
        'weather': query.weather_data,
        'recommendation': {
            'summary': recommendation.summary,
            'crops': recommendation.crops_data,
            'mandi_prices': recommendation.mandi_prices_data,
            'calendar': recommendation.calendar_data,
            'farming_tips': recommendation.farming_tips,
        }
    })


@require_http_methods(["GET"])
def api_crop_recommendation_report_view(request, query_id: int):
    """
    Download the PDF report for a query id (same content as web download button).
    """
    query = get_object_or_404(FarmerQuery, id=query_id)
    try:
        recommendation = query.recommendation
    except CropRecommendation.DoesNotExist:
        return HttpResponse("Recommendation not found", status=404)

    pdf_bytes = generate_pdf_report(query, recommendation)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"KisanAI_CropReport_{query.location.replace(' ', '_')}_{query.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
    return response
