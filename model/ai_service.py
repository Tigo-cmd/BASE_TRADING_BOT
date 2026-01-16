import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import os
import json
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.groq_client = None
        self.active_provider = None
        
        # Use Groq as primary AI provider
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=groq_key)
                self.active_provider = "groq"
                print("✅ AIService: Using Groq")
            except Exception as e:
                print(f"⚠️ Groq init failed: {e}")
        
        self.is_active = self.active_provider is not None
        
        if not self.is_active:
            print("⚠️ AIService: No AI provider configured (add GROQ_API_KEY)")

    async def _call_ai(self, prompt: str) -> str:
        """Call Groq AI."""
        if self.groq_client:
            try:
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1024,
                )
                return completion.choices[0].message.content
            except Exception as e:
                return f"AI error: {str(e)}"
        
        return "AI unavailable (no provider configured)"

    async def analyze_token_security(self, token_data: dict) -> str:
        """AI-driven risk assessment of a token."""
        if not self.is_active:
            return "AI Analysis unavailable (API Key missing)."

        prompt = (
            f"Analyze the following token security data for a trading bot on Base network:\n"
            f"Token: {token_data.get('name')} ({token_data.get('symbol')})\n"
            f"Price: {token_data.get('price')}\n"
            f"Liquidity: {token_data.get('liquidity')}\n"
            f"Renounced: {token_data.get('renounced')}\n"
            f"Honeypot: {token_data.get('honeypot')}\n"
            f"\nProvide a concise 2-3 sentence summary of the risk level (Low, Medium, High) and why."
        )

        return await self._call_ai(prompt)

    async def detect_market_trends(self, market_snapshot: dict) -> str:
        """AI-driven trend detection across multiple tokens."""
        if not self.is_active:
            return "Market Trends unavailable (API Key missing)."

        snapshot_str = json.dumps(market_snapshot, indent=2)
        prompt = (
            f"Examine this snapshot of recent activity on the Base network:\n{snapshot_str}\n"
            f"\nIdentify the current dominant trend or narrative (e.g., Memecoins, AI Agents, DeFi 2.0). "
            f"Provide a short summary for a trader's dashboard."
        )

        return await self._call_ai(prompt)

    async def get_fun_fact(self) -> str:
        """Generate a random fun fact about trading, crypto, or Base network."""
        if not self.is_active:
            return "Fun Facts unavailable (API Key missing)."

        prompt = (
            "Generate ONE random fun fact about any of these topics: "
            "cryptocurrency trading, the Base network by Coinbase, DeFi, blockchain technology, "
            "or trading psychology. Make it interesting, educational, and under 100 words. "
            "Start directly with the fact, no intro needed."
        )

        return await self._call_ai(prompt)

# Singleton instance
_ai_service = None

def get_ai_service():
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
