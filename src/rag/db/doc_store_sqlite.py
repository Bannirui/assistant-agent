import sqlite3
from pathlib import Path
from typing import Optional

from ...config import settings
from .doc_store import KnowledgeDoc, KnowledgeDocRepository


SCHEMA = """
CREATE TABLE IF NOT EXISTS knowledge_docs (
    -- 文档ID 自增
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 文档标题
    title       TEXT NOT NULL,
    -- 文档内容 (Markdown)
    content     TEXT NOT NULL,
    -- 来源 (如 confluence/语雀/手动上传)
    source      TEXT DEFAULT '',
    -- active/archived
    status      TEXT NOT NULL DEFAULT 'active',
    -- 创建时间
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    -- 更新时间
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


class KnowledgeDocRepoSQLite(KnowledgeDocRepository):
    def __init__(self):
        self._db_path: Optional[Path] = None

    def _get_path(self) -> Path:
        if self._db_path is None:
            p = Path(settings.knowledge_db_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            self._db_path = p
        return self._db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._get_path()))
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        conn = self._connect()
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()

    def list_all(self) -> list[KnowledgeDoc]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM knowledge_docs WHERE status='active' ORDER BY id"
            ).fetchall()
            return [_row_to_doc(row) for row in rows]
        finally:
            conn.close()

    def get(self, doc_id: int) -> Optional[KnowledgeDoc]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM knowledge_docs WHERE id=?", (doc_id,)
            ).fetchone()
            return _row_to_doc(row) if row else None
        finally:
            conn.close()

    def upsert(self, doc: KnowledgeDoc) -> KnowledgeDoc:
        conn = self._connect()
        try:
            if doc.id:
                conn.execute(
                    """UPDATE knowledge_docs SET
                        title=?, content=?, source=?,
                        status='active', updated_at=datetime('now')
                    WHERE id=?""",
                    (doc.title, doc.content, doc.source, doc.id),
                )
            else:
                cursor = conn.execute(
                    """INSERT INTO knowledge_docs (title, content, source)
                    VALUES (?, ?, ?)""",
                    (doc.title, doc.content, doc.source),
                )
                doc.id = cursor.lastrowid
            conn.commit()
            return doc
        finally:
            conn.close()

    def delete(self, doc_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE knowledge_docs SET status='archived', updated_at=datetime('now') WHERE id=?",
                (doc_id,),
            )
            conn.commit()
        finally:
            conn.close()


def _row_to_doc(row: sqlite3.Row) -> KnowledgeDoc:
    return KnowledgeDoc(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        source=row["source"],
        status=row["status"],
    )
