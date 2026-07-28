import pytest
from src.rag.knowledge_base import KnowledgeBase


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


class TestKnowledgeBase:
    def test_initialize_creates_collection(self):
        kb = KnowledgeBase()
        kb.initialize()
        assert kb.client is not None
        collections = kb.client.get_collections()
        collection_names = [c.name for c in collections.collections]
        assert "knowledge_base" in collection_names

    def test_status_not_initialized(self):
        kb = KnowledgeBase()
        status = kb.get_status()
        assert status["status"] == "not_initialized"
