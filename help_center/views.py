import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def help_center_view(request):
    """Renders the Help Center page with government schemes."""
    return render(request, "help_center/help_center.html")


# ──────────────────────────────────────────────
#  FALLBACK DATA — Comprehensive list of schemes
# ──────────────────────────────────────────────

def _get_fallback_schemes(category="all"):
    """Returns a rich set of static government schemes if the API fails."""
    all_schemes = [
        {
            "name": "PM-KISAN Samman Nidhi (2026)",
            "hindi_name": "पीएम-किसान सम्मान निधि (2026)",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Direct income support scheme providing ₹6,000 per year in three equal installments directly to farmer families' bank accounts. Updated in 2026 with enhanced digital verification.",
            "benefits": "₹6,000/year (₹2,000 every 4 months) directly to bank accounts",
            "eligibility": "All landholding farmer families with cultivable land",
            "how_to_apply": "Register online at pmkisan.gov.in or visit nearest CSC center with Aadhaar, land records, and bank passbook",
            "documents_required": "Aadhaar Card, Land Records, Bank Passbook, Mobile Number",
            "category": "financial",
            "icon": "💰",
            "launch_year": "2019 (Updated 2026)",
            "official_link": "https://pmkisan.gov.in",
            "is_active": True
        },
        {
            "name": "PMFBY — Pradhan Mantri Fasal Bima Yojana 2.0",
            "hindi_name": "प्रधानमंत्री फसल बीमा योजना 2.0",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "India's flagship crop insurance scheme protecting farmers against losses from natural calamities, pests, and diseases. Premium is just 2% for Kharif, 1.5% for Rabi, and 5% for commercial crops.",
            "benefits": "Full crop loss coverage; Low premium (2% Kharif, 1.5% Rabi); Govt pays remaining premium",
            "eligibility": "All farmers growing notified crops in notified areas (both loanee and non-loanee)",
            "how_to_apply": "Apply through banks, CSCs, insurance agents, or directly on pmfby.gov.in before sowing deadline",
            "documents_required": "Aadhaar, Land Records, Bank Account, Sowing Certificate",
            "category": "insurance",
            "icon": "🛡️",
            "launch_year": "2016 (Updated 2026)",
            "official_link": "https://pmfby.gov.in",
            "is_active": True
        },
        {
            "name": "Kisan Credit Card (KCC Plus)",
            "hindi_name": "किसान क्रेडिट कार्ड (केसीसी प्लस)",
            "ministry": "Ministry of Finance / NABARD",
            "description": "Provides affordable short-term credit to farmers for crop production, post-harvest, and allied activities. Interest rate is just 4% per annum (7% minus 3% interest subvention).",
            "benefits": "Loans up to ₹3 Lakh at 4% interest; Crop insurance coverage included; Revolving credit facility",
            "eligibility": "All farmers, tenant farmers, sharecroppers, and self-help groups",
            "how_to_apply": "Apply at nearest commercial bank, cooperative bank, or Regional Rural Bank with land documents",
            "documents_required": "Aadhaar, Land Records/Lease Agreement, Passport Photo, Bank Account",
            "category": "credit",
            "icon": "💳",
            "launch_year": "1998 (Updated 2026)",
            "official_link": "https://www.nabard.org",
            "is_active": True
        },
        {
            "name": "PMKSY — Pradhan Mantri Krishi Sinchayee Yojana",
            "hindi_name": "प्रधानमंत्री कृषि सिंचाई योजना",
            "ministry": "Ministry of Jal Shakti / Ministry of Agriculture",
            "description": "Aims to expand cultivated area under irrigation, improve water use efficiency through 'Per Drop More Crop'. Provides subsidies for drip irrigation, sprinkler systems, and micro-irrigation.",
            "benefits": "55% subsidy for small/marginal farmers; 45% for others on micro-irrigation systems",
            "eligibility": "Any farmer with cultivable land; Priority to small & marginal farmers",
            "how_to_apply": "Apply through State Agriculture/Horticulture Department or online at pmksy.gov.in",
            "documents_required": "Aadhaar, Land Records, Bank Account, Quotation from equipment supplier",
            "category": "irrigation",
            "icon": "💧",
            "launch_year": "2015 (Updated 2026)",
            "official_link": "https://pmksy.gov.in",
            "is_active": True
        },
        {
            "name": "Soil Health Card Scheme",
            "hindi_name": "मृदा स्वास्थ्य कार्ड योजना",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Provides soil health cards to farmers with crop-wise recommendations for nutrients and fertilizers. Helps optimize fertilizer usage to reduce cost and improve yields.",
            "benefits": "Free soil testing; Crop-wise fertilizer recommendations; Reduces input cost by 20-30%",
            "eligibility": "All farmers across India",
            "how_to_apply": "Contact nearest Krishi Vigyan Kendra (KVK) or Agriculture Department for free soil testing",
            "documents_required": "Aadhaar, Land Record, Soil Sample",
            "category": "soil",
            "icon": "🌱",
            "launch_year": "2015 (Updated 2026)",
            "official_link": "https://soilhealth.dac.gov.in",
            "is_active": True
        },
        {
            "name": "Digital Agriculture Mission 2.0",
            "hindi_name": "डिजिटल कृषि मिशन 2.0",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Promotes AI, drones, IoT, and satellite technology in farming. Provides training and subsidies for drone-based spraying, precision agriculture, and smart farming tools.",
            "benefits": "Up to 100% subsidy on drones for SC/ST farmers; 50% for others; Free digital training",
            "eligibility": "All farmers, FPOs, and Custom Hiring Centers",
            "how_to_apply": "Apply through State Agriculture Department or authorized drone service providers",
            "documents_required": "Aadhaar, Land Records, FPO Registration (if applicable)",
            "category": "technology",
            "icon": "📱",
            "launch_year": "2021 (Updated 2026)",
            "official_link": "https://agricoop.nic.in",
            "is_active": True
        },
        {
            "name": "e-NAM — National Agriculture Market",
            "hindi_name": "ई-नाम (राष्ट्रीय कृषि बाजार)",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Pan-India electronic trading portal connecting 1,361+ APMC mandis. Enables farmers to sell produce online to buyers across the country for better price discovery.",
            "benefits": "Direct access to nationwide buyers; Transparent pricing; Reduced middlemen; Online payment",
            "eligibility": "All farmers with produce to sell",
            "how_to_apply": "Register on enam.gov.in portal or at nearest e-NAM enabled mandi",
            "documents_required": "Aadhaar, Bank Account, Mobile Number",
            "category": "market",
            "icon": "🏪",
            "launch_year": "2016 (Updated 2026)",
            "official_link": "https://enam.gov.in",
            "is_active": True
        },
        {
            "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
            "hindi_name": "परंपरागत कृषि विकास योजना (PKVY)",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Promotes organic farming through cluster-based approach. Provides financial support for organic inputs, certification (PGS), and marketing. Covers 50,000 clusters.",
            "benefits": "₹50,000 per hectare over 3 years; Organic certification support; Market linkage",
            "eligibility": "Groups of 50+ farmers forming a cluster of at least 50 acres",
            "how_to_apply": "Apply through State Agriculture Department or District Agriculture Officer",
            "documents_required": "Aadhaar, Land Records, Group Formation Documents",
            "category": "soil",
            "icon": "🌿",
            "launch_year": "2015 (Updated 2026)",
            "official_link": "https://pgsindia-ncof.gov.in",
            "is_active": True
        },
        {
            "name": "PM Kisan Maan-Dhan Yojana (Pension Scheme)",
            "hindi_name": "पीएम किसान मानधन योजना (पेंशन)",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Voluntary pension scheme for small and marginal farmers. After age 60, farmers receive a guaranteed monthly pension of ₹3,000. Government matches the farmer's contribution.",
            "benefits": "₹3,000/month pension after age 60; Government contributes 50% of premium",
            "eligibility": "Small and marginal farmers aged 18-40 with less than 2 hectares of land",
            "how_to_apply": "Register at CSC center or pmkmy.gov.in with Aadhaar and bank details",
            "documents_required": "Aadhaar, Land Records, Bank/Savings Account, Age Proof",
            "category": "financial",
            "icon": "🧓",
            "launch_year": "2019",
            "official_link": "https://pmkmy.gov.in",
            "is_active": True
        },
        {
            "name": "Agriculture Infrastructure Fund (AIF)",
            "hindi_name": "कृषि अवसंरचना कोष",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Provides medium-to-long term credit facility for building post-harvest management infrastructure like cold storage, warehouses, and processing units. ₹1 Lakh Crore fund.",
            "benefits": "3% interest subvention; ₹2 Crore credit guarantee per project; Loans up to ₹2 Crore",
            "eligibility": "Farmers, FPOs, PACS, Agri-entrepreneurs, Startups, and SHGs",
            "how_to_apply": "Apply online at agriinfra.dac.gov.in through any scheduled bank",
            "documents_required": "Business Plan, Land/Lease Documents, Bank Account, Identity Proof",
            "category": "credit",
            "icon": "🏗️",
            "launch_year": "2020 (Updated 2026)",
            "official_link": "https://agriinfra.dac.gov.in",
            "is_active": True
        },
        {
            "name": "National Mission on Sustainable Agriculture (NMSA)",
            "hindi_name": "राष्ट्रीय सतत कृषि मिशन (NMSA)",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Makes agriculture more productive, sustainable, and climate-resilient. Promotes rainfed area development, soil health management, and water use efficiency.",
            "benefits": "Subsidy for rain water harvesting; Organic manure units; Climate-resilient seeds",
            "eligibility": "All farmers, especially in rainfed and vulnerable areas",
            "how_to_apply": "Contact District Agriculture Office or State NMSA cell",
            "documents_required": "Aadhaar, Land Records, Application Form from Agriculture Office",
            "category": "soil",
            "icon": "🌍",
            "launch_year": "2014 (Updated 2026)",
            "official_link": "https://nmsa.dac.gov.in",
            "is_active": True
        },
        {
            "name": "Sub-Mission on Agricultural Mechanization (SMAM)",
            "hindi_name": "कृषि मशीनीकरण पर उप-मिशन (SMAM)",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Promotes farm mechanization by providing subsidies on purchase of agricultural equipment. Includes Custom Hiring Centers and Farm Machinery Banks for rental access.",
            "benefits": "40-50% subsidy on farm machinery; Support for Custom Hiring Centers (CHCs)",
            "eligibility": "All farmers; Priority to SC/ST, women, and small/marginal farmers",
            "how_to_apply": "Apply on agrimachinery.nic.in or through District Agriculture Office",
            "documents_required": "Aadhaar, Land Records, Bank Account, Equipment Quotation",
            "category": "technology",
            "icon": "🚜",
            "launch_year": "2014 (Updated 2026)",
            "official_link": "https://agrimachinery.nic.in",
            "is_active": True
        },
        {
            "name": "Rashtriya Krishi Vikas Yojana (RKVY-RAFTAAR)",
            "hindi_name": "राष्ट्रीय कृषि विकास योजना - रफ्तार",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Incentivizes states to increase public investment in agriculture. Supports agri-startups, innovation, and integrated farming with flexible funding.",
            "benefits": "Funding for agri-startups up to ₹25 Lakhs; State-level agricultural projects support",
            "eligibility": "Agri-startups, FPOs, and State government agricultural programs",
            "how_to_apply": "Apply through State Agriculture Department or RKVY-RAFTAAR portal",
            "documents_required": "Business Plan, Registration Documents, Identity Proof, Bank Account",
            "category": "financial",
            "icon": "🚀",
            "launch_year": "2007 (Updated 2026)",
            "official_link": "https://rkvy.nic.in",
            "is_active": True
        },
        {
            "name": "National Horticulture Mission (NHM)",
            "hindi_name": "राष्ट्रीय बागवानी मिशन (NHM)",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Promotes holistic growth of horticulture sector including fruits, vegetables, flowers, spices, and plantation crops through area expansion and post-harvest management.",
            "benefits": "Subsidy up to 50% for new orchards/gardens; Support for greenhouses and shade nets",
            "eligibility": "All farmers engaged in or willing to start horticulture",
            "how_to_apply": "Apply through State Horticulture Department or District Horticulture Officer",
            "documents_required": "Aadhaar, Land Records, Bank Account, Project Report",
            "category": "soil",
            "icon": "🍎",
            "launch_year": "2005 (Updated 2026)",
            "official_link": "https://nhm.nic.in",
            "is_active": True
        },
        {
            "name": "Pradhan Mantri Annadata Aay SanraksHan Abhiyan (PM-AASHA)",
            "hindi_name": "प्रधानमंत्री अन्नदाता आय संरक्षण अभियान",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "description": "Umbrella scheme to ensure MSP to farmers. Includes Price Support Scheme (PSS), Price Deficiency Payment Scheme (PDPS), and Private Procurement Stockist Scheme.",
            "benefits": "Guaranteed MSP procurement; Price deficiency compensation; Market price stabilization",
            "eligibility": "All farmers selling notified crops at or below MSP",
            "how_to_apply": "Sell at designated procurement centers during procurement window; Register on state portal",
            "documents_required": "Aadhaar, Land Records, Bank Account, Crop Details",
            "category": "market",
            "icon": "📊",
            "launch_year": "2018 (Updated 2026)",
            "official_link": "https://agricoop.nic.in",
            "is_active": True
        },
    ]

    if category and category != "all":
        filtered = [s for s in all_schemes if s["category"] == category]
        return filtered if filtered else all_schemes
    return all_schemes


