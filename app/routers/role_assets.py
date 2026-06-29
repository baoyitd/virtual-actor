"""v0.5 角色主路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.schemas.role import (
    BriefingSaveRequest,
    RoleCreate,
    RoleDetail,
    RoleListItem,
    RoleStatus,
    RoleUpdate,
    RoleWorkspaceSummary,
)
from app.services.recommend_service import _meets_pool_criteria
from app.services.output_schema_service import OUTPUT_TEMPLATES
from app.services.role_service import RoleService

router = APIRouter(prefix="/role-assets", tags=["角色管理"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=RoleDetail, status_code=201)
async def create_role(
    data: RoleCreate,
    creation_source_hint: str = Query(default="manual"),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    try:
        role = await svc.create(data, creation_source=creation_source_hint)
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    await db.commit()
    detail = await svc.build_detail(role.id)
    assert detail is not None
    return detail


@router.get("", response_model=list[RoleListItem])
async def list_roles(
    status: RoleStatus | None = Query(None),
    category: str | None = Query(None),
    owner: str | None = Query(None),
    business_domain: str | None = Query(None),
    visibility: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    roles = await svc.list_by_status(
        status=status,
        category=category,
        owner=owner,
        business_domain=business_domain,
        visibility=visibility,
    )
    items: list[RoleListItem] = []
    for role in roles:
        detail = await svc.build_detail(role.id)
        if not detail:
            continue
        items.append(
            RoleListItem(
                role_id=detail.role_id,
                role_version_id=detail.role_version_id,
                published_version_id=detail.published_version_id,
                role_name=detail.name,
                bio=detail.bio,
                tags=detail.tags,
                status=detail.status,
                summary=detail.main_duty_cluster or detail.bio,
                model_binding=detail.model_binding,
                has_test_record=detail.has_test_record,
                latest_test_rating=detail.latest_test_rating,
                latest_tested_at=detail.latest_tested_at,
                test_run_count=detail.test_run_count,
                updated_at=detail.updated_at,
                category=detail.category,
                owner=detail.owner,
                visibility=detail.visibility,
                business_domain=detail.business_domain,
                creation_source=detail.creation_source,
                output_mode=detail.output_mode,
                output_type=detail.output_type,
                briefing_status=detail.briefing.status,
                recommend_pool_eligible=_meets_pool_criteria(detail),
                legacy_incomplete=detail.legacy.is_legacy and bool(detail.legacy.missing_requirements),
            )
        )
    return items


@router.get("/output-templates", tags=["输出模板"])
async def get_output_templates():
    return OUTPUT_TEMPLATES


@router.get("/{role_id}", response_model=RoleDetail)
async def get_role(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    detail = await svc.build_detail(role_id)
    if not detail:
        raise HTTPException(status_code=404, detail="角色不存在")
    return detail


@router.get("/{role_id}/workspace", response_model=RoleWorkspaceSummary)
async def get_workspace_summary(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    detail = await svc.build_workbench_summary(role_id)
    if not detail:
        raise HTTPException(status_code=404, detail="角色不存在")
    return detail


@router.patch("/{role_id}", response_model=RoleDetail)
async def update_role(role_id: str, data: RoleUpdate, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    try:
        role = await svc.update(role_id, data)
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    await db.commit()
    detail = await svc.build_detail(role_id)
    assert detail is not None
    return detail


@router.patch("/{role_id}/briefing", response_model=RoleDetail)
async def save_briefing(role_id: str, data: BriefingSaveRequest, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    try:
        detail = await svc.save_briefing(role_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    await db.commit()
    return detail


@router.post("/{role_id}/briefing/regenerate", response_model=RoleDetail)
async def regenerate_briefing(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    try:
        detail = await svc.regenerate_briefing(role_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    await db.commit()
    return detail


@router.post("/{role_id}/to-test", response_model=RoleDetail)
async def move_to_test(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    try:
        detail = await svc.save_briefing(role_id, BriefingSaveRequest())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    await db.commit()
    return detail


@router.post("/{role_id}/publish", response_model=RoleDetail)
async def publish_role(
    role_id: str,
    user: CurrentUser,
    published_by: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    try:
        role = await svc.publish(role_id, published_by or user.username)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    await db.commit()
    detail = await svc.build_detail(role_id)
    assert detail is not None
    return detail


@router.post("/{role_id}/archive", response_model=RoleDetail)
async def archive_role(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    role = await svc.archive(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    await db.commit()
    detail = await svc.build_detail(role_id)
    assert detail is not None
    return detail


@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    ok = await svc.delete(role_id)
    if not ok:
        raise HTTPException(status_code=404, detail="角色不存在")
    await db.commit()
