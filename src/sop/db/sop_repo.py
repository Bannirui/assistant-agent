from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ...config import settings


# SOP存到数据库的数据模型
@dataclass
class SopRecord:
    # 用id检索sop文档 如FLIGHT_REFUND_DISPUTE
    id: str
    # 品类 机票/酒店/火车/打车
    category: str
    # 用来解决哪些类型的客诉 ["退差价","价格争议"]
    issue_types: list[str]
    # 处理步骤 ["确认订单","查询价格",...]
    steps: list[str]
    # 补偿规则 [{"condition":"条件","action":"动作"}]
    compensation_rules: list[dict]
    # 话术模板 {"key":"文本"}
    templates: dict[str, str]
    # 操作按钮 [{"type":"refund","label":"发起退款"}]
    suggested_actions: list[dict]


class SopRepository(ABC):
    r"""
    SOP持久层抽象
    数据库生产用MySQL
    side project用SQLite
    """

    @abstractmethod
    def init(self) -> None:
        r"""
        建表 表不存在才创建
        """

    @abstractmethod
    def load_all(self) -> list[SopRecord]:
        r"""
        读取所有的SOP文档
        """

    @abstractmethod
    def upsert(self, record: SopRecord, updated_by: str = "") -> None:
        r"""
        新增或更新一条SOP
        :param record: SOP已经存在于数据库就更新 不在数据库就新增
        """

    @abstractmethod
    def soft_delete(self, sop_id: str) -> None:
        r"""
        软删除SOP 标记为archived
        :param sop_id: SOP的ID
        """

    @abstractmethod
    def import_from_yaml(self, yaml_dir: str = "") -> int:
        r"""
        尝试把本地的SOP文件导入到数据库去
        :param yaml_dir: 本地SOP文件的路径目录
        :return: 从本地导入了多少个SOP文件到数据库
        """


_repo: Optional[SopRepository] = None


# ---把数据库的操作暴露到模块层级 start---
def get_repository() -> SopRepository:
    r"""
    工厂函数 根据配置选择用哪种数据库
    :return: 具体的数据库实现
    """
    global _repo
    if _repo is None:
        sql_type: str = getattr(settings, "sop_db_type", "sqlite")
        if sql_type == "mysql":
            from .db_mysql import SopRepositoryMySQL
            _repo = SopRepositoryMySQL()
        else:
            from .db_sqlite import SopRepositorySQLite
            _repo = SopRepositorySQLite()
    return _repo


def init_db() -> None:
    get_repository().init()


def load_all_sops() -> list[dict]:
    records = get_repository().load_all()
    return [
        {
            "id": r.id,
            "category": r.category,
            "issue_types": r.issue_types,
            "steps": r.steps,
            "compensation_rules": r.compensation_rules,
            "templates": r.templates,
            "suggested_actions": r.suggested_actions,
        }
        for r in records
    ]


def upsert_sop(sop: dict, updated_by: str = "") -> None:
    get_repository().upsert(
        SopRecord(
            id=sop["id"],
            category=sop.get("category", ""),
            issue_types=sop.get("issue_types", []),
            steps=sop.get("steps", []),
            compensation_rules=sop.get("compensation_rules", []),
            templates=sop.get("templates", {}),
            suggested_actions=sop.get("suggested_actions", []),
        ),
        updated_by=updated_by,
    )


def import_from_yaml(yaml_dir: str = "") -> int:
    return get_repository().import_from_yaml(yaml_dir)


def archive_sop(sop_id: str) -> None:
    get_repository().soft_delete(sop_id)
# ---把数据库的操作暴露到模块层级 end---
