import yaml
from pathlib import Path
from typing import Optional

from ..config import settings


class SOPEngine:
    def __init__(self):
        self._sops: dict[str, dict] = {}
        self._category_index: dict[str, list[str]] = {}

    def load_all(self):
        sop_dir = settings.sop_path
        if not sop_dir.exists():
            sop_dir.mkdir(parents=True, exist_ok=True)
            return

        self._sops.clear()
        self._category_index.clear()

        for yaml_file in sop_dir.glob("*.yaml"):
            with open(yaml_file, "r", encoding="utf-8") as f:
                sop = yaml.safe_load(f)
                if not sop:
                    continue

                sop_id = sop.get("id")
                if not sop_id:
                    continue

                self._sops[sop_id] = sop

                category = sop.get("category", "")
                if category:
                    if category not in self._category_index:
                        self._category_index[category] = []
                    self._category_index[category].append(sop_id)

    def search(
        self, category: str, issue_type: str
    ) -> Optional[dict]:
        category_sops = self._category_index.get(category, [])

        for sop_id in category_sops:
            sop = self._sops.get(sop_id)
            if not sop:
                continue
            issue_types = sop.get("issue_types", [])
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
        return [
            {
                "id": sop["id"],
                "category": sop.get("category", ""),
                "issue_types": sop.get("issue_types", []),
            }
            for sop in self._sops.values()
        ]

    def reload(self):
        self.load_all()
        return {"status": "reloaded", "sop_count": len(self._sops)}


sop_engine = SOPEngine()
