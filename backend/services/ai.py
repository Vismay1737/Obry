import logging
from core.config import settings
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

class AIService:
    _llm = None

    @classmethod
    def get_llm(cls):
        # Always use the API Key if available, regardless of USE_REAL_AI variable
        if not settings.NVIDIA_API_KEY:
             return "MOCK"

        if cls._llm is None:
            try:
                # Initialize the ChatNVIDIA client using the provided key
                cls._llm = ChatNVIDIA(
                    model="meta/llama-3.1-405b-instruct", 
                    api_key=settings.NVIDIA_API_KEY, 
                    temperature=0.2,
                    top_p=0.7,
                    max_tokens=1024
                )
                logger.info("Successfully connected to NVIDIA NIM endpoints.")
            except Exception as e:
                logger.error(f"Failed to initialize NVIDIA NIM model: {e}")
                cls._llm = "MOCK"
        return cls._llm

    @classmethod
    async def analyze_results_dict(cls, target: str, raw_results: dict) -> dict:
        import json
        llm = cls.get_llm()
        
        # We can increase the character limit now because the Llama 3.1 405B has a huge context window
        context = f"Target Website: {target}\n\n"
        for tool, output in raw_results.items():
            if not output: continue
            tool_summary = output[:2500] 
            context += f"--- {tool.upper()} OUTPUT ---\n{tool_summary}\n\n"

        if llm == "MOCK":
            return {
                "ai_analysis": f"[MOCK AI] The target {target} was scanned. Ports 80/443 visible.",
                "security_score": 85,
                "vulnerabilities": [{
                    "title": "Mock Open Network Services",
                    "severity": "medium",
                    "description": "Port scanning identified exposed services on the target machine.",
                    "recommendation": "Close unused ports and implement a strict firewall policy.",
                    "remediation_script": "#!/bin/bash\n# Example UFW Firewall Remediation\nsudo ufw default deny incoming\nsudo ufw allow 80/tcp\nsudo ufw allow 443/tcp\nsudo ufw enable"
                }]
            }

        try:
            prompt_content = f"""
            As a Senior Cybersecurity Analyst, analyze the following security scan results for the target {target}.
            
            {context}
            
            Return ONLY a valid JSON object containing exactly these fields (do not wrap in markdown ```json blocks, just return raw JSON):
            {{
                "ai_analysis": "A high-level executive summary of the security posture.",
                "security_score": integer (0 to 100) representing overall security health,
                "vulnerabilities": [
                    {{
                        "title": "Title of the vulnerability",
                        "severity": "critical" | "high" | "medium" | "low",
                        "description": "Detailed explanation of the flaw based on tool output",
                        "recommendation": "Step-by-step advice to fix the issue",
                        "remediation_script": "Exact bash, terraform, docker, nginx.conf, or kubectl command block to automatically fix this vulnerability. Leave as empty string if a script is impossible. Include comments in the script explaining the fix."
                    }}
                ]
            }}
            """

            messages = [
                SystemMessage(content="You are a professional cybersecurity auditor analyzing Kali Linux outputs. Output raw JSON ONLY. No yapping. No markdown formatting. Only raw JSON object."),
                HumanMessage(content=prompt_content)
            ]

            response = llm.invoke(messages)
            text_resp = response.content.strip()
            
            # Strip markdown backticks just in case the LLM disobeys
            if text_resp.startswith("```json"):
                text_resp = text_resp[7:]
            elif text_resp.startswith("```"):
                text_resp = text_resp[3:]
            if text_resp.endswith("```"):
                text_resp = text_resp[:-3]
                
            return json.loads(text_resp.strip())

        except Exception as e:
            logger.error(f"Error during AI JSON analysis: {e}")
            return {
                "ai_analysis": f"Error parsing AI response or calling NIM API: {str(e)}",
                "security_score": 0,
                "vulnerabilities": []
            }

    @classmethod
    async def consult(cls, target: str, raw_results: dict, user_query: str) -> str:
        llm = cls.get_llm()
        if llm == "MOCK" or not llm:
            return "AI Copilot is offline (NVIDIA API key required)."

        context = f"Target Website: {target}\n\n"
        for tool, output in raw_results.items():
            tool_summary = output[:2500] if output else "No output."
            context += f"--- {tool.upper()} OUTPUT ---\n{tool_summary}\n\n"

        prompt_content = f"""
        User Query: {user_query}
        
        Context regarding {target}:
        {context}
        
        Answer the user's question based strictly on the security context provided above.
        """

        messages = [
            SystemMessage(content="You are Orby, the Cybersecurity AI Copilot. Use the scan context to answer user questions about security risks."),
            HumanMessage(content=prompt_content)
        ]

        try:
            response = llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            return f"Consultation error: {str(e)}"
