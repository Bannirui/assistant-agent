r"""
Agent工厂
根据配置COPILOT_AGENT_TYPE创建对应的Agent实例
工厂模式+策略模式
"""

from ..config import settings
from .base import BaseAgent


def create_agent() -> BaseAgent:
    r"""
    Agent工厂方法
    :return: 根据配置文件中指定的Agent实现方式 创建对应类型的Agent实例
    """
    agent_type = settings.copilot_agent_type.lower()

    if agent_type == "native":
        from .native.agent import NativeAgent
        return NativeAgent()

    elif agent_type == "langchain":
        from .langchain.agent import LangChainAgent
        return LangChainAgent()

    elif agent_type == "langgraph":
        from .langgraph.agent import LangGraphAgent
        return LangGraphAgent()

    else:
        raise ValueError(
            f"未知的Agent类型: {agent_type}"
            f"可选: native/langchain/langgraph"
        )
