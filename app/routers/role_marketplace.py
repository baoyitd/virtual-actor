"""资产市场路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.schemas.marketplace import RecommendRequest, RecommendResponse
from app.schemas.role import RoleListItem, RoleStatus
from app.services.recommend_service import _meets_pool_criteria, recommend
from app.services.role_service import RoleService

router = APIRouter(prefix="/marketplace", tags=["资产市场"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[RoleListItem])
async def marketplace_list(
    category: str | None = Query(None),
    business_domain: str | None = Query(None),
    output_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    pairs = await svc.list_with_published_version(category=category, business_domain=business_domain)
    items: list[RoleListItem] = []
    for role, published_version in pairs:
        detail = await svc.build_version_public_detail(published_version.id)
        if not detail:
            continue
        if output_type and detail.output_type != output_type:
            continue
        current = await svc.build_detail(role.id)
        if not current:
            continue
        items.append(
            RoleListItem(
                role_id=role.id,
                role_version_id=published_version.id,
                published_version_id=published_version.id,
                role_name=role.name,
                bio=role.bio,
                tags=role.tags or [],
                status=RoleStatus.PUBLISHED,
                summary=detail.main_duty_cluster or role.bio,
                model_binding=detail.model_binding,
                has_test_record=detail.has_test_record,
                latest_test_rating=None,
                latest_tested_at=detail.latest_tested_at,
                test_run_count=detail.test_run_count,
                updated_at=role.updated_at,
                category=role.category,
                owner=role.owner or "",
                visibility=role.visibility,
                business_domain=role.business_domain,
                creation_source=role.creation_source,
                output_mode=detail.output_mode,
                output_type=detail.output_type,
                briefing_status=detail.briefing.status,
                recommend_pool_eligible=_meets_pool_criteria(detail),
                legacy_incomplete=current.legacy.is_legacy and bool(current.legacy.missing_requirements),
            )
        )
    return items


@router.post("/recommend", response_model=RecommendResponse)
async def marketplace_recommend(data: RecommendRequest, db: AsyncSession = Depends(get_db)):
    return await recommend(data.intent, data.category, data.business_domain, db)
