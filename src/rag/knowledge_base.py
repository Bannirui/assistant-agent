from typing import Optional
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from ..config import settings
from ..llm.provider import registry as provider_registry


COLLECTION_NAME = "knowledge_base"
VECTOR_SIZE = 1024
CHUNK_OVERLAP = 100
CHUNK_SIZE = 512


class KnowledgeBase:
    def __init__(self):
        self.client: Optional[QdrantClient] = None

    def initialize(self):
        qdrant_path = settings.qdrant_path
        qdrant_path.mkdir(parents=True, exist_ok=True)

        self.client = QdrantClient(path=str(qdrant_path))

        collections = self.client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )

    def chunk_text(self, text: str, source: str) -> list[dict]:
        chunks = []
        paragraphs = text.split("\n\n")

        current_chunk = ""
        current_heading = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if para.startswith("#"):
                parts = para.split("\n", 1)
                heading = parts[0].lstrip("#").strip()
                para_text = parts[1].strip() if len(parts) > 1 else ""
                if current_chunk:
                    chunks.append({"text": current_chunk.strip(), "source": source, "heading": current_heading})
                current_chunk = para_text
                current_heading = heading
            else:
                if len(current_chunk) + len(para) > CHUNK_SIZE and current_chunk:
                    chunks.append({"text": current_chunk.strip(), "source": source, "heading": current_heading})
                    overlap = current_chunk[-CHUNK_OVERLAP:] if len(current_chunk) > CHUNK_OVERLAP else ""
                    current_chunk = overlap + para
                else:
                    if current_chunk:
                        current_chunk += "\n" + para
                    else:
                        current_chunk = para

        if current_chunk.strip():
            chunks.append({"text": current_chunk.strip(), "source": source, "heading": current_heading})

        return chunks

    def _embed(self, texts: list[str]) -> list[list[float]]:
        return provider_registry.embed.embed(texts)

    def ingest_directory(self, directory: Optional[Path] = None):
        if directory is None:
            directory = settings.knowledge_path
        if not directory.exists():
            return {"status": "error", "message": f"Directory not found: {directory}"}

        all_chunks = []
        for file_path in directory.glob("*.md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            chunks = self.chunk_text(content, source=file_path.name)
            all_chunks.extend(chunks)

        if not all_chunks:
            return {"status": "ok", "message": "No documents found", "count": 0}

        texts = [c["text"] for c in all_chunks]
        embeddings = self._embed(texts)

        self.client.delete_collection(COLLECTION_NAME)
        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

        points = []
        for i, (chunk, embedding) in enumerate(zip(all_chunks, embeddings)):
            points.append(PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "heading": chunk.get("heading", ""),
                },
            ))

        batch_size = 100
        for i in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=points[i:i + batch_size],
            )

        return {"status": "ok", "count": len(points), "sources": list(set(c["source"] for c in all_chunks))}

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        query_embedding = self._embed([query])[0]

        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=top_k,
        )

        return [
            {
                "chunk_text": r.payload["text"],
                "source_document": r.payload["source"],
                "heading": r.payload.get("heading", ""),
                "relevance_score": round(r.score, 4),
            }
            for r in results
        ]

    def get_status(self) -> dict:
        try:
            info = self.client.get_collection(COLLECTION_NAME)
            return {
                "status": "ready",
                "collection": COLLECTION_NAME,
                "points_count": info.points_count,
            }
        except Exception:
            return {"status": "not_initialized"}


knowledge_base = KnowledgeBase()
