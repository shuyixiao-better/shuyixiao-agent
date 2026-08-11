from typing import Any

from shuyixiao_agent.agents.simple_agent import SimpleAgent
from shuyixiao_agent.providers import LLMProvider


class FakeProvider:
    def chat_completion(self, messages, **_: Any):
        return {"choices": [{"message": {"content": f"echo: {messages[-1]['content']}"}}]}

    def simple_chat(self, user_message, system_message=None, timeout=None):
        return f"echo: {user_message}"


def test_simple_agent_accepts_an_offline_provider() -> None:
    provider = FakeProvider()
    assert isinstance(provider, LLMProvider)
    assert SimpleAgent(llm_client=provider).chat("hello") == "echo: hello"