# ──────────────────────────────────────────────
#  API: Fetch ALL Government Schemes via Gemini
# ──────────────────────────────────────────────

@require_GET
def fetch_schemes_api(request):
    """
    API endpoint: Returns latest Indian government schemes for farmers
    using the Gemini API. Optional ?category= and ?state= query params.
    """
    category = request.GET.get("category", "all")
    state = request.GET.get("state", "").strip()

    category_filter = ""
    if category and category != "all":
        category_filter = f"Focus specifically on schemes related to: {category}."

    state_filter = ""
    if state:
        state_filter = f"""
Also include 2-3 state-specific schemes available in {state} (e.g., state agriculture subsidies, 
state irrigation programs, state crop insurance top-ups specific to {state}).
"""

    prompt = f"""
You are an expert advisor on Indian Government agricultural schemes and policies.

List 15 of the most important, currently active Indian Government schemes specifically designed 
to help farmers in India (as of April 2026). Include BOTH Central Government schemes AND 
State-level schemes if a state is mentioned.
{category_filter}
{state_filter}

Include a diverse mix covering these categories:
- financial (direct income support, subsidies)
- insurance (crop insurance, livestock insurance)  
- irrigation (water management, micro-irrigation)
- soil (soil health, organic farming, horticulture)
- technology (digital agriculture, drones, precision farming)
- credit (loans, credit cards, infrastructure funding)
- market (market access, MSP, e-trading)

For EACH scheme, provide the following in valid JSON format:
- name: Full official name of the scheme (string)
- hindi_name: Hindi name of the scheme (string, empty string if unknown)
- ministry: Ministry or department responsible (string)
- description: A clear, farmer-friendly description in 2-3 sentences (string)
- benefits: Key financial/material benefits — be specific with amounts where possible (string)
- eligibility: Who is eligible — be specific (string)
- how_to_apply: Step-by-step application method (string)
- documents_required: Key documents needed to apply (string)
- category: One of ["financial", "insurance", "irrigation", "soil", "technology", "credit", "market"] (string)
- icon: A single relevant emoji (string)
- launch_year: Year launched or last major update (string)
- official_link: Official government website URL (string)
- is_active: Whether the scheme is currently active in 2026 (boolean)

Return ONLY a valid JSON array with exactly 15 scheme objects. No markdown, no extra text, no explanation.
Example: [{{"name": "...", "hindi_name": "...", "ministry": "...", "description": "...", "benefits": "...", "eligibility": "...", "how_to_apply": "...", "documents_required": "...", "category": "financial", "icon": "💰", "launch_year": "2019", "official_link": "https://...", "is_active": true}}]
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

        # Filter by category client-side if needed
        if category and category != "all":
            filtered = [s for s in schemes if s.get("category") == category]
            if filtered:
                schemes = filtered

        return JsonResponse({
            "success": True,
            "schemes": schemes,
            "total": len(schemes),
            "category": category,
            "state": state,
            "source": "gemini-ai"
        })

    except json.JSONDecodeError as e:
        print(f"Gemini API Decode Error: {str(e)}")
        schemes = _get_fallback_schemes(category)
        return JsonResponse({
            "success": True,
            "schemes": schemes,
            "total": len(schemes),
            "category": category,
            "source": "fallback"
        })
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        schemes = _get_fallback_schemes(category)
        return JsonResponse({
            "success": True,
            "schemes": schemes,
            "total": len(schemes),
            "category": category,
            "source": "fallback"
        })


# ──────────────────────────────────────────────
#  API: Get detailed info about a specific scheme
# ──────────────────────────────────────────────

@require_GET
def scheme_detail_api(request):
    """
    API endpoint: Returns detailed AI-generated info about a specific scheme.
    Query param: ?name=PM-KISAN
    """
    scheme_name = request.GET.get("name", "").strip()
    if not scheme_name:
        return JsonResponse({"success": False, "error": "Scheme name is required"}, status=400)

    prompt = f"""
