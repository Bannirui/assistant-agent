r"""
OpenAI 兼容协议的模型接入

DeepSeek、通义千问、ChatGPT 都完全兼容 OpenAI 的 API 格式
https://platform.openai.com/docs/api-reference
"""

from typing import Optional
from openai import OpenAI

from ..provider import LLMProvider, ChatResponse


class OpenAICompatibleProvider(LLMProvider):
    r"""
    聊天和向量化都走 OpenAI 兼容 API
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
