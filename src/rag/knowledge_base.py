from typing import Optional
from pathlib import Path

from ..config import settings
from ..llm.provider import registry as provider_registry
from .vector.vector_repo import get_repository, VectorPoint, SearchResult

# 向量库表名 文档数据库的概念
COLLECTION_NAME = "knowledge_base"
# 相邻两个块的重复字符数 防止上下文断裂
CHUNK_OVERLAP = 100
# 每块最大字符数
CHUNK_SIZE = 512


class KnowledgeBase:
    r"""
    RAG的R检索器
    """

    def __init__(self):
        self._initialized = False

    def initialize(self) -> None:
        # 向量库的实现
        repo = get_repository()
        # 向量库建表
        repo.init(COLLECTION_NAME, settings.knowledge_vector_size)
        self._initialized = True

    def chunk_text(self, text: str, source: str) -> list[dict]:
        r"""
        :param text: 文本内容
        :param source: 文件名
        :return: 文本内容分成的块
        """
        # 文本被分成的块{块内容 文件名 段落标题} 相邻的块冗余100个字
        chunks: list[dict] = []
        # 双换行分段
        paragraphs = text.split("\n\n")

        # 划分的块 遇到了新的段落 块就不要集满 有多少算多少
        current_chunk = ""
        # 段落标题
        current_heading = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            # 新的段落
            if para.startswith("#"):
                # 段落标题那一行
                parts = para.split("\n", 1)
                # 段落标题
                heading = parts[0].lstrip("#").strip()
                # 段落内容
                para_text = parts[1].strip() if len(parts) > 1 else ""
                if current_chunk:
                    # 已经开始处理新的段落的 先把上一个段落的块收集起来 块内容 文件名 标题名
                    chunks.append({"text": current_chunk.strip(), "source": source, "heading": current_heading})
                current_chunk = para_text
                current_heading = heading
            else:
                # 段落太长 之前已经有一部分被划分到块里面了 块也满了
                if len(current_chunk) + len(para) > CHUNK_SIZE and current_chunk:
                    # 块大小超标了 先把它收集起来 准备开辟新块
                    chunks.append({"text": current_chunk.strip(), "source": source, "heading": current_heading})
                    # 上一个块的尾巴上抠一段出来占位下一块的开头 也就是挨着两个块弄点重复内容
                    overlap = current_chunk[-CHUNK_OVERLAP:] if len(current_chunk) > CHUNK_OVERLAP else ""
                    # 这个地方 冗余内容+段落内容 可能是超出了块大小限制的 下面会对块大小检查 递归拆分
                    current_chunk = overlap + para
                else:
                    # 块还没满 可以继续放这个段落的内容
                    if current_chunk:
                        current_chunk += "\n" + para
                    else:
                        current_chunk = para

            # 如果当前块超过限制 递归拆分
            while len(current_chunk) > CHUNK_SIZE:
                # 切出前CHUNK_SIZE个字符作为一块
                chunks.append({"text": current_chunk[:CHUNK_SIZE].strip(), "source": source, "heading": current_heading})
                if len(current_chunk) > CHUNK_SIZE + CHUNK_OVERLAP:
                    # 一个块放不下剩下的内容 还要继续冗余
                    # 丢掉前面412个 也就是说现在块的开头100个跟上一个块最后100个一样
                    current_chunk = current_chunk[CHUNK_SIZE - CHUNK_OVERLAP:]
                else:
                    # 一个块能放下剩下的内容 不用冗余了 剩下的所有内容都放这一个块上
                    current_chunk = current_chunk[CHUNK_SIZE:]
                    break

        if current_chunk.strip():
            chunks.append({"text": current_chunk.strip(), "source": source, "heading": current_heading})

        return chunks

    def _embed(self, texts: list[str]) -> list[list[float]]:
        r"""
        文字转向量
        :param texts: 知识库所有文本文件被分成的块 里面的块内容 也就是不包含标题
        :return: 向量
        """
        # 拿到向量模型调用API转向量
        return provider_registry.embed.embed(texts)

    def _build_index(self, all_chunks: list[dict]) -> dict:
        """chunk → embed → 写入向量库"""
        if not all_chunks:
            return {"status": "ok", "message": "No documents found", "count": 0}

        texts = [c["text"] for c in all_chunks]
        embeddings = self._embed(texts)

        repo = get_repository()
        repo.clear(COLLECTION_NAME)
        repo.init(COLLECTION_NAME, settings.knowledge_vector_size)

        points = []
        for i, (chunk, emb) in enumerate(zip(all_chunks, embeddings)):
            points.append(VectorPoint(
                id=i,
                vector=emb,
                text=chunk["text"],
                source=chunk["source"],
                heading=chunk.get("heading", ""),
            ))

        repo.upsert(COLLECTION_NAME, points)
        return {"status": "ok", "count": len(points), "sources": list(set(c["source"] for c in all_chunks))}

    def ingest_from_db(self) -> dict:
        """从 knowledge_docs 表读取文档，切块、向量化、写入向量库"""
        from .db.doc_store import get_doc_repo
        docs = get_doc_repo().list_all()

        all_chunks = []
        for doc in docs:
            chunks = self.chunk_text(doc.content, source=doc.title)
            all_chunks.extend(chunks)

        return self._build_index(all_chunks)

    def ingest_directory(self, directory: Optional[Path] = None) -> dict:
        r"""
        从本地 .md 文件导入 (需显式指定路径 生产环境无本地文件)
        """
        if directory is None:
            return {"status": "error", "message": "No directory specified"}

        # 知识库所有文件被分成的块
        all_chunks = []
        for file_path in directory.glob("*.md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # 所有的文件都要分块
            chunks = self.chunk_text(content, source=file_path.name)
            all_chunks.extend(chunks)

        return self._build_index(all_chunks)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        r"""
        不是直接查询文本 转成向量从向量库里面查询几个最接近的
        :param query: 查询的文本
        :param top_k: 查询条件
        :return:
        """
        query_embedding = self._embed([query])[0]

        repo = get_repository()
        # 从向量库里面查
        results = repo.search(COLLECTION_NAME, query_embedding, top_k)

        return [
            {
                "chunk_text": r.chunk_text,
                "source_document": r.source_document,
                "heading": r.heading,
                "relevance_score": r.relevance_score,
            }
            for r in results
        ]

    def get_status(self) -> dict:
        r"""
        知识库的状态
        """
        try:
            return get_repository().get_status(COLLECTION_NAME)
        except Exception:
            return {"status": "not_initialized"}


knowledge_base = KnowledgeBase()