You are an expert on Indian government agricultural schemes. Provide a comprehensive, 
farmer-friendly guide about: "{scheme_name}"

Respond in valid JSON format with these fields:
- name: Full official name (string)
- hindi_name: Hindi name (string)
- ministry: Responsible ministry (string)
- description: Detailed 4-5 sentence description (string)
- benefits: Detailed list of all benefits with specific amounts (string)
- eligibility: Detailed eligibility criteria (string)
- how_to_apply: Step-by-step application process (string)
- documents_required: Complete list of required documents (string)
- helpline: Toll-free helpline number if available (string)
- official_link: Official website URL (string)
- important_dates: Any upcoming deadlines or registration windows in 2026 (string)
- faqs: Array of 3 common questions and answers, each as {{"q": "...", "a": "..."}}
- tips: 3 practical tips for farmers applying to this scheme (string)

Return ONLY valid JSON. No markdown, no extra text.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        detail = json.loads(raw_text)
        return JsonResponse({"success": True, "detail": detail})

    except Exception as e:
        print(f"Scheme Detail API Error: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": "Could not fetch scheme details. Please try again."
        })


# ──────────────────────────────────────────────
#  API: AI Chat specifically for scheme queries
# ──────────────────────────────────────────────

@csrf_exempt
def scheme_chat_api(request):
    """
    Dedicated AI chat endpoint for government scheme queries.
    More focused than the general chatbot.
    """
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request method"}, status=405)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            msg = data.get("message", "").strip()
        else:
            msg = request.POST.get("message", "").strip()

        if not msg:
            return JsonResponse({"reply": "Please enter a question about government schemes."})

        prompt = f"""
You are "Kisan AI", a specialized Indian government scheme advisor for farmers.
You have deep knowledge of ALL central and state-level agricultural schemes in India as of 2026.

GUIDELINES:
- Answer in simple, farmer-friendly language
- Always mention specific scheme names, amounts, and eligibility when relevant
- If the farmer asks about a specific scheme, give complete details including how to apply
- If asking about eligibility, give a clear YES/NO answer first, then explain
- Include official website links where applicable
- If the question is about a state-specific scheme, provide state-level information
- Use bullet points for clarity
- Keep response concise but comprehensive (max 300 words)
- If you don't know something, say so honestly

Farmer's question: {msg}

Respond naturally as a helpful agricultural advisor. Do NOT use JSON format for this response.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        reply = response.text if response.text else "Sorry, I couldn't process that. Please try again."
        return JsonResponse({"reply": reply, "success": True})

    except Exception as e:
        print(f"Scheme Chat API Error: {str(e)}")
        return JsonResponse({
            "reply": "⚠️ I'm having trouble connecting right now. Please try again in a moment.",
            "success": False
        })
