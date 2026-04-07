import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from dotenv import load_dotenv
from google import genai


load_dotenv()

# client create kra
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def chat_page(request):
    return render(request, "chatbot.html")

# API
@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        try:
            
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                msg = data.get("message")
            else:
                msg = request.POST.get("message")

            if not msg:
                return JsonResponse({"reply": "Please enter a question"})

            # Gender-neutral prompt with correct Python multi-line string syntax
            prompt = f"""
            You are an agriculture expert helping Indian farmers.
            Answer in simple Hindi 
            Always use a gender-neutral and respectful greeting like 'नमस्ते किसान साथी!' or 'नमस्कार!'. 
            Do NOT use gender-specific terms like 'BHAI'.

            User: {msg}
            """

            
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt
            )
            
            reply = response.text if response.text else "No response"

            return JsonResponse({"reply": reply})

        except Exception as e:
            return JsonResponse({"reply": f"Error: {str(e)}"})

    return JsonResponse({"reply": "Invalid request"})