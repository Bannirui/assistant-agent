import json
import re

from ...config import settings
from ...llm.provider import registry as provider_registry
from ..base import BaseAgent
from ..prompts import SYSTEM_PROMPT, OUTPUT_FORMAT_REMINDER
from .tools import TOOLS, tool_registry


class NativeAgent(BaseAgent):
    r"""
    原生Function Calling Agent
    手写ReAct循环 直接调用OpenAI兼容的LLM Tool Calling API
    工具注册使用@use_tool策略模式
    """

    def __init__(self):
        self.max_iterations = settings.copilot_max_agent_iterations

    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        return tool_registry.execute(tool_name, arguments=arguments)

    def analyze(self, ticket_id: str) -> dict:
        # OpenAI定义了role来标识消息是谁说的 优先级 system>developer>user>assistant(LLM模型的)
        # LLM模型
        provider = provider_registry.chat

        # Agent Loop 限制循环执行次数 每次问大模型的 相当于要保存上下文
        messages = [
            # system级的prompt
            {"role": "system", "content": SYSTEM_PROMPT},
            # user级的prompt
            {"role": "user", "content": f"请分析工单: {ticket_id}"},
        ]

        for iteration in range(self.max_iterations):
            # 告诉LLM哪些工具可用 看看它想调用哪个工具
            response = provider.chat(messages, tools=TOOLS)

            if response.tool_calls:
                # 在Agent Loop的时候每次的对话都要带上上一次的消息 是一次LLM想要访问那些工具 就把这些信息作为assistant级的prompt输入
                messages.append({
                    "role": "assistant",
                    "content": response.content or "",
                    "tool_calls": response.tool_calls,
                })

                for tc in response.tool_calls:
                    args = json.loads(tc["function"]["arguments"])
                    result = self._execute_tool(tc["function"]["name"], args)
                    # LLM模型想调用哪些工具 把对应的工具调用结果 用tool级的消息作为输入prompt再告诉模型
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    })
            else:
                messages.append({
                    "role": "user",
                    "content": OUTPUT_FORMAT_REMINDER,
                })
                final_response = provider.chat(messages)
                return self._parse_output(final_response.content or "")

        return {
            "analysis": {"intent": "超出迭代次数", "emotion": "未知", "risk": "高"},
            "reply_template": "抱歉，系统分析超时，请人工处理工单 {ticket_id}",
            "suggested_actions": [{"type": "escalate", "label": "升级主管"}],
            "references": {},
            "warnings": ["Agent达到最大迭代次数，请人工处理"],
        }

    def _parse_output(self, content: str) -> dict:
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return {
            "analysis": {"intent": "解析失败", "emotion": "未知", "risk": "高"},
            "reply_template": content,
            "suggested_actions": [],
            "references": {},
            "warnings": ["输出格式解析失败，请人工查看原始输出"],
        }
