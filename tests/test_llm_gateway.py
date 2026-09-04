import pytest
from orchestrator.llm import (
    LLMGateway,
    LLMRequestRequirement,
    BaseLLMProvider,
    AnthropicProvider,
    OpenAIProvider,
    GoogleGeminiProvider,
    LocalFallbackProvider,
    LLMGatewayResponse,
    LLMUsage,
)
from orchestrator.llm_client import LLMClient

class MockFailingProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__(name="failing_mock", model_name="fail_v1", api_key="valid_key")

    async def generate(self, messages, system_prompt=None):
        raise RuntimeError("Provider connection failed")

class MockWorkingProvider(BaseLLMProvider):
    def __init__(self, name="working_mock", model_name="work_v1"):
        super().__init__(name=name, model_name=model_name, api_key="valid_key", capabilities=["coding", "chat"])

    async def generate(self, messages, system_prompt=None):
        return LLMGatewayResponse(
            text="Mock response",
            provider_name=self.name,
            model_name=self.model_name,
            usage=LLMUsage(input_tokens=10, output_tokens=20, total_tokens=30, estimated_cost_usd=0.0001, latency_ms=15.0),
            is_fallback=False,
        )

@pytest.mark.asyncio
async def test_llm_provider_health_check():
    p1 = MockWorkingProvider()
    assert p1.check_health() is True

    p2 = MockWorkingProvider()
    p2.api_key = "invalid_key"
    assert p2.check_health() is False

@pytest.mark.asyncio
async def test_gateway_capability_routing():
    gw = LLMGateway()
    gw.providers = [
        LocalFallbackProvider(),
        MockWorkingProvider(name="coder", model_name="code_v1"),
    ]

    req = LLMRequestRequirement(task_type="coding")
    selected = gw.select_provider(req)
    assert selected.name == "coder"

@pytest.mark.asyncio
async def test_gateway_fallback_on_failure():
    gw = LLMGateway()
    gw.providers = [
        MockFailingProvider(),
        MockWorkingProvider(name="fallback_worker"),
    ]

    res = await gw.generate(messages=[{"role": "user", "content": "Hello"}])
    assert res.text == "Mock response"
    assert res.provider_name == "fallback_worker"
    assert res.is_fallback is True

@pytest.mark.asyncio
async def test_llm_client_backward_compatibility():
    client = LLMClient()
    res = await client.generate(messages=[{"role": "user", "content": "Test"}])
    assert res.text is not None
    assert res.model_used is not None
    assert res.latency_ms >= 0
