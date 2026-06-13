"""Memory-model clients for the MeMo-style inferential sensor."""
import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class MemoryModelClient(ABC):
    """Abstract oracle that answers targeted sub-queries about project facts."""

    @abstractmethod
    def ask(self, prompt: str, max_tokens: int = 300) -> str:
        """Return the model's response to a single prompt."""
        raise NotImplementedError

    def multi_turn(self, prompts: List[str], max_tokens: int = 300) -> List[str]:
        """Run a sequence of independent prompts and return their responses."""
        return [self.ask(p, max_tokens=max_tokens) for p in prompts]


class APIMemoryModelClient(MemoryModelClient):
    """Call an API LLM using the same key priority as backend/app.py."""

    def __init__(self, model: Optional[str] = None):
        self.provider = self._detect_provider()
        self.model = model or self._default_model()
        self._client: Optional[Any] = None

    @staticmethod
    def _detect_provider() -> str:
        if os.environ.get("OPENAI_API_KEY"):
            return "openai"
        if os.environ.get("XAI_API_KEY"):
            return "xai"
        if os.environ.get("GROQ_API_KEY"):
            return "groq"
        return ""

    def _default_model(self) -> str:
        defaults = {
            "openai": "gpt-4o-mini",
            "xai": "grok-3",
            "groq": "llama-3.3-70b-versatile",
        }
        return defaults.get(self.provider, "gpt-4o-mini")

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is required for APIMemoryModelClient") from exc

        if self.provider == "openai":
            self._client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        elif self.provider == "xai":
            self._client = OpenAI(
                api_key=os.environ.get("XAI_API_KEY"),
                base_url="https://api.x.ai/v1",
            )
        elif self.provider == "groq":
            self._client = OpenAI(api_key=os.environ.get("GROQ_API_KEY"))
        else:
            raise RuntimeError(
                "No API key found. Set OPENAI_API_KEY, XAI_API_KEY, or GROQ_API_KEY."
            )
        return self._client

    def ask(self, prompt: str, max_tokens: int = 300) -> str:
        client = self._get_client()
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            return f"[Error: LLM API call failed ({exc}).]"


class LocalMemoryModelClient(MemoryModelClient):
    """Use the existing local CPU LLM wrapper if it is available."""

    def ask(self, prompt: str, max_tokens: int = 300) -> str:
        try:
            from local_llm import is_local_llm_ready, local_generate
        except ImportError as exc:
            raise RuntimeError("local_llm module not available") from exc

        if not is_local_llm_ready():
            raise RuntimeError("Local LLM is not initialized.")
        return local_generate(prompt, max_new_tokens=max_tokens)


class FakeMemoryModelClient(MemoryModelClient):
    """Deterministic test client that returns queued or default responses."""

    def __init__(self, responses: Optional[List[str]] = None):
        self.responses = responses or []
        self.calls: List[str] = []
        self._index = 0

    def ask(self, prompt: str, max_tokens: int = 300) -> str:
        self.calls.append(prompt)
        if self._index < len(self.responses):
            response = self.responses[self._index]
            self._index += 1
            return response
        return json.dumps(
            {
                "contradiction": False,
                "confidence": 0.0,
                "type": "none",
                "explanation": "default fake response",
            }
        )
