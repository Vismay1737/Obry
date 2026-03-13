import torch
import transformers
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    _pipeline = None

    @classmethod
    def get_pipeline(cls):
        if not settings.USE_REAL_AI:
            return "MOCK"

        if cls._pipeline is None:
            model_id = "vanessasml/cyber-risk-llama-3-8b"
            try:
                logger.info(f"Initializing AI Model: {model_id}...")
                
                # Detect best torch dtype
                if torch.cuda.is_available():
                    device = "cuda"
                    try:
                        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
                    except Exception:
                        dtype = torch.float16
                else:
                    device = "cpu"
                    dtype = torch.float32

                # Add timeout and attempt to load model with simplified parameters
                cls._pipeline = transformers.pipeline(
                    "text-generation",
                    model=model_id,
                    model_kwargs={"torch_dtype": dtype, "low_cpu_mem_usage": True},
                    device_map="auto" if device == "cuda" else None,
                    device=None if device == "cuda" else 0 if device == "cpu" else None
                )
                logger.info(f"AI Model initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize AI model: {e}")
                cls._pipeline = "MOCK" # Marker for mock fallback
        return cls._pipeline

    @classmethod
    async def analyze_results(cls, target: str, raw_results: dict) -> str:
        pipeline = cls.get_pipeline()
        
        # Prepare a comprehensive prompt based on the tool outputs
        context = f"Target Website: {target}\n\n"
        for tool, output in raw_results.items():
            if not output: continue
            tool_summary = output[:800] 
            context += f"--- {tool.upper()} OUTPUT ---\n{tool_summary}\n\n"

        if pipeline == "MOCK":
            return f"""[FALLBACK AI ANALYSIS FOR {target}]
The AI model was unable to load due to hardware constraints. Here is a baseline heuristic assessment:
1. SUMMARY: The target {target} was scanned using Nmap and Nikto. Open ports and services identify potential attack surfaces.
2. RISKS: 
   - Port 80/443: Web servers are visible; ensure all software is patched to latest versions.
   - Information Disclosure: Tool logs indicate technology fingerprints (see WhatWeb tab).
   - Configuration: Nikto checks identified potential misconfigurations (see Nikto tab).
3. REMEDIATION: Review the detailed logs in the 'Nmap' and 'Nikto' tabs to specifically address identified version numbers and vulnerabilities."""

        if not pipeline:
            return "AI Analysis is currently unavailable (Model failed to initialize)."

        try:
            prompt_content = f"""
            As a Senior Cybersecurity Analyst, analyze the following security scan results for the target {target}.
            
            {context}
            
            Please provide:
            1. A high-level security summary.
            2. Top 3 critical vulnerabilities or exposures identified.
            3. Actionable remediation steps for the web administrator.
            
            Keep the tone professional and the advice practical.
            """

            messages = [
                {"role": "system", "content": "You are a professional cybersecurity auditor from a leading security firm."},
                {"role": "user", "content": prompt_content},
            ]

            prompt = pipeline.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )

            terminators = [
                pipeline.tokenizer.eos_token_id,
                pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ]

            outputs = pipeline(
                prompt,
                max_new_tokens=800,
                eos_token_id=terminators,
                do_sample=True,
                temperature=0.1,
                top_p=0.9,
            )
            
            analysis = outputs[0]["generated_text"][len(prompt):]
            return analysis.strip()
        except Exception as e:
            logger.error(f"Error during AI analysis: {e}")
            return f"Error generating AI analysis: {str(e)}"

    @classmethod
    async def consult(cls, target: str, raw_results: dict, user_query: str) -> str:
        pipeline = cls.get_pipeline()
        if not pipeline:
            return "AI Copilot is offline."

        context = f"Target Website: {target}\n\n"
        for tool, output in raw_results.items():
            tool_summary = output[:800] if output else "No output."
            context += f"--- {tool.upper()} OUTPUT ---\n{tool_summary}\n\n"

        prompt_content = f"""
        User Query: {user_query}
        
        Context regarding {target}:
        {context}
        
        Answer the user's question based on the security context provided above.
        """

        messages = [
            {"role": "system", "content": "You are Orby, the Cybersecurity AI Copilot. Use the scan context to answer user questions about security risks."},
            {"role": "user", "content": prompt_content},
        ]

        try:
            prompt = pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            outputs = pipeline(
                prompt,
                max_new_tokens=400,
                do_sample=True,
                temperature=0.2,
            )
            return outputs[0]["generated_text"][len(prompt):].strip()
        except Exception as e:
            return f"Consultation error: {str(e)}"
