import time
import httpx
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from orchestrator.llm.models import LLMGatewayResponse, LLMUsage
from orchestrator.observability import jarvis_logger

class BaseLLMProvider(ABC):
    """
    Abstract LLM provider contract providing generation, capabilities, and health checks.
    """
    def __init__(self, name: str, model_name: str, api_key: Optional[str] = None, capabilities: Optional[List[str]] = None):
        self.name = name
        self.model_name = model_name
        self.api_key = api_key
        self.capabilities = capabilities or ["chat"]
        self.is_healthy = True
        self.consecutive_failures = 0

    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> LLMGatewayResponse:
        pass

    def check_health(self) -> bool:
        if not self.api_key or self.api_key.startswith("YOUR_") or self.api_key.startswith("invalid_"):
            return False
        return self.is_healthy and self.consecutive_failures < 3

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "claude-3-5-sonnet-20241022"):
        super().__init__(name="anthropic", model_name=model_name, api_key=api_key, capabilities=["chat", "coding", "reasoning"])

    async def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> LLMGatewayResponse:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload: Dict[str, Any] = {"model": self.model_name, "messages": messages, "max_tokens": 1024}
            if system_prompt:
                payload["system"] = system_prompt

            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": self.api_key or "", "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("content", [])
            text = content[0].get("text", "") if content else ""
            usage_data = data.get("usage", {})
            in_tok = usage_data.get("input_tokens", 0)
            out_tok = usage_data.get("output_tokens", 0)
            tot_tok = in_tok + out_tok
            cost = (in_tok * 0.000003) + (out_tok * 0.000015)
            elapsed = (time.time() - start_time) * 1000

            return LLMGatewayResponse(
                text=text,
                provider_name=self.name,
                model_name=self.model_name,
                usage=LLMUsage(input_tokens=in_tok, output_tokens=out_tok, total_tokens=tot_tok, estimated_cost_usd=round(cost, 6), latency_ms=round(elapsed, 2)),
                is_fallback=False,
            )

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o"):
        super().__init__(name="openai", model_name=model_name, api_key=api_key, capabilities=["chat", "coding", "reasoning", "speed"])

    async def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> LLMGatewayResponse:
        start_time = time.time()
        formatted = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        formatted.extend(messages)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model_name, "messages": formatted, "max_tokens": 1024},
            )
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            text = choices[0]["message"]["content"] if choices else ""
            usage_data = data.get("usage", {})
            in_tok = usage_data.get("prompt_tokens", 0)
            out_tok = usage_data.get("completion_tokens", 0)
            tot_tok = usage_data.get("total_tokens", in_tok + out_tok)
            cost = (in_tok * 0.0000025) + (out_tok * 0.00001)
            elapsed = (time.time() - start_time) * 1000

            return LLMGatewayResponse(
                text=text,
                provider_name=self.name,
                model_name=self.model_name,
                usage=LLMUsage(input_tokens=in_tok, output_tokens=out_tok, total_tokens=tot_tok, estimated_cost_usd=round(cost, 6), latency_ms=round(elapsed, 2)),
                is_fallback=False,
            )

class GoogleGeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-pro"):
        super().__init__(name="google_gemini", model_name=model_name, api_key=api_key, capabilities=["chat", "reasoning", "speed"])

    async def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> LLMGatewayResponse:
        start_time = time.time()
        last_msg = messages[-1]["content"] if messages else ""
        prompt_text = f"{system_prompt}\n{last_msg}" if system_prompt else last_msg

        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            response = await client.post(url, json={"contents": [{"parts": [{"text": prompt_text}]}]})
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            text = candidates[0]["content"]["parts"][0]["text"] if candidates else ""
            elapsed = (time.time() - start_time) * 1000

            return LLMGatewayResponse(
                text=text,
                provider_name=self.name,
                model_name=self.model_name,
                usage=LLMUsage(input_tokens=len(prompt_text.split()), output_tokens=len(text.split()), total_tokens=len(prompt_text.split()) + len(text.split()), latency_ms=round(elapsed, 2)),
                is_fallback=False,
            )

class HuggingFaceProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt2"):
        super().__init__(name="huggingface", model_name=model_name, api_key=api_key, capabilities=["chat", "fallback"])

    async def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> LLMGatewayResponse:
        start_time = time.time()
        last_msg = messages[-1]["content"] if messages else ""
        prompt = f"{system_prompt}\n{last_msg}" if system_prompt else last_msg

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{self.model_name}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"inputs": prompt},
            )
            response.raise_for_status()
            data = response.json()
            gen_text = ""
            if isinstance(data, list) and data:
                gen_text = data[0].get("generated_text", "")
            elif isinstance(data, dict):
                gen_text = data.get("generated_text", "")
            elapsed = (time.time() - start_time) * 1000

            return LLMGatewayResponse(
                text=gen_text or "HuggingFace fallback response",
                provider_name=self.name,
                model_name=self.model_name,
                usage=LLMUsage(latency_ms=round(elapsed, 2)),
                is_fallback=True,
            )

class LocalFallbackProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__(name="local_fallback", model_name="local_rule_engine", api_key="local_key", capabilities=["chat", "fallback"])

    async def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> LLMGatewayResponse:
        return LLMGatewayResponse(
            text="I am operating in fallback mode. How can I assist you today?",
            provider_name=self.name,
            model_name=self.model_name,
            usage=LLMUsage(input_tokens=0, output_tokens=10, total_tokens=10, latency_ms=1.0),
            is_fallback=True,
        )
