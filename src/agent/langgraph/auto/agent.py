r"""
LangGraph自动ReAct Agent
使用langgraph.prebuilt.create_react_agent一行生成标准ReAct管线
"""

import json
import re

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from ....config import settings
from ...base import BaseAgent
from ...prompts import SYSTEM_PROMPT
from ...tools import TOOLS


class LangGraphAutoAgent(BaseAgent):
    r"""
    LangGraph自动ReAct Agent
    使用langgraph.prebuilt.create_react_agent自动构建agent+tools节点
    StateGraph的两个节点(agent/tools)+条件路由 框架一行搞定
    """

    def __init__(self):
        llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
        self.graph = create_react_agent(
            model=llm,
            tools=TOOLS,
            prompt=SYSTEM_PROMPT,
        )

    def analyze(self, ticket_id: str) -> dict:
        result = self.graph.invoke(
            {"messages": [HumanMessage(content=f"请分析工单: {ticket_id}")]},
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
            "reply_template": "LangGraph Auto Agent 未产生有效输出",
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
            "warnings": ["LangGraph Auto 输出解析失败，请人工查看原始输出"],
        }
