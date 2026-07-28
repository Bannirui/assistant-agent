from typing import Optional

from ..config import settings
from ..llm.provider import registry as provider_registry
from ..router.order_router import router as order_router
from ..sop.engine import sop_engine
from ..calculator.engine import calculator_registry
from ..rag.knowledge_base import knowledge_base


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_ticket",
            "description": "获取工单详情。输入工单ID，返回工单的完整信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string", "description": "工单ID，格式如 TK-20240728-001"}
                },
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "获取订单详情。根据订单ID查询订单的完整信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "订单ID，格式如 ORD-F-001"}
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer",
            "description": "获取客户信息。根据客户ID查询客户档案。",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "客户ID，格式如 C10086"}
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_sop",
            "description": "搜索标准操作流程（SOP）。根据产品品类和问题类型查找对应的处理流程、补偿规则和话术模板。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "产品品类：机票、酒店、火车、打车"},
                    "issue_type": {"type": "string", "description": "问题类型，如：退差价、司机迟到、取消预订等"}
                },
                "required": ["category", "issue_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_refund",
            "description": "计算退改费用。用于需要精确计算的退票、退差价、取消预订等涉及金额的场景。输入订单和客户信息，返回精确的退费金额和计算明细。注意：所有涉及金额的输出必须使用此工具的结果，不得自行计算或估算。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "产品品类"},
                    "order_id": {"type": "string", "description": "订单ID"},
                    "customer_id": {"type": "string", "description": "客户ID"}
                },
                "required": ["category", "order_id", "customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "搜索公司知识库。当SOP未覆盖当前问题时，使用此工具搜索相关文档、政策、规定。返回最相关的文档片段。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询，用自然语言描述要查找的内容"}
                },
                "required": ["query"],
            },
        },
    },
]

SYSTEM_PROMPT = """你是一个旅游企业客服团队的 AI Copilot。你的职责是帮助客服人员快速处理客诉工单。

## 工作流程
1. 客服会输入一个工单号，你首先调用 get_ticket 获取工单详情
2. 根据工单内容，调用其他工具获取需要的信息（订单、客户、SOP、计算退费等）
3. 综合所有信息后，输出结构化的分析结果

## 重要规则
- **金额必须精确**：涉及退款、退费、补偿等金额输出时，必须使用 calculate_refund 工具获取精确结果，严禁自行计算或估算
- **SOP优先**：首先尝试 search_sop 找标准处理流程。如果返回"未匹配"，再使用 search_knowledge 搜索知识库
- **只读操作**：你只能查询和生成建议，不能执行任何写操作（退款、取消订单等）
- **不确定时宁可说不确定**：不要编造信息，不确定的数据必须标注"待确认"
- **先拉工单再行动**：任何时候都要先获取工单信息再决定下一步

## 输出格式
当你完成所有信息收集和分析后，输出以下JSON格式的结果：

```json
{
  "analysis": {
    "intent": "问题意图",
    "emotion": "客户情绪（正常/焦虑/愤怒）",
    "risk": "风险等级（低/中/高）及风险说明"
  },
  "reply_template": "给客服的建议回复话术，带{变量名}占位符",
  "suggested_actions": [
    {"type": "操作类型", "label": "按钮显示文字", "params": {}}
  ],
  "references": {
    "order_summary": "订单关键信息摘要",
    "customer_info": "客户关键信息",
    "policy_excerpt": "相关政策摘录"
  },
  "warnings": ["需要提醒客服的注意事项"]
}
```

## 回复话术原则
- 先道歉再解决
- 使用亲切但专业的语气
- 话术中的金额、日期等关键数据使用 {变量名} 占位符，最终由系统填充
- 如涉及补偿，明确指出补偿金额和来源（计算引擎/SOP/政策）"""

OUTPUT_FORMAT_REMINDER = """请基于以上所有信息，生成最终的分析结果。严格按照JSON格式输出，不要遗漏任何字段。
话术中的金额、日期等动态信息使用 {变量名} 格式的占位符。"""


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
                    import json
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
        import json
        import re

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
