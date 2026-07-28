from typing import Optional

from .db import load_all_sops, import_from_yaml


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
        把SOP加载到内存 构建缓存
        """
        # 查数据库
        sops: list[dict] = load_all_sops()
        # 先清空缓存 防止污染
        self._sops.clear()
        self._category_index.clear()

        for sop in sops:
            sop_id = sop.get("id")
            if not sop_id:
                continue
            # 构建缓存 id映射SOP
            self._sops[sop_id] = sop
            # SOP的品类
            category: str = sop.get("category", "")
            if category:
                if category not in self._category_index:
                    # 品类不在缓存里面
                    self._category_index[category] = []
                # 构建缓存 品类映射idj
                self._category_index[category].append(sop_id)

    def search(self, category: str, issue_type: str) -> dict:
        r"""
        :param category: 客诉的品类 机票|打车
        :param issue_type: 客诉的类型 退差|晚点
        :return: sop的匹配度
                 品类 and 客诉类型 都匹配->高度匹配1.0
                 只有 品类 匹配->中等匹配0.5
        """
        # 品类的SOP id
        category_sops: list[str] = self._category_index.get(category, [])

        for sop_id in category_sops:
            sop = self._sops.get(sop_id)
            if not sop:
                continue
            issue_types = sop.get("issue_types", [])
            if issue_type in issue_types:
                # 高度匹配 品类+客诉类型
                return {
                    "matched": True,
                    "match_confidence": 1.0,
                    "sop": sop,
                }

        for sop_id in category_sops:
            sop = self._sops.get(sop_id)
            if not sop:
                continue
            # 中等匹配 品类
            return {
                "matched": True,
                "match_confidence": 0.5,
                "sop": sop,
                "note": f"No exact match for '{issue_type}', returning general SOP for '{category}'",
            }
        # 没匹配到SOP
        return {"matched": False, "sop": None}

    def list_sops(self) -> list[dict]:
        r"""
        所有的SOP文档
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
        支持热加载 运营会对SOP进行新增/更新/删除 对应的数据库会更新 重新从数据拉数据构建内存缓存
        """
        self.load_all()
        return {"status": "reloaded", "sop_count": len(self._sops)}


sop_engine = SOPEngine()
