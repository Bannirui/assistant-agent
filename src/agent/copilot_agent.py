import json
import re

from ..config import settings
from ..llm.provider import registry as provider_registry
from .prompts import SYSTEM_PROMPT, OUTPUT_FORMAT_REMINDER
from .tools import TOOLS, tool_registry


class CopilotAgent:
    def __init__(self):
        self.max_iterations = settings.copilot_max_agent_iterations

    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        r"""
        :param tool_name: 函数名
        :param arguments: 函数执行需要的实参
        :return: 函数的执行结果 函数不同 执行结果不同 所以都转成了字符串
        """
        # 从注册中心找到实现
        return tool_registry.execute(tool_name, arguments=arguments)

    def analyze(self, ticket_id: str) -> dict:
        provider = provider_registry.chat

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"请分析工单: {ticket_id}"},
        ]

        for iteration in range(self.max_iterations):
            response = provider.chat(messages, tools=TOOLS)

            if response.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": response.content or "",
                    "tool_calls": response.tool_calls,
                })

                for tc in response.tool_calls:
                    args = json.loads(tc["function"]["arguments"])
                    result = self._execute_tool(tc["function"]["name"], args)
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


agent = CopilotAgent()
