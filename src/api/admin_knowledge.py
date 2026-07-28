r"""知识库管理接口 — 运营管理后台使用"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..rag.knowledge_base import knowledge_base
from ..rag.db.doc_store import get_doc_repo, KnowledgeDoc

router = APIRouter(prefix="/admin/knowledge", tags=["知识库管理"])


# 知识库文档请求体
class KnowledgeDocRequest(BaseModel):
    # 文档标题
    title: str
    # 文档内容 (Markdown)
    content: str
    # 来源 confluence/语雀/手动上传
    source: str = ""


@router.get("/docs")
async def list_docs() -> list[dict[str, Any]]:
    r"""列出所有知识库文档"""
    docs = get_doc_repo().list_all()
    return [{"id": d.id, "title": d.title, "source": d.source, "status": d.status} for d in docs]


@router.get("/docs/{doc_id}")
async def get_doc(doc_id: int) -> dict[str, Any]:
    r"""查看单个文档详情"""
    doc = get_doc_repo().get(doc_id)
    if not doc:
        raise HTTPException(404, f"Document {doc_id} not found")
    return {"id": doc.id, "title": doc.title, "content": doc.content, "source": doc.source}


@router.post("/docs")
async def create_doc(req: KnowledgeDocRequest) -> dict[str, Any]:
    r"""新增知识库文档"""
    doc = get_doc_repo().upsert(KnowledgeDoc(title=req.title, content=req.content, source=req.source))
    return {"status": "created", "id": doc.id}


@router.put("/docs/{doc_id}")
async def update_doc(doc_id: int, req: KnowledgeDocRequest) -> dict[str, Any]:
    r"""更新知识库文档"""
    existing = get_doc_repo().get(doc_id)
    if not existing:
        raise HTTPException(404, f"Document {doc_id} not found")
    existing.title = req.title
    existing.content = req.content
    existing.source = req.source
    get_doc_repo().upsert(existing)
    return {"status": "updated", "id": doc_id}


@router.delete("/docs/{doc_id}")
async def delete_doc(doc_id: int) -> dict[str, Any]:
    r"""软删除知识库文档 (status=archived)"""
    get_doc_repo().delete(doc_id)
    return {"status": "archived", "id": doc_id}


@router.post("/ingest")
async def ingest_knowledge() -> dict[str, Any]:
    r"""
    从DB重新索引全部文档到向量库
    文档变更后通过这个接口重建索引
    """
    return knowledge_base.ingest_from_db()


@router.get("/status")
async def knowledge_status() -> dict[str, Any]:
    r"""查看向量库索引了多少文档"""
    return knowledge_base.get_status()
