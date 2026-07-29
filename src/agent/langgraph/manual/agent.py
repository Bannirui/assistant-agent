r"""
LangGraph手动ReAct Agent
手动构建StateGraph 实现ReAct模式
将Agent工作流建模为有向图
节点=操作
边=状态转移
"""

import json
import re
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage

from ....config import settings
from ...base import BaseAgent
from ...prompts import SYSTEM_PROMPT, OUTPUT_FORMAT_REMINDER
from ...tools import TOOLS


class AgentState(TypedDict):
    r"""
    状态机核心数据结构
    定义Agent在任意时刻的完整快照
    messages使用add_messages reducer自动累加
    """
    messages: Annotated[list[BaseMessage], add_messages]
    iteration: int
    remaining_steps: int
    result: dict | None


class LangGraphManualAgent(BaseAgent):
    r"""
    LangGraph手动ReAct Agent
    状态图结构：
        START -> call_llm -> [条件路由]
                |-> tool_calls                |-> no_tool_calls
             execute_tools -> call_llm          final -> END

    与auto版本的区别
    - 手动定义StateGraph/节点/边/条件路由
    - 完全控制每一步做什么 没有框架的黑盒封装
    - 适合需要自定义节点逻辑/自定义状态字段的场景
    """

    def __init__(self):
        self.max_iterations = settings.copilot_max_agent_iterations
        llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
        self.llm_with_tools = llm.bind_tools(TOOLS)

        self.graph = self._build_graph()

    def _call_llm(self, state: AgentState) -> dict:
        r"""
        节点1
        调用LLM推理
        """
        response = self.llm_with_tools.invoke(state["messages"])
        return {
            "messages": [response],
            "remaining_steps": state["remaining_steps"],
        }

    def _execute_tools(self, state: AgentState) -> dict:
        r"""
        节点2
        执行工具调用
        """
        last_message = state["messages"][-1]
        tool_map = {t.name: t for t in TOOLS}

        tool_results = []
        for tc in last_message.tool_calls:
            tool_fn = tool_map.get(tc["name"])
            content = tool_fn.invoke(tc["args"]) if tool_fn else f"未知工具: {tc['name']}"
            tool_results.append(ToolMessage(content=content, tool_call_id=tc["id"]))

        return {
            "messages": tool_results,
            "iteration": state["iteration"] + 1,
            "remaining_steps": state["remaining_steps"] - 1,
        }

    def _should_continue(self, state: AgentState) -> str:
        r"""
        条件路由
        判断下一步是继续循环还是输出结果
        """
        last_message = state["messages"][-1]

        if state["iteration"] >= self.max_iterations:
            return "final"
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "execute_tools"
        return "final"

    def _final(self, state: AgentState) -> dict:
        r"""
        节点3
        生成最终JSON结果
        """
        messages = list(state["messages"])
        last_message = messages[-1]

        if isinstance(last_message, ToolMessage):
            messages.append(HumanMessage(content=OUTPUT_FORMAT_REMINDER))
            response = self.llm_with_tools.invoke(messages)
            result = _parse_output(response.content or "")
        elif isinstance(last_message, AIMessage):
            result = _parse_output(last_message.content or "")
        else:
            result = {
                "analysis": {"intent": "未知", "emotion": "未知", "risk": "高"},
                "reply_template": "LangGraph 手动状态机未产生有效输出",
                "suggested_actions": [],
                "references": {},
                "warnings": ["状态机异常终止"],
            }

        return {
            "messages": [AIMessage(content=json.dumps(result, ensure_ascii=False))],
            "result": result,
        }

    def _build_graph(self):
        r"""
        构建StateGraph
        """
        workflow = StateGraph(AgentState)

        workflow.add_node("call_llm", self._call_llm)
        workflow.add_node("execute_tools", self._execute_tools)
        workflow.add_node("final", self._final)

        workflow.set_entry_point("call_llm")

        workflow.add_conditional_edges(
            "call_llm",
            self._should_continue,
            {"execute_tools": "execute_tools", "final": "final"},
        )
        workflow.add_edge("execute_tools", "call_llm")
        workflow.add_edge("final", END)

        return workflow.compile()

    def analyze(self, ticket_id: str) -> dict:
        initial_state: AgentState = {
            "messages": [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"请分析工单: {ticket_id}"),
            ],
            "iteration": 0,
            "remaining_steps": self.max_iterations,
            "result": None,
        }

        final_state = self.graph.invoke(
            initial_state,
            {"recursion_limit": self.max_iterations + 5},
        )
        return final_state["result"] or {
            "analysis": {"intent": "超出迭代次数", "emotion": "未知", "risk": "高"},
            "reply_template": "抱歉，系统分析超时，请人工处理工单 {ticket_id}",
            "suggested_actions": [{"type": "escalate", "label": "升级主管"}],
            "references": {},
            "warnings": ["LangGraph 手动状态机达到最大迭代次数，请人工处理"],
        }


def _parse_output(content: str) -> dict:
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
        "warnings": ["LangGraph 手动输出解析失败，请人工查看原始输出"],
    }
