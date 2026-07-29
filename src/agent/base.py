from abc import ABC, abstractmethod


class BaseAgent(ABC):
    r"""
    Agent的基类接口
    所有Agent实现 Native/LangChain/LangGraph都继承这个接口
    通过策略模式实现运行时热切换
    """

    @abstractmethod
    def analyze(self, ticket_id: str) -> dict:
        r"""
        分析客诉工单 执行完整的Agent工作流
        :param ticket_id: 工单编号 如TK-20240728-001
        :return: 结构化分析结果
        """
        ...
