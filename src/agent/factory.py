r"""
Agent工厂
根据配置COPILOT_AGENT_TYPE创建对应的Agent实例

可选值
  native           - 手写ReAct循环 直接调OpenAI API 无框架依赖
  langchain        - langchain.agents.create_agent LangChain高层API
  langgraph-auto   - langgraph.prebuilt.create_react_agent 自动ReAct
  langgraph        - langgraph.graph.StateGraph 手动构建状态机 手动搭图
  langgraph-manual - langgraph.graph.StateGraph 手动构建状态机 手动搭图
"""

from ..config import settings
from .base import BaseAgent


def create_agent() -> BaseAgent:
    r"""
    Agent工厂方法
    :return: 根据配置文件中指定的Agent实现方式 创建对应类型的Agent实例
    """
    # 配置文件指定的agent实现方式
    agent_type = settings.copilot_agent_type.lower()
    # 原生
    if agent_type == "native":
        from .native.agent import NativeAgent
        return NativeAgent()
    # LangChain
    elif agent_type == "langchain":
        from .langchain.agent import LangChainAgent
        return LangChainAgent()
    # LangGraph自动
    elif agent_type == "langgraph-auto":
        from .langgraph.auto.agent import LangGraphAutoAgent
        return LangGraphAutoAgent()
    # LangGraph手动搭图
    elif agent_type in ("langgraph-manual", "langgraph"):
        from .langgraph.manual.agent import LangGraphManualAgent
        return LangGraphManualAgent()

    else:
        raise ValueError(
            f"未知的Agent类型: {agent_type}。"
            f"可选: native/langchain/langgraph-auto/langgraph-manual"
        )
