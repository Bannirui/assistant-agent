from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .llm.provider import registry as provider_registry, OpenAICompatibleProvider
from .sop.engine import sop_engine
from .sop.db import init_db
from .rag.knowledge_base import knowledge_base
from .rag.db.doc_store import get_doc_repo

# 路由模块
from .api.copilot import router as copilot_router
from .api.admin_sop import router as admin_sop_router
from .api.admin_knowledge import router as admin_knowledge_router

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

# 注册路由
# 业务接口
app.include_router(copilot_router)
# SOP管理接口
app.include_router(admin_sop_router)
# 知识库管理接口
app.include_router(admin_knowledge_router)


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
    # 初始化DB 知识库文档表
    get_doc_repo().init()

    # 从SOP表构建内存缓存
    sop_engine.load_all()

    # 初始化RAG检索器
    knowledge_base.initialize()
    status = knowledge_base.get_status()
    if status.get("points_count", 0) == 0:
        # 向量库表是空的 就尝试从数据库拉数据新建向量库
        docs = get_doc_repo().list_all()
        if docs:
            # 从数据库拿到知识库的文档
            knowledge_base.ingest_from_db()
