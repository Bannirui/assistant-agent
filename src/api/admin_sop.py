r"""SOP管理接口—运营管理后台使用"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..sop.engine import sop_engine
from ..sop.db import load_all_sops as list_sops_from_db, upsert_sop

router = APIRouter(prefix="/admin/sop", tags=["SOP管理"])


# SOP新增/更新请求体
class SopUpsertRequest(BaseModel):
    # 规则ID 如FLIGHT_REFUND_DISPUTE
    id: str
    # 品类 机票/酒店/火车/打车
    category: str = ""
    # 用来解决哪些类型的客诉
    issue_types: list[str] = []
    # 处理步骤
    steps: list[str] = []
    # 补偿规则
    compensation_rules: list[dict] = []
    # 话术模板
    templates: dict[str, str] = {}
    # 操作按钮
    suggested_actions: list[dict] = []


@router.get("")
async def list_sops() -> list[dict[str, Any]]:
    r"""列出所有 SOP"""
    return list_sops_from_db()


@router.get("/{sop_id}")
async def get_sop(sop_id: str) -> dict[str, Any]:
    r"""查看单个 SOP 详情"""
    all_sops = list_sops_from_db()
    for s in all_sops:
        if s["id"] == sop_id:
            return s
    raise HTTPException(404, f"SOP {sop_id} not found")


@router.post("")
async def create_sop(req: SopUpsertRequest) -> dict[str, Any]:
    r"""上传SOP"""
    upsert_sop(req.model_dump(), updated_by="admin")
    return {"status": "created", "id": req.id}


@router.put("/{sop_id}")
async def update_sop(sop_id: str, req: SopUpsertRequest) -> dict[str, Any]:
    r"""更新SOP"""
    data = req.model_dump()
    data["id"] = sop_id
    upsert_sop(data, updated_by="admin")
    return {"status": "updated", "id": sop_id}


@router.delete("/{sop_id}")
async def delete_sop(sop_id: str) -> dict[str, Any]:
    r"""软删除 SOP (status=archived)"""
    from ..sop.db import archive_sop
    archive_sop(sop_id)
    return {"status": "archived", "id": sop_id}


@router.post("/reload")
async def reload_sop() -> dict[str, Any]:
    r"""
    从DB重新加载SOP到内存
    运营更新了SOP后通过这个接口进行重新加载
    """
    return sop_engine.reload()
