r"""
ChromaDB
参考https://docs.trychroma.com/
"""

from .repository import VectorRepository, VectorPoint, SearchResult


class VectorRepositoryChroma(VectorRepository):
    def init(self, collection: str, vector_size: int) -> None:
        raise NotImplementedError("ChromaDB is not yet implemented")

    def clear(self, collection: str) -> None:
        raise NotImplementedError("ChromaDB is not yet implemented")

    def upsert(self, collection: str, points: list[VectorPoint]) -> None:
        raise NotImplementedError("ChromaDB is not yet implemented")

    def search(
        self, collection: str, query_vector: list[float], top_k: int
    ) -> list[SearchResult]:
        raise NotImplementedError("ChromaDB is not yet implemented")

    def get_status(self, collection: str) -> dict:
        raise NotImplementedError("ChromaDB is not yet implemented")
