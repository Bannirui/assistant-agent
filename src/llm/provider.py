from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class ChatMessage:
    role: str
    content: str
    tool_calls: Optional[list] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class LLMProvider(ABC):
    r"""
    抽象 定义规范
    具体的实现放在 providers/ 目录下
    """

    @abstractmethod
    def chat(self, messages: list, tools: Optional[list] = None) -> "ChatResponse":
        r"""
        聊天模型
        负责推理和生成 决定做什么和说什么
        """
        ...

    # 向量模型 负责
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        r"""
        向量模型 负责把文本内容转换成向量
        """
        ...


@dataclass
class ChatResponse:
    # LLM回复文字时候才会有值 就是回复的内容 "hello丁先生..."
    content: Optional[str]
    # LLM想调用工具时候才会有值 说明LLM想调用哪个工具 想怎么调用 [{"id":"call_1","function":{"name":"get_ticket","arguments":"{...}"}}]
    tool_calls: Optional[list] = None
    # OpenAI sdk的LLM原始返回
    raw_choice: Optional[object] = None


class ProviderRegistry:
    r"""
    注册聊天和向量模型 两个独立注册 解耦了厂商
    """
    # 聊天模型
    _chat_provider: Optional[LLMProvider]
    # 向量模型
    _embed_provider: Optional[LLMProvider]

    def __init__(self):
        self._chat_provider: Optional[LLMProvider] = None
        self._embed_provider: Optional[LLMProvider] = None

    def register_chat(self, provider: LLMProvider) -> None:
        r"""
        注册聊天模型
        """
        self._chat_provider = provider

    def register_embed(self, provider: LLMProvider) -> None:
        r"""
        注册向量模型
        :param provider: 向量模型 负责把文本内容转换到向量
        """
        self._embed_provider = provider

    @property
    def chat(self) -> LLMProvider:
        r"""
        外面当成属性用 拿到聊天模型
        """
        if self._chat_provider is None:
            raise RuntimeError("Chat provider not registered")
        return self._chat_provider

    @property
    def embed(self) -> LLMProvider:
        r"""
        外面当成属性用 拿到向量模型
        """
        if self._embed_provider is None:
            raise RuntimeError("Embedding provider not registered")
        return self._embed_provider


registry = ProviderRegistry()
