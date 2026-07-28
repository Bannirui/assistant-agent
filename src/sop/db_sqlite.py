import json
import sqlite3
from pathlib import Path
from typing import Optional

from .db import SopRepository, SopRecord
from ..config import settings


SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS sops (
    -- 用id检索sop文档 如FLIGHT_REFUND_DISPUTE
    id          TEXT PRIMARY KEY,
    -- 品类 机票/酒店/火车/打车
    category    TEXT NOT NULL,
    -- 用来解决哪些类型的客诉 ["退差价","价格争议"]
    issue_types TEXT NOT NULL,
    -- 处理步骤 ["确认订单","查询价格",...]
    steps       TEXT,
    -- 补偿规则 [{"condition":"条件","action":"动作"}]
    compensation TEXT,
    -- 话术模板 {"key":"文本"}
    templates   TEXT,
    -- 操作按钮 [{"type":"refund","label":"发起退款"}]
    actions     TEXT,
    -- 版本号 每次修改+1
    version     INTEGER NOT NULL DEFAULT 1,
    -- active/draft/archived
    status      TEXT NOT NULL DEFAULT 'active',
    -- 创建时间
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    -- 更新时间
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    -- 修改人
    updated_by  TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_sop_category ON sops(category);
CREATE INDEX IF NOT EXISTS idx_sop_status  ON sops(status);
"""


class SopRepositorySQLite(SopRepository):
    r"""
    数据库用的是sqlite
    """
    _db_path: Optional[Path]

    def __init__(self):
        self._db_path: Optional[Path] = None

    def _get_path(self) -> Path:
        r"""
        :return: sqlite数据库 内嵌路径
        """
        if self._db_path is None:
            p = Path(settings.copilot_db_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            self._db_path = p
        return self._db_path

    def _connect(self) -> sqlite3.Connection:
        r"""
        连接到sqlite数据库
        """
        conn = sqlite3.connect(str(self._get_path()))
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        r"""
        初始化sqlite
        """
        # 连接数据库
        conn = self._connect()
        # 创建SOP表
        conn.executescript(SQLITE_SCHEMA)
        conn.commit()
        conn.close()

    def load_all(self) -> list[SopRecord]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM sops WHERE status = 'active' ORDER BY category, id"
            ).fetchall()
            return [_row_to_record(row) for row in rows]
        finally:
            conn.close()

    def upsert(self, record: SopRecord, updated_by: str = "") -> None:
        conn = self._connect()
        try:
            existing = conn.execute(
                "SELECT version FROM sops WHERE id = ?", (record.id,)
            ).fetchone()
            if existing:
                conn.execute(
                    """UPDATE sops SET
                        category=?, issue_types=?, steps=?, compensation=?,
                        templates=?, actions=?, version=?, status='active',
                        updated_at=datetime('now'), updated_by=?
                    WHERE id = ?""",
                    (
                        record.category,
                        json.dumps(record.issue_types, ensure_ascii=False),
                        json.dumps(record.steps, ensure_ascii=False),
                        json.dumps(record.compensation_rules, ensure_ascii=False),
                        json.dumps(record.templates, ensure_ascii=False),
                        json.dumps(record.suggested_actions, ensure_ascii=False),
                        existing["version"] + 1,
                        updated_by,
                        record.id,
                    ),
                )
            else:
                conn.execute(
                    """INSERT INTO sops
                        (id, category, issue_types, steps, compensation, templates, actions, updated_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        record.id,
                        record.category,
                        json.dumps(record.issue_types, ensure_ascii=False),
                        json.dumps(record.steps, ensure_ascii=False),
                        json.dumps(record.compensation_rules, ensure_ascii=False),
                        json.dumps(record.templates, ensure_ascii=False),
                        json.dumps(record.suggested_actions, ensure_ascii=False),
                        updated_by,
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def import_from_yaml(self, yaml_dir: str = "") -> int:
        import yaml
        import glob
        import os

        path = yaml_dir or settings.copilot_sop_dir
        files = glob.glob(os.path.join(path, "*.yaml"))
        count = 0

        for filepath in files:
            with open(filepath, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
            if raw and raw.get("id"):
                record = SopRecord(
                    id=raw["id"],
                    category=raw.get("category", ""),
                    issue_types=raw.get("issue_types", []),
                    steps=raw.get("steps", []),
                    compensation_rules=raw.get("compensation_rules", []),
                    templates=raw.get("templates", {}),
                    suggested_actions=raw.get("suggested_actions", []),
                )
                self.upsert(record, updated_by="import")
                count += 1

        return count


def _row_to_record(row: sqlite3.Row) -> SopRecord:
    r"""
    数据库映射到数据模型
    :param row: 数据库记录
    :return: 模型
    """
    return SopRecord(
        id=row["id"],
        category=row["category"],
        issue_types=json.loads(row["issue_types"]),
        steps=json.loads(row["steps"]) if row["steps"] else [],
        compensation_rules=json.loads(row["compensation"]) if row["compensation"] else [],
        templates=json.loads(row["templates"]) if row["templates"] else {},
        suggested_actions=json.loads(row["actions"]) if row["actions"] else [],
    )
