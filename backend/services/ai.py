import json
from openai import AsyncOpenAI
from core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class AIService:
    @staticmethod
    async def analyze_scan_results(scan_results: dict):
        """Send raw scan results to OpenAI for vulnerability analysis and scoring."""
        if not settings.OPENAI_API_KEY:
            return {
                "security_score": 50,
                "ai_analysis": "OpenAI API key not configured. Mock analysis provided.",
                "vulnerabilities": [
                    {
                        "title": "API Key Missing",
                        "severity": "Low",
                        "description": "The OpenAI API key is missing so deep analysis couldn't be performed.",
                        "recommendation": "Configure OPENAI_API_KEY in the .env file."
                    }
                ]
            }

        prompt = f"""
        You are an expert cybersecurity analyst. Analyze the following raw output from various security tools (Nmap, WhatWeb, Subfinder, Nikto).
        
        Raw Data:
        {json.dumps(scan_results, indent=2)}
        
        Provide your response exactly in the following JSON format:
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
            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a cybersecurity AI. Return only raw JSON without markup."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            result_json = json.loads(response.choices[0].message.content)
            return result_json
        except Exception as e:
            return {
                "security_score": 0,
                "ai_analysis": f"Error analyzing results with AI: {str(e)}",
                "vulnerabilities": []
            }
