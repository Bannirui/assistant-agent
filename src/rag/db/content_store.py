r"""
内容存储抽象层。
小文件 (<1MB): ContentStoreInline   直接存 DB
大文件 (>1MB): ContentStoreOSS      存 OSS，DB 只存 URL
"""

from abc import ABC, abstractmethod
from typing import Optional

from ...config import settings


class ContentStore(ABC):
    """内容持久层抽象"""

    @abstractmethod
    def get(self, doc_id: int) -> Optional[str]:
        """读取文档内容"""

    @abstractmethod
    def put(self, doc_id: int, content: str) -> Optional[str]:
        """
        存储文档内容
        返回: inline 模式返回 None, OSS 模式返回 URL
        """

    @abstractmethod
    def delete(self, doc_id: int) -> None:
        """删除文档内容"""


# ── Inline 实现 (内容直接存 DB) ──

class ContentStoreInline(ContentStore):
    """小文件直接存数据库 content 字段 当前默认模式"""

    def get(self, doc_id: int) -> Optional[str]:
        from .doc_store import get_doc_repo
        doc = get_doc_repo().get(doc_id)
        return doc.content if doc else None

    def put(self, doc_id: int, content: str) -> Optional[str]:
        from .doc_store import get_doc_repo
        doc = get_doc_repo().get(doc_id)
        if doc:
            doc.content = content
            get_doc_repo().upsert(doc)
        return None  # inline 模式不返回 URL

    def delete(self, doc_id: int) -> None:
        pass  # inline 模式内容随文档一起软删除


# ── 工厂 ──

_store: Optional[ContentStore] = None


def get_content_store() -> ContentStore:
    global _store
    if _store is None:
        backend = getattr(settings, "knowledge_content_backend", "inline")
        if backend == "oss":
            from .content_store_oss import ContentStoreOSS
            _store = ContentStoreOSS()
        else:
            _store = ContentStoreInline()
    return _store
