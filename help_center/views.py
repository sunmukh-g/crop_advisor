import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def help_center_view(request):
    """Renders the Help Center page with government schemes."""
    return render(request, "help_center/help_center.html")


@require_GET
def fetch_schemes_api(request):
    """
    API endpoint: Returns latest Indian government schemes for farmers
    using the Gemini API. Optional ?category= query param to filter.
    """
    category = request.GET.get("category", "all")

    category_filter = ""
    if category and category != "all":
        category_filter = f"Focus specifically on schemes related to: {category}."

    prompt = f"""
You are a knowledgeable advisor on Indian Government agricultural schemes.
List the 8 most important and latest Indian Government schemes specifically designed 
to help farmers in India (as of 2024-2025).
{category_filter}

For EACH scheme, provide the following in valid JSON format:
- name: Full official name of the scheme (string)
- hindi_name: Hindi name of the scheme if available (string, else empty string)
- ministry: Ministry or department responsible (string)
- description: A clear, farmer-friendly description in 2-3 sentences (string)
- benefits: Key financial/material benefits (string)
- eligibility: Who is eligible (string)
- how_to_apply: How farmers can apply or register (string)
- category: One of ["financial", "insurance", "irrigation", "soil", "technology", "credit", "market"] (string)
- icon: A single relevant emoji (string)
- launch_year: Year when the scheme was launched or last major update (string)
- official_link: Official government website link (string)
- is_active: Whether the scheme is currently active (boolean)

Return ONLY a valid JSON array with exactly 8 scheme objects. No markdown, no extra text.
Example format:
[{{"name": "...", "hindi_name": "...", "ministry": "...", "description": "...", "benefits": "...", "eligibility": "...", "how_to_apply": "...", "category": "financial", "icon": "💰", "launch_year": "2019", "official_link": "https://...", "is_active": true}}]
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text.strip()

        # Clean potential markdown code blocks
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        schemes = json.loads(raw_text)

        return JsonResponse({
            "success": True,
            "schemes": schemes,
            "total": len(schemes),
            "category": category
        })

    except json.JSONDecodeError as e:
        return JsonResponse({
            "success": False,
            "error": f"Failed to parse AI response: {str(e)}",
            "schemes": []
        }, status=500)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
            "schemes": []
        }, status=500)
