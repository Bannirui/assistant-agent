from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class ChatMessage:
    role: str
    content: str
    tool_calls: Optional[list] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: list, tools: Optional[list] = None) -> "ChatResponse":
        ...

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


@dataclass
class ChatResponse:
    content: Optional[str]
    tool_calls: Optional[list] = None
    raw_choice: Optional[object] = None


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self._client: Optional[OpenAI] = None

    def _get_client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def chat(self, messages: list, tools: Optional[list] = None) -> ChatResponse:
        client = self._get_client()
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        tool_calls = None
        if choice.message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                    "type": "function",
                }
                for tc in choice.message.tool_calls
            ]

        return ChatResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            raw_choice=choice,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        response = client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [d.embedding for d in response.data]


class ProviderRegistry:
    def __init__(self):
        self._chat_provider: Optional[LLMProvider] = None
        self._embed_provider: Optional[LLMProvider] = None

    def register_chat(self, provider: LLMProvider):
        self._chat_provider = provider

    def register_embed(self, provider: LLMProvider):
        self._embed_provider = provider

    @property
    def chat(self) -> LLMProvider:
        if self._chat_provider is None:
            raise RuntimeError("Chat provider not registered")
        return self._chat_provider

    @property
    def embed(self) -> LLMProvider:
        if self._embed_provider is None:
            raise RuntimeError("Embedding provider not registered")
        return self._embed_provider


registry = ProviderRegistry()
