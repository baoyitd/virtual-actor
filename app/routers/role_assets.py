"""角色 CRUD 路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.services.role_service import RoleService
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleDetail, RoleListItem, RoleStatus,
)

router = APIRouter(prefix="/role-assets", tags=["角色管理"], dependencies=[Depends(get_current_user)])


# ──── 创建 ────

@router.post("", response_model=RoleDetail, status_code=201)
async def create_role(data: RoleCreate, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    role = await svc.create(data)
    await db.commit()
    return await _to_detail(svc, role.id)


# ──── 读取 ────

@router.get("", response_model=list[RoleListItem])
async def list_roles(
    status: RoleStatus | None = Query(None, description="按状态筛选"),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    roles = await svc.list_by_status(status)
    result = []
    for r in roles:
        stats = await svc.get_with_test_stats(r.id)
        if r.current_version_id:
            fields = await svc.get_version_fields(r.current_version_id)
            if stats is not None:
                stats["model_binding"] = fields.get("model_binding")
        result.append(_to_list_item(r, stats))
    return result


@router.get("/{role_id}", response_model=RoleDetail)
async def get_role(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    stats = await svc.get_with_test_stats(role_id)
    if not stats:
        raise HTTPException(status_code=404, detail="角色不存在")
    return await _to_detail(svc, role_id, stats)


# ──── 更新 ────

@router.patch("/{role_id}", response_model=RoleDetail)
async def update_role(role_id: str, data: RoleUpdate, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    role = await svc.update(role_id, data)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    await db.commit()
    return await _to_detail(svc, role_id)


# ──── 状态迁移 ────

@router.post("/{role_id}/publish", response_model=RoleDetail)
async def publish_role(
    role_id: str,
    user: CurrentUser,
    published_by: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    role = await svc.publish(role_id, published_by or user.username)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    await db.commit()
    return await _to_detail(svc, role_id)


@router.post("/{role_id}/archive", response_model=RoleDetail)
async def archive_role(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    role = await svc.archive(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    await db.commit()
    return await _to_detail(svc, role_id)


@router.post("/{role_id}/to-test", response_model=RoleDetail)
async def move_to_test(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    role = await svc.change_status(role_id, RoleStatus.TEST)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    await db.commit()
    return await _to_detail(svc, role_id)


# ──── 删除 ────

@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    ok = await svc.delete(role_id)
    if not ok:
        raise HTTPException(status_code=404, detail="角色不存在")
    await db.commit()


# ──── 辅助函数 ────

def _to_list_item(role, stats: dict | None = None) -> RoleListItem:
    s = stats or {}
    return RoleListItem(
        role_id=role.id,
        role_version_id=role.current_version_id,
        role_name=role.name,
        bio=role.bio,
        tags=role.tags or [],
        status=RoleStatus(role.status),
        summary=role.bio[:100] if role.bio else "",
        model_binding=s.get("model_binding"),
        has_test_record=s.get("has_test_record", False),
        latest_test_rating=s.get("latest_test_rating"),
        latest_tested_at=s.get("latest_tested_at"),
        test_run_count=s.get("test_run_count", 0),
        updated_at=role.updated_at,
    )


async def _to_detail(svc: RoleService, role_id: str, stats: dict | None = None) -> RoleDetail:
    if stats is None:
        stats = await svc.get_with_test_stats(role_id)
    role = stats["role"]
    fields = {}
    if role.current_version_id:
        fields = await svc.get_version_fields(role.current_version_id)
    validated = []
    if role.current_version_id:
        from sqlalchemy import select
        from app.models.knowledge_ref import ValidatedKnowledgeVersion
        result = await svc.db.execute(
            select(ValidatedKnowledgeVersion).where(
                ValidatedKnowledgeVersion.version_id == role.current_version_id
            )
        )
        validated = result.scalars().all()

    return RoleDetail(
        role_id=role.id,
        role_version_id=role.current_version_id,
        name=role.name,
        bio=role.bio,
        tags=role.tags or [],
        status=RoleStatus(role.status),
        identity_background=fields.get("identity_background"),
        point_of_view=fields.get("point_of_view"),
        decision_style=fields.get("decision_style"),
        responsibility_boundary=fields.get("responsibility_boundary"),
        speaking_style=fields.get("speaking_style"),
        collaboration_mode=fields.get("collaboration_mode"),
        capability_boundary=fields.get("capability_boundary"),
        model_binding=fields.get("model_binding"),
        knowledge_refs=[
            {
                "id": kr.id,
                "role_id": kr.role_id,
                "kb_id": kr.kb_id,
                "knowledge_object_id": kr.knowledge_object_id,
                "knowledge_version_id": kr.knowledge_version_id,
                "title": kr.title,
                "type": kr.type,
                "knowledge_source": kr.knowledge_source,
                "bound_at": kr.bound_at,
            }
            for kr in (role.knowledge_refs or [])
        ],
        validated_knowledge_versions=[
            {"knowledge_object_id": item.knowledge_object_id, "knowledge_version_id": item.knowledge_version_id}
            for item in validated
        ],
        has_test_record=stats.get("has_test_record", False),
        latest_test_rating=stats.get("latest_test_rating"),
        latest_tested_at=stats.get("latest_tested_at"),
        test_run_count=stats.get("test_run_count", 0),
        created_at=role.created_at,
        updated_at=role.updated_at,
    )
