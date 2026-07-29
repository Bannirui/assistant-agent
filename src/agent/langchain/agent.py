import json
import re

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool as lc_tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from ...config import settings
from ...router.order_router import router as order_router
from ...sop.engine import sop_engine
from ...calculator import calculator_registry
from ...rag.knowledge_base import knowledge_base
from ..base import BaseAgent
from ..prompts import SYSTEM_PROMPT


@lc_tool
def get_ticket(ticket_id: str) -> str:
    r"""
    获取工单详情
    :param ticket_id: 输入工单ID
    :return: 返回工单的完整信息
    """
    ticket = order_router.get_ticket(ticket_id)
    if ticket is None:
        return "工单未找到"
    return str(ticket.raw)


@lc_tool
def get_order(order_id: str) -> str:
    r"""
    :param order_id: 根据订单ID查询订单的完整信息
    :return: 获取订单详情
    """
    order = order_router.get_order(order_id)
    if order is None:
        return "订单未找到"
    return str(order)


@lc_tool
def get_customer(customer_id: str) -> str:
    r"""
    :param customer_id: 根据客户ID查询客户档案
    :return: 获取客户信息
    """
    customer = order_router.get_customer(customer_id)
    if customer is None:
        return "客户未找到"
    return str(customer)


@lc_tool
def search_sop(category: str, issue_type: str) -> str:
    r"""
    :param category: 客诉的产品品类
    :param issue_type: 客诉的问题类型
    :return: 标准操作流程SOP
    """
    result = sop_engine.search(category, issue_type)
    if not result["matched"]:
        return "未匹配到SOP"
    return str(result)


@lc_tool
def calculate_refund(category: str, order_id: str, customer_id: str) -> str:
    r"""
    计算退改费用
    :param category: 产品品类
    :param order_id: 订单
    :param customer_id: 客户
    :return: 返回精确的退费金额和计算明细
    """
    order = order_router.get_order(order_id)
    customer = order_router.get_customer(customer_id)
    if order is None or customer is None:
        return "订单或客户信息缺失，无法计算"
    result = calculator_registry.calculate(category, order, customer)
    return str({
        "payable": result.payable,
        "fee_rate": result.fee_rate,
        "fee_amount": result.fee_amount,
        "settle_amount": result.settle_amount,
        "detail": result.detail,
    })


@lc_tool
def search_knowledge(query: str) -> str:
    r"""
    搜索公司知识库
    当SOP未覆盖时 搜索相关文档/政策/规定
    :param query: 搜索的关键词 转换成向量到向量库找对应的文档
    :return:
    """
    results = knowledge_base.search(query)
    if not results:
        return "未找到相关知识"
    return str(results)


TOOLS = [get_ticket, get_order, get_customer, search_sop, calculate_refund, search_knowledge]


class LangChainAgent(BaseAgent):
    r"""
    LangChain Tools Agent
    使用langgraph.prebuilt.create_react_agent创建标准ReAct Agent
    框架自动管理工具调用循环、状态传递和对话历史
    """

    def __init__(self):
        llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
        # 预设好固定管线
        self.graph = create_react_agent(
            model=llm,
            tools=TOOLS,
            prompt=SYSTEM_PROMPT,
        )

    def analyze(self, ticket_id: str) -> dict:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"请分析工单: {ticket_id}"),
        ]

        result = self.graph.invoke(
            {"messages": messages},
            {"recursion_limit": settings.copilot_max_agent_iterations + 5},
        )

        final_messages = result.get("messages", [])
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                parsed = self._parse_output(msg.content)
                if parsed["analysis"]["intent"] not in ("解析失败",):
                    return parsed

        return {
            "analysis": {"intent": "解析失败", "emotion": "未知", "risk": "高"},
            "reply_template": "LangChain Agent 未产生有效输出",
            "suggested_actions": [],
            "references": {},
            "warnings": ["请人工查看原始输出"],
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
            "warnings": ["LangChain 输出解析失败，请人工查看原始输出"],
        }
