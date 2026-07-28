r"""
参考 https://qdrant.tech/documentation/
"""
from pathlib import Path
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from ..config import settings
from .repository import VectorRepository, VectorPoint, SearchResult


class VectorRepositoryQdrant(VectorRepository):
    r"""
    Qdrant的本地模式
    """
    def __init__(self):
        self._client: Optional[QdrantClient] = None

    def _get_client(self) -> QdrantClient:
        if self._client is None:
            qdrant_path = settings.qdrant_path
            qdrant_path.mkdir(parents=True, exist_ok=True)
            self._client = QdrantClient(path=str(qdrant_path))
        return self._client

    def init(self, collection: str, vector_size: int) -> None:
        client = self._get_client()
        collections = client.get_collections()
        names = [c.name for c in collections.collections]
        if collection not in names:
            client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def clear(self, collection: str) -> None:
        client = self._get_client()
        client.delete_collection(collection)

    def upsert(self, collection: str, points: list[VectorPoint]) -> None:
        client = self._get_client()
        qdrant_points = [
            PointStruct(
                id=p.id,
                vector=p.vector,
                payload={
                    "text": p.text,
                    "source": p.source,
                    "heading": p.heading,
                },
            )
            for p in points
        ]
        batch = 100
        for i in range(0, len(qdrant_points), batch):
            client.upsert(
                collection_name=collection,
                points=qdrant_points[i:i + batch],
            )

    def search(
        self, collection: str, query_vector: list[float], top_k: int
    ) -> list[SearchResult]:
        client = self._get_client()
        results = client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
        )
        return [
            SearchResult(
                chunk_text=r.payload["text"],
                source_document=r.payload["source"],
                heading=r.payload.get("heading", ""),
                relevance_score=round(r.score, 4),
            )
            for r in results
        ]

    def get_status(self, collection: str) -> dict:
        try:
            client = self._get_client()
            info = client.get_collection(collection)
            return {
                "status": "ready",
                "collection": collection,
                "points_count": info.points_count,
            }
        except Exception:
            return {"status": "not_initialized"}
