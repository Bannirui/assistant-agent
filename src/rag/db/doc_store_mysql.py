r"""
MySQL 后端占位。
"""

from .doc_store import KnowledgeDoc, KnowledgeDocRepository


class KnowledgeDocRepoMySQL(KnowledgeDocRepository):
    def init(self) -> None:
        raise NotImplementedError("MySQL backend is not yet implemented")

    def list_all(self) -> list[KnowledgeDoc]:
        raise NotImplementedError("MySQL backend is not yet implemented")

    def get(self, doc_id: int) -> KnowledgeDoc | None:
        raise NotImplementedError("MySQL backend is not yet implemented")

    def upsert(self, doc: KnowledgeDoc) -> KnowledgeDoc:
        raise NotImplementedError("MySQL backend is not yet implemented")

    def delete(self, doc_id: int) -> None:
        raise NotImplementedError("MySQL backend is not yet implemented")
