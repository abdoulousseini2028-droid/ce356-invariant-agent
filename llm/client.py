import os
from typing import List


class LLMClient:
    def __init__(self, provider: str = "gemini", model: str = None):
        self.provider = provider
        if model is None:
            model = {
                "anthropic": "claude-opus-4-20250514",
                "openai": "gpt-4o",
                "gemini": "gemini-2.0-flash",
            }.get(provider, "gemini-2.0-flash")
        self.model = model

    def generate(self, messages: List[dict]) -> str:
        if self.provider == "gemini":
            return self._call_gemini(messages)
        elif self.provider == "anthropic":
            return self._call_anthropic(messages)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _call_gemini(self, messages: List[dict]) -> str:
        import google.genai as genai
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        client = genai.Client(api_key=api_key)
        prompt = "\n\n".join(m["content"] for m in messages)
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text.strip()

    def _call_anthropic(self, messages: List[dict]) -> str:
        import anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        client = anthropic.Anthropic(api_key=api_key)
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]
        response = client.messages.create(
            model=self.model,
            max_tokens=512,
            system=system_msg,
            messages=user_messages,
        )
        return response.content[0].text.strip()


class MockLLMClient:
    def generate(self, messages: list) -> str:
        return '~(pc1 = "critical" /\\ pc2 = "critical")'
