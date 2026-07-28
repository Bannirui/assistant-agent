import pytest
from src.rag.knowledge_base import KnowledgeBase, COLLECTION_NAME
from src.rag.repository import get_repository


class TestChunking:
    @pytest.fixture
    def kb(self):
        return KnowledgeBase()

    def test_chunk_simple_text(self, kb):
        text = "段落A" + "内容" * 200 + "\n\n" + "段落B" + "数据" * 200
        chunks = kb.chunk_text(text, source="test.md")
        assert len(chunks) >= 2
        assert all("text" in c for c in chunks)
        assert all("source" in c for c in chunks)
        assert all(c["source"] == "test.md" for c in chunks)

    def test_chunk_with_headings(self, kb):
        text = "## 第一节\n第一节的内容。\n\n## 第二节\n第二节的内容。"
        chunks = kb.chunk_text(text, source="test.md")
        assert len(chunks) >= 2

    def test_chunk_empty_text(self, kb):
        chunks = kb.chunk_text("", source="test.md")
        assert len(chunks) == 0

    def test_chunk_single_paragraph(self, kb):
        text = "只有一段内容的文档。"
        chunks = kb.chunk_text(text, source="test.md")
        assert len(chunks) >= 1

    def test_chunk_preserves_source(self, kb):
        text = "段落A\n\n段落B"
        chunks = kb.chunk_text(text, source="policy.md")
        for chunk in chunks:
            assert chunk["source"] == "policy.md"

    def test_chunk_long_paragraph_no_overflow(self, kb):
        """单段落超过 CHUNK_SIZE 也要被切成多块"""
        long_para = "X" * 800 + "\n\n" + "Y" * 300
        chunks = kb.chunk_text(long_para, source="test.md")
        assert len(chunks) >= 2
        for c in chunks:
            assert len(c["text"]) <= 520   # CHUNK_SIZE 512 + 少量余量


class TestKnowledgeBase:
    def test_initialize_creates_collection(self):
        kb = KnowledgeBase()
        kb.initialize()
        repo = get_repository()
        status = repo.get_status(COLLECTION_NAME)
        assert status["status"] == "ready"

    def test_repo_status(self):
        repo = get_repository()
        status = repo.get_status(COLLECTION_NAME)
        assert status["status"] == "ready"
