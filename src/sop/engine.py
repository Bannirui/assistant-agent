import yaml
from pathlib import Path
from typing import Optional

from ..config import settings


class SOPEngine:
    # 两个缓存搭配 快速映射品类->sop的文本内容
    # sop id映射sop的yaml文本内容
    _sops: dict[str, dict]
    # 品类映射sop id
    _category_index: dict[str, list[str]]


def __init__(self):
    self._sops: dict[str, dict] = {}
    self._category_index: dict[str, list[str]] = {}


def load_all(self):
    r"""
    启动加载
    """
    # 存放sop的路径
    sop_dir: Path = settings.sop_path
    if not sop_dir.exists():
        sop_dir.mkdir(parents=True, exist_ok=True)
        return
    # 加载缓存之前先情况 防止污染
    self._sops.clear()
    self._category_index.clear()

    for yaml_file in sop_dir.glob("*.yaml"):
        with open(yaml_file, "r", encoding="utf-8") as f:
            sop = yaml.safe_load(f)
            if not sop:
                continue
            # 标准的sop范式规定文档必须有个字段照叫id 标识这个文档
            sop_id: str = sop.get("id")
            if not sop_id:
                continue
            # sop文件缓存起来
            self._sops[sop_id] = sop
            # yaml文件的品类字段
            category: str = sop.get("category", "")
            if category:
                if category not in self._category_index:
                    self._category_index[category] = []
                # sop文档品类到id的映射
                self._category_index[category].append(sop_id)


def search(
        self, category: str, issue_type: str
) -> Optional[dict]:
    r"""
    :param category: 客诉的品类 机票|打车
    :param issue_type: 客诉的类型 退差|晚点
    :return: sop的匹配度
             品类 and 客诉类型 都匹配->高度匹配1.0
             只有 品类 匹配->中等匹配0.5
    """
    # 客诉品类映射到sop id
    category_sops: list[str] = self._category_index.get(category, [])

    for sop_id in category_sops:
        # sop文档
        sop = self._sops.get(sop_id)
        if not sop:
            continue
        # sop囊括的客诉类型
        issue_types = sop.get("issue_types", [])
        # 看看是不是需要的客诉类型
        if issue_type in issue_types:
            return {
                "matched": True,
                "match_confidence": 1.0,
                "sop": sop,
            }

    for sop_id in category_sops:
        sop = self._sops.get(sop_id)
        if not sop:
            continue
        return {
            "matched": True,
            "match_confidence": 0.5,
            "sop": sop,
            "note": f"No exact match for '{issue_type}', returning general SOP for '{category}'",
        }

    return {"matched": False, "sop": None}


def list_sops(self) -> list[dict]:
    r"""
    所有的sop文档
    """
    return [
        {
            "id": sop["id"],
            "category": sop.get("category", ""),
            "issue_types": sop.get("issue_types", []),
        }
        for sop in self._sops.values()
    ]


def reload(self):
    r"""
    支持sop的热更新 可能运营会新增/修改sop
    """
    self.load_all()
    return {"status": "reloaded", "sop_count": len(self._sops)}


sop_engine = SOPEngine()
