"""统一消费 API 路由 — consume + test-consume + consume-records"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.services.consume_service import ConsumeService
from app.schemas.consume import (
    ConsumeRequest, ConsumeResponse,
    TestConsumeRequest, TestConsumeResponse,
    ConsumeRecordOut, ConsumeRecordListQuery, TestValidationRecordOut,
    ConsumeStatus, CallerType,
)

router = APIRouter(prefix="/role-assets", tags=["统一消费"], dependencies=[Depends(get_current_user)])


@router.post("/{role_id}/consume", response_model=ConsumeResponse)
async def consume_role(
    role_id: str,
    data: ConsumeRequest,
    db: AsyncSession = Depends(get_db),
):
    """统一消费 API — 仅 published 角色可消费"""
    svc = ConsumeService(db)
    result = await svc.consume(role_id, data)
    await db.commit()
    return result


@router.post("/{role_id}/test-consume", response_model=TestConsumeResponse)
async def test_consume_role(
    role_id: str,
    data: TestConsumeRequest,
    db: AsyncSession = Depends(get_db),
):
    """测试验证消费 — 仅 test 状态角色可调用"""
    svc = ConsumeService(db)
    result = await svc.test_consume(role_id, data)
    await db.commit()
    return result


@router.get("/{role_id}/consume-records", response_model=list[ConsumeRecordOut])
async def get_consume_records(
    role_id: str,
    status: ConsumeStatus | None = Query(None),
    caller_type: CallerType | None = Query(None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """消费记录查询 — 只查询 usage_records，不包含 test_validation_records"""
    svc = ConsumeService(db)
    query = ConsumeRecordListQuery(
        status=status,
        caller_type=caller_type,
        offset=offset,
        limit=limit,
    )
    return await svc.get_consume_records(role_id, query)


@router.get("/{role_id}/test-validations", response_model=list[TestValidationRecordOut])
async def get_test_validation_records(
    role_id: str,
    version_id: str | None = Query(None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """测试验证记录查询 — 只查询 test_validation_records，不包含 usage_records"""
    svc = ConsumeService(db)
    return await svc.get_test_validation_records(
        role_id,
        version_id=version_id,
        offset=offset,
        limit=limit,
    )
