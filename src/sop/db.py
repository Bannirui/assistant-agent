import sqlite3
import json
from pathlib import Path
from typing import Optional

from ..config import settings

SCHEMA = """
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


def get_db_path() -> Path:
    r"""
    :return: sqlite路径
    """
    p = Path(settings.copilot_db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def init_db() -> None:
    r"""
    初始化sqlite表 表不存在就新建 不存在就跳过
    """
    conn = sqlite3.connect(str(get_db_path()))

    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def load_all_sops() -> list[dict]:
    r"""
    :return: 从数据库读取所有的SOP文档
    """
    conn = get_connection()
    try:
        # 从表里面拿到所有的SOP
        rows = conn.execute(
            "SELECT * FROM sops WHERE status = 'active' ORDER BY category, id"
        ).fetchall()
        # SOP文档
        sops = []
        for row in rows:
            sop = {
                "id": row["id"],
                "category": row["category"],
                "issue_types": json.loads(row["issue_types"]),
                "steps": json.loads(row["steps"]) if row["steps"] else [],
                "compensation_rules": json.loads(row["compensation"]) if row["compensation"] else [],
                "templates": json.loads(row["templates"]) if row["templates"] else {},
                "suggested_actions": json.loads(row["actions"]) if row["actions"] else [],
            }
            sops.append(sop)
        return sops
    finally:
        conn.close()


def upsert_sop(sop: dict, updated_by: str = "") -> None:
    r"""
    :param sop: 对SOP文档做新增或者更新
    :param updated_by: 操作人
    """
    conn = get_connection()
    try:
        # 看看SOP文档在数据库是不是已经存在
        existing = conn.execute("SELECT version FROM sops WHERE id = ?", (sop["id"],)).fetchone()
        if existing:
            new_version = existing["version"] + 1
            # 更新
            conn.execute(
                """UPDATE sops
                   SET category=?,
                       issue_types=?,
                       steps=?,
                       compensation=?,
                       templates=?,
                       actions=?,
                       version=?,
                       status='active',
                       updated_at=datetime('now'),
                       updated_by=?
                   WHERE id = ?""",
                (
                    sop["category"],
                    json.dumps(sop["issue_types"], ensure_ascii=False),
                    json.dumps(sop.get("steps", []), ensure_ascii=False),
                    json.dumps(sop.get("compensation_rules", []), ensure_ascii=False),
                    json.dumps(sop.get("templates", {}), ensure_ascii=False),
                    json.dumps(sop.get("suggested_actions", []), ensure_ascii=False),
                    new_version,
                    updated_by,
                    sop["id"],
                ),
            )
        else:
            # 新增
            conn.execute(
                """INSERT INTO sops (id, category, issue_types, steps, compensation, templates, actions, updated_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    sop["id"],
                    sop["category"],
                    json.dumps(sop["issue_types"], ensure_ascii=False),
                    json.dumps(sop.get("steps", []), ensure_ascii=False),
                    json.dumps(sop.get("compensation_rules", []), ensure_ascii=False),
                    json.dumps(sop.get("templates", {}), ensure_ascii=False),
                    json.dumps(sop.get("suggested_actions", []), ensure_ascii=False),
                    updated_by,
                ),
            )
        conn.commit()
    finally:
        conn.close()


def import_from_yaml(yaml_dir: str = "") -> int:
    r"""

    :param yaml_dir: 显式指定SOP的目录或者从配置文件里面拿目录
    :return: 多少个本地的SOP文件被放到数据库
    """
    import yaml
    import glob
    import os

    path = yaml_dir or settings.copilot_sop_dir
    files = glob.glob(os.path.join(path, "*.yaml"))
    count = 0

    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            sop = yaml.safe_load(f)
        # 认为规定SOP的范式 放到数据库已经后面的检索都要依赖id 所以要保证id的有效性
        if sop and sop.get("id"):
            # 数据库没有就新增 数据库有就更新
            upsert_sop(sop, updated_by="import")
            count += 1

    return count
