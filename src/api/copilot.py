r"""业务接口—客服使用"""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import settings
from ..agent.copilot_agent import agent
from ..sop.engine import sop_engine
from ..rag.knowledge_base import knowledge_base

router = APIRouter(prefix="/api/copilot", tags=["业务接口"])


# 请求体
class AnalyzeRequest(BaseModel):
    # 工单编号
    ticket_id: str


# 响应体
class AnalyzeResponse(BaseModel):
    # 工单编号
    ticket_id: str
    # {"intent":"退差","emotion":"愤怒","risk":"高"}
    analysis: dict[str, Any]
    # 建议回复用户的话术
    reply_template: str
    # [{"type":"refund"},{"label":"发起退款10元"}]
    suggested_actions: list[dict[str, Any]]
    # 订单快照 客户信息 政策原文
    references: dict[str, Any]
    # ["客户情绪激动","金额来自计算引擎"]
    warnings: list[str]


@router.get("/status")
async def get_status() -> dict[str, Any]:
    r"""
    健康检查 前端确认后端正常
    """
    return {
        "status": "running",
        # 加载了多少个SOP
        "sop_count": len(sop_engine._sops),
        # 向量数据库的状态
        "knowledge_base": knowledge_base.get_status(),
        "max_iterations": settings.copilot_max_agent_iterations,
    }


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_ticket(req: AnalyzeRequest) -> AnalyzeResponse:
    r"""
    分析客服录入的客诉工单
    触发整个Agent流水线
    """
    # Agent启动ReAct循环 调用各种Tool 返回结构化的结果
    result: dict[str, Any] = agent.analyze(req.ticket_id)
    return AnalyzeResponse(
        ticket_id=req.ticket_id,
        analysis=result.get("analysis", {}),
        reply_template=result.get("reply_template", ""),
        suggested_actions=result.get("suggested_actions", []),
        references=result.get("references", {}),
        warnings=result.get("warnings", []),
    )
