"""Small provider contracts shared by agent implementations.

The project talks to OpenAI-compatible HTTP APIs through ``GiteeAIClient``.
Agents depend on this protocol instead of a concrete vendor so tests and future
providers can supply the same small interface without changing agent logic.
"""

from typing import Any, Iterator, Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Interface used by the agent layer."""

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
        timeout: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any] | Iterator[dict[str, Any]]:
        """Return an OpenAI-compatible chat completion response."""

    def simple_chat(
        self,
        user_message: str,
        system_message: str | None = None,
        timeout: int | None = None,
    ) -> str:
        """Return the text response for a single user message."""
