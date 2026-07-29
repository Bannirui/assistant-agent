r"""
LangChain/LangGraph共用的工具定义

使用langchain_core的@tool装饰器 自动从函数签名+docstring
生成Pydantic schema供LLM tool calling使用
"""

from langchain_core.tools import tool as lc_tool

from ..router.order_router import router as order_router
from ..sop.engine import sop_engine
from ..calculator import calculator_registry
from ..rag.knowledge_base import knowledge_base


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
