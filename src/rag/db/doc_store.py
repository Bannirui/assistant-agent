from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from ...config import settings


@dataclass
class KnowledgeDoc:
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    source: str = ""
    status: str = "active"


class KnowledgeDocRepository(ABC):
    @abstractmethod
    def init(self) -> None: ...
    @abstractmethod
    def list_all(self) -> list[KnowledgeDoc]: ...
    @abstractmethod
    def get(self, doc_id: int) -> Optional[KnowledgeDoc]: ...
    @abstractmethod
    def upsert(self, doc: KnowledgeDoc) -> KnowledgeDoc: ...
    @abstractmethod
    def delete(self, doc_id: int) -> None: ...


# ── 工厂 ──

_repo: Optional[KnowledgeDocRepository] = None


def get_doc_repo() -> KnowledgeDocRepository:
    global _repo
    if _repo is None:
        db_type = getattr(settings, "knowledge_db_type", "sqlite")
        if db_type == "mysql":
            from .doc_store_mysql import KnowledgeDocRepoMySQL
            _repo = KnowledgeDocRepoMySQL()
        else:
            from .doc_store_sqlite import KnowledgeDocRepoSQLite
            _repo = KnowledgeDocRepoSQLite()
    return _repo
