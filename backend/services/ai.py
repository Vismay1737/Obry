import json
import asyncio
from google import genai
from google.genai import types
from core.config import settings

class AIService:
    @staticmethod
    async def analyze_scan_results(scan_results: dict):
        """Send raw scan results to Gemini for vulnerability analysis and scoring."""
        if not settings.GEMINI_API_KEY:
            return {
                "security_score": 50,
                "ai_analysis": "Gemini API key not configured. Mock analysis provided.",
                "vulnerabilities": [
                    {
                        "title": "API Key Missing",
                        "severity": "Low",
                        "description": "The Gemini API key is missing so deep analysis couldn't be performed.",
                        "recommendation": "Configure GEMINI_API_KEY in the .env file."
                    }
                ]
            }

        prompt = f"""
You are an expert cybersecurity analyst. Analyze the following raw output from various security tools (Nmap, WhatWeb, Subfinder, Nikto).

Raw Data:
{json.dumps(scan_results, indent=2)}

Provide your response ONLY as a valid JSON object with no extra text or markdown, using this exact structure:
{{
    "security_score": <int from 0 to 100, where 100 is perfectly secure>,
    "ai_analysis": "<A summary paragraph explaining the overall security posture and key findings>",
    "vulnerabilities": [
        {{
            "title": "<Short title of the vulnerability>",
            "severity": "<Low, Medium, High, or Critical>",
            "description": "<Detailed explanation of the risk>",
            "recommendation": "<How to fix it>"
        }}
    ]
}}
"""

        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.0-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            result_json = json.loads(response.text)
            return result_json
        except Exception as e:
            return {
                "security_score": 50,
                "ai_analysis": f"AI analysis unavailable: {str(e)}",
                "vulnerabilities": []
            }
