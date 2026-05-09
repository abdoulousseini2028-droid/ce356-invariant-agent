"""
llm/client.py
Model-agnostic LLM API wrapper.
Supports Gemini (default), Anthropic, and OpenAI — swap via provider arg.
"""

import os
from typing import List


class LLMClient:
    def __init__(self, provider: str = "gemini", model: str = None):
        self.provider = provider
        if model is None:
            model = {
                "anthropic": "claude-opus-4-20250514",
                "openai": "gpt-4o",
                "gemini": "gemini-flash-latest",
            }.get(provider, "gemini-flash-latest")
        self.model = model

    def generate(self, messages: List[dict]) -> str:
        if self.provider == "gemini":
            return self._call_gemini(messages)
        elif self.provider == "anthropic":
            return self._call_anthropic(messages)
        elif self.provider == "openai":
            return self._call_openai(messages)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    # ── providers ─────────────────────────────────────────────────────────

    def _call_gemini(self, messages: List[dict]) -> str:
        import google.genai as genai
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        client = genai.Client(api_key=api_key)
        
        # Build prompt from messages (google.genai expects simple string format)
        prompt_parts = []
        for msg in messages:
            prompt_parts.append(msg["content"])
        
        prompt = "\n\n".join(prompt_parts)
        
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={"max_output_tokens": 512}
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

    def _call_openai(self, messages: List[dict]) -> str:
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY", "")
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=self.model, messages=messages, max_tokens=512
        )
        return response.choices[0].message.content.strip()


class MockLLMClient:
    """Mock LLM that returns a hardcoded correct invariant for testing."""
    
    def __init__(self):
        pass
    
    def generate(self, messages: list) -> str:
        """Return a correct mutual exclusion invariant."""
        return '~(pc1 = "critical" /\\ pc2 = "critical")'
