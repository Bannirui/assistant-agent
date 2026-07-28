from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .llm.provider import registry as provider_registry, OpenAICompatibleProvider
from .agent.copilot_agent import agent
from .sop.engine import sop_engine
from .sop.db import init_db, import_from_yaml
from .rag.knowledge_base import knowledge_base

# 应用实例
app: FastAPI = FastAPI(title="Tourism CS Copilot", version="0.1.0")

# 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.on_event("startup")
async def startup() -> None:
    r"""
    资源初始化 处理完就开始接收客户端请求
    """
    # LLM模型注册 Agent对话用
    provider_registry.register_chat(
        OpenAICompatibleProvider(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
    )
    # 向量模型注册 RAG用
    provider_registry.register_embed(
        OpenAICompatibleProvider(
            base_url=settings.embed_base_url,
            api_key=settings.embed_api_key,
            model=settings.embed_model,
        )
    )
    # 初始化DB SOP表
    init_db()
    # 从SOP表构建内存缓存
    sop_engine.load_all()
    if len(sop_engine._sops) == 0:
        # 尝试把本地的SOP文件先导到数据库去
        import_from_yaml()
        sop_engine.load_all()

    # 初始化RAG检索器
    knowledge_base.initialize()
    status = knowledge_base.get_status()
    if status.get("points_count", 0) == 0:
        # 向量库为空 自动从知识库目录导入文档
        knowledge_base.ingest_directory()


@app.get("/api/copilot/status")
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


@app.post("/api/copilot/analyze", response_model=AnalyzeResponse)
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


@app.post("/admin/sop/reload")
async def reload_sop() -> dict[str, Any]:
    r"""
    从数据库重新加载SOP到内存
    """
    result: dict[str, Any] = sop_engine.reload()
    return result


@app.post("/admin/sop/import-yaml")
async def import_sop_yaml() -> dict[str, Any]:
    r"""
    从 YAML 文件导入 SOP 到数据库 (首次启动或手动触发)
    """
    count: int = import_from_yaml()
    sop_engine.load_all()
    return {"status": "imported", "count": count}


@app.post("/admin/knowledge/ingest")
async def ingest_knowledge() -> dict[str, Any]:
    r"""
    管理接口-知识库操作
    公司wiki文档更新后 重新索引到向量数据库
    """
    result: dict[str, Any] = knowledge_base.ingest_directory()
    return result


@app.get("/admin/knowledge/status")
async def knowledge_status() -> dict[str, Any]:
    r"""
    查看知识库索引了多少文档
    """
    return knowledge_base.get_status()
