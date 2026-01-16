import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.is_active = True
        else:
            print("⚠️ AIService: GEMINI_API_KEY not found in .env")
            self.is_active = False

    async def analyze_token_security(self, token_data: dict) -> str:
        """
        AI-driven risk assessment of a token.
        """
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

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Analysis error: {str(e)}"

    async def detect_market_trends(self, market_snapshot: list) -> str:
        """
        AI-driven trend detection across multiple tokens.
        """
        if not self.is_active:
            return "Market Trends unavailable (API Key missing)."

        snapshot_str = json.dumps(market_snapshot, indent=2)
        prompt = (
            f"Examine this snapshot of recent activity on the Base network:\n{snapshot_str}\n"
            f"\nIdentify the current dominant trend or narrative (e.g., Memecoins, AI Agents, DeFi 2.0). "
            f"Provide a short summary for a trader's dashboard."
        )

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Trend detection error: {str(e)}"

# Singleton instance
_ai_service = None

def get_ai_service():
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
