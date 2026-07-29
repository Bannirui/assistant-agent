import json
import re

from ..config import settings
from ..llm.provider import registry as provider_registry
from ..router.order_router import router as order_router
from ..sop.engine import sop_engine
from ..calculator.engine import calculator_registry
from ..rag.knowledge_base import knowledge_base
from .prompts import SYSTEM_PROMPT, OUTPUT_FORMAT_REMINDER
from .tools import TOOLS


class CopilotAgent:
    def __init__(self):
        self.max_iterations = settings.copilot_max_agent_iterations

    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        if tool_name == "get_ticket":
            ticket = order_router.get_ticket(arguments["ticket_id"])
            if ticket is None:
                return "工单未找到"
            return str(ticket.raw)

        elif tool_name == "get_order":
            order = order_router.get_order(arguments["order_id"])
            if order is None:
                return "订单未找到"
            return str(order)

        elif tool_name == "get_customer":
            customer = order_router.get_customer(arguments["customer_id"])
            if customer is None:
                return "客户未找到"
            return str(customer)

        elif tool_name == "search_sop":
            result = sop_engine.search(arguments["category"], arguments["issue_type"])
            if not result["matched"]:
                return "未匹配到SOP"
            return str(result)

        elif tool_name == "calculate_refund":
            order = order_router.get_order(arguments["order_id"])
            customer = order_router.get_customer(arguments["customer_id"])
            if order is None or customer is None:
                return "订单或客户信息缺失，无法计算"
            result = calculator_registry.calculate(arguments["category"], order, customer)
            return str({
                "refundable": result.refundable,
                "fee_rate": result.fee_rate,
                "fee_amount": result.fee_amount,
                "refund_amount": result.refund_amount,
                "detail": result.detail,
            })

        elif tool_name == "search_knowledge":
            results = knowledge_base.search(arguments["query"])
            if not results:
                return "未找到相关知识"
            return str(results)

        return f"未知工具: {tool_name}"

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
