"""版本相关路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.schemas.role import RoleVersionPublicResponse
from app.schemas.version import PublishedVersionOut, VersionListItem
from app.services.role_service import RoleService

router = APIRouter(tags=["角色版本"], dependencies=[Depends(get_current_user)])


@router.get("/role-assets/{role_id}/published-version", response_model=PublishedVersionOut)
async def get_published_version(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    version = await svc.get_latest_published_version(role_id)
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
    svc = RoleService(db)
    detail = await svc.build_version_public_detail(version_id)
    if not detail:
        raise HTTPException(status_code=404, detail="版本不存在")
    return detail


@router.get("/role-assets/{role_id}/versions", response_model=list[VersionListItem])
async def list_versions(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    versions = await svc.list_versions(role_id)
    return [
        VersionListItem(
            role_version_id=item.id,
            version_number=item.version_number,
            status=item.status,
            published_at=item.published_at,
        )
        for item in versions
    ]
