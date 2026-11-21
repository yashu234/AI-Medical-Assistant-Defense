"""
LLM Client with OpenAI-compatible API Integration and Local Simulated Demo Mode.

Dual-Engine Architecture:
1. When OPENAI_API_KEY is supplied: Communicates with OpenAI-compatible endpoint.
2. When OPENAI_API_KEY is omitted: Runs entirely locally in simulated demo mode with
   deterministic, educational responses. Responses are visibly labeled as simulated.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for generating health education responses."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY.strip()
        self.base_url = settings.OPENAI_BASE_URL.rstrip("/")
        self.model = settings.OPENAI_MODEL
        self.is_simulated = settings.is_local_demo_mode

    async def generate_chat_completion(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> Dict[str, Any]:
        """
        Generates completion via OpenAI API if configured; otherwise uses Local Demo Mode.
        Returns dict with keys: {'content': str, 'is_simulated': bool, 'model': str}
        """
        # If no API key is configured, immediately invoke Local Demo Engine
        if self.is_simulated or not self.api_key:
            return self._generate_simulated_response(system_prompt, user_message)

        # Attempt API call to OpenAI-compatible endpoint
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return {
                    "content": content,
                    "is_simulated": False,
                    "model": self.model,
                }
        except Exception as e:
            logger.warning(
                f"OpenAI API call failed or timed out ({str(e)}). Falling back to Local Demo Mode."
            )
            simulated = self._generate_simulated_response(system_prompt, user_message)
            simulated["fallback_reason"] = f"API connection unavailable: {str(e)}"
            return simulated

    def _generate_simulated_response(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """
        Produces realistic, structured educational responses without calling any external LLM.
        Clearly tagged as simulated demo output.
        """
        prefix = "[Simulated Demo Mode - No API Key Configured]\n\n"
        query = user_message.lower()

        # Check domain
        if "cholesterol" in query or "ldl" in query or "hdl" in query:
            body = (
                "**Cholesterol and Cardiovascular Health Overview**\n\n"
                "• **LDL (Low-Density Lipoprotein):** Often referred to as 'bad' cholesterol. "
                "High levels of LDL can contribute to plaque buildup in arteries (atherosclerosis).\n"
                "• **HDL (High-Density Lipoprotein):** Often termed 'good' cholesterol because it helps "
                "scavenge excess cholesterol from the bloodstream and return it to the liver for excretion.\n"
                "• **Triglycerides:** A common form of fat in the blood stored from excess caloric intake.\n\n"
                "**General Lifestyle Considerations:**\n"
                "Diets rich in soluble fiber (oats, legumes), omega-3 fatty acids, and regular aerobic exercise "
                "support healthy lipid profiles. Any specific target ranges should be interpreted by your physician "
                "in context with your overall cardiovascular risk factors."
            )
        elif "blood pressure" in query or "hypertension" in query:
            body = (
                "**Blood Pressure Physiology & General Information**\n\n"
                "• **Systolic Pressure (Top Number):** Measures the pressure in arteries when the heart beats.\n"
                "• **Diastolic Pressure (Bottom Number):** Measures the pressure in arteries between beats.\n\n"
                "**General Clinical Categories (for adults):**\n"
                "- Normal: Less than 120/80 mmHg\n"
                "- Elevated: Systolic 120-129 and Diastolic <80 mmHg\n"
                "- Stage 1 Hypertension: Systolic 130-139 or Diastolic 80-89 mmHg\n\n"
                "**Key Note:** Single readings do not establish a diagnosis; medical professionals usually look "
                "at trends across multiple measurements taken at rest."
            )
        elif "vaccine" in query or "immunity" in query:
            body = (
                "**How Vaccines Interact With the Immune System**\n\n"
                "Vaccines train the immune system to recognize pathogens safely without causing the full illness:\n"
                "1. **Antigen Introduction:** An inactive part or blueprint (mRNA/protein) of the virus or bacteria is presented.\n"
                "2. **Antibody Production:** B-lymphocytes produce targeted antibodies against the specific antigen.\n"
                "3. **Memory Cells:** T and B memory cells persist, allowing the body to mount a swift defense if exposed in the future."
            )
        elif "sleep" in query or "insomnia" in query:
            body = (
                "**Principles of Sleep Hygiene**\n\n"
                "Consistent sleep habits play a vital role in cellular repair, cognitive performance, and hormonal regulation:\n"
                "• Maintain a consistent bedtime and waking schedule every day.\n"
                "• Limit exposure to blue-light emitting screens 60 minutes before bedtime.\n"
                "• Keep the bedroom environment cool, dark, and quiet.\n"
                "• Avoid caffeine and heavy meals within 4-6 hours of sleep."
            )
        else:
            body = (
                "**Health & Wellness Educational Guidance**\n\n"
                f"Regarding your query on: *'{user_message}'*:\n\n"
                "In general health education, maintaining consistent hydration, balanced nutrition, "
                "regular physical activity, and routine preventive checkups are core pillars of health.\n\n"
                "For any individual symptoms or personalized questions about medications, tests, or chronic conditions, "
                "consulting your primary healthcare provider is always the most appropriate step."
            )

        full_content = prefix + body
        return {
            "content": full_content,
            "is_simulated": True,
            "model": "local-simulated-engine",
        }


llm_client = LLMClient()
