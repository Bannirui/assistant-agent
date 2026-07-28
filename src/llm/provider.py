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
    r"""
    抽象 定义规范
    现在流程的模型几乎都完全兼容OpenAI的协议格式 所以现在只有一个派生
    要是有其他格式的跟OpenAI不一样的 就继续派生就行
    """

    # 聊天模型
    @abstractmethod
    def chat(self, messages: list, tools: Optional[list] = None) -> "ChatResponse":
        ...

    # 向量模型
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


@dataclass
class ChatResponse:
    # LLM回复文字时候才会有值 就是回复的内容 "hello丁先生..."
    content: Optional[str]
    # LLM想调用工具时候才会有值 说明LLM想调用哪个工具 想怎么调用 [{"id":"call_1","function":{"name":"get_ticket","arguments":"{...}"}}]
    tool_calls: Optional[list] = None
    # OpenAI sdk的LLM原始返回
    raw_choice: Optional[object] = None


class OpenAICompatibleProvider(LLMProvider):
    r"""
    OpenAI格式的模型接入
    https://developers.openai.com/api/reference/overview
    现在几乎所有的模型都是完全兼容OpenAI的格式的 不管是聊天还是向量化 都直接接入就行
    """
    # 模型名称
    model: str
    # 模型地址
    base_url: str
    # 模型key
    api_key: str

    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self._client: Optional[OpenAI] = None

    def _get_client(self) -> OpenAI:
        r"""
        :return: OpenAI的sdk
        """
        if self._client is None:
            # 懒加载
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def chat(self, messages: list, tools: Optional[list] = None) -> ChatResponse:
        r"""
        调用OpenAI的sdk进行聊天
        :param messages: 对话历史 [{"role":"system","content":"xxx"},{"role":"user","content":"xxx"}]
        :param tools: 工具定义 告诉LLM调用哪些函数 [{"type":"function","function":{"name":"get_weather"},...]
        """
        client = self._get_client()
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            # 传了就带上让LLM调用 没传就纯聊天 告诉LLM有哪些工具可用
            kwargs["tools"] = tools

        response = client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        tool_calls = None
        if choice.message.tool_calls:
            # LLM想调用哪些工具
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
            # LLM回复了文字内容就把文字内容返回出去
            content=choice.message.content,
            # LLM说想调用工具就把想怎么调用工具返回出去
            tool_calls=tool_calls,
            raw_choice=choice,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        r"""
        OpenAI官网的示例 https://developers.openai.com/api/docs/guides/embeddings
        :param texts: 要转换成向量的文本
        :return: 每个文本对应的向量
        """
        client = self._get_client()
        response = client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [d.embedding for d in response.data]


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


def register_chat(self, provider: LLMProvider):
    r"""
    注册聊天模型
    """
    self._chat_provider = provider


def register_embed(self, provider: LLMProvider):
    r"""
    注册向量模型
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
