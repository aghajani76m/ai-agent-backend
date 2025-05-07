import openai
from app.core.config import settings

openai.api_key = settings.OPENAI_API_KEY

class AIClient:
    def chat(self, messages: list[dict]) -> dict:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=settings.TEMPERATURE,
        )
        usage = resp["usage"]  # tokens
        content = resp["choices"][0]["message"]["content"]
        return {"content": content, "usage": usage}