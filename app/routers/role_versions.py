"""版本相关路由（含决策产品最小消费接口）"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.services.role_service import RoleService
from app.services.version_service import VersionService
from app.schemas.version import PublishedVersionOut, VersionListItem
from app.schemas.role import RoleVersionPublicResponse

router = APIRouter(tags=["角色版本"], dependencies=[Depends(get_current_user)])


# ──── 决策产品最小消费接口 ────

@router.get("/role-assets/{role_id}/published-version", response_model=PublishedVersionOut)
async def get_published_version(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = VersionService(db)
    version = await svc.get_published_version(role_id)
    if not version:
        raise HTTPException(status_code=404, detail="该角色无已发布版本")
    return PublishedVersionOut(
        role_id=role_id,
        role_version_id=version.id,
        published_at=version.published_at,
        published_by=version.published_by,
    )


@router.get("/role-versions/{version_id}", response_model=RoleVersionPublicResponse)
async def get_version_detail(version_id: str, db: AsyncSession = Depends(get_db)):
    version_svc = VersionService(db)
    role_svc = RoleService(db)

    version = await version_svc.get_by_id(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    # 获取角色基本信息
    role_stats = await role_svc.get_with_test_stats(version.role_id)
    if not role_stats:
        raise HTTPException(status_code=404, detail="角色不存在")
    role = role_stats["role"]

    # 获取版本字段快照
    fields = await role_svc.get_version_fields(version_id)

    return RoleVersionPublicResponse(
        role_id=role.id,
        role_version_id=version.id,
        summary=(fields.get("bio") or role.bio or "")[:100],
        model_binding=fields.get("model_binding"),
        identity_background=fields.get("identity_background"),
        point_of_view=fields.get("point_of_view"),
        decision_style=fields.get("decision_style"),
        responsibility_boundary=fields.get("responsibility_boundary"),
        speaking_style=fields.get("speaking_style"),
        knowledge_refs=[
            {
                "id": kr.id,
                "role_id": kr.role_id,
                "knowledge_object_id": kr.knowledge_object_id,
                "knowledge_version_id": kr.knowledge_version_id,
                "title": kr.title,
                "type": kr.type,
                "bound_at": kr.bound_at,
            }
            for kr in (role.knowledge_refs or [])
        ],
        validated_knowledge_versions=[
            {"knowledge_object_id": vk.knowledge_object_id, "knowledge_version_id": vk.knowledge_version_id}
            for vk in (version.validated_knowledge or [])
        ],
        has_test_record=role_stats.get("has_test_record", False),
        latest_test_rating=role_stats.get("latest_test_rating"),
        latest_tested_at=role_stats.get("latest_tested_at"),
        test_run_count=role_stats.get("test_run_count", 0),
    )


# ──── 扩展接口 ────

@router.get("/role-assets/{role_id}/versions", response_model=list[VersionListItem])
async def list_versions(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = VersionService(db)
    versions = await svc.list_versions(role_id)
    return [
        VersionListItem(
            role_version_id=v.id,
            version_number=v.version_number,
            status=v.status,
            published_at=v.published_at,
        )
        for v in versions
    ]
