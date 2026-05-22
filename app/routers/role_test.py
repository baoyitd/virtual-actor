"""角色测试路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.services.test_service import TestService
from app.schemas.test_run import TestRunCreate, TestRunOut, TestRunRating

router = APIRouter(tags=["角色测试"], dependencies=[Depends(get_current_user)])


@router.post("/role-assets/{role_id}/test", response_model=TestRunOut)
async def run_test(role_id: str, data: TestRunCreate, db: AsyncSession = Depends(get_db)):
    svc = TestService(db)
    record = await svc.run_test(role_id, data.test_input)
    if not record:
        raise HTTPException(status_code=404, detail="角色不存在")
    await db.commit()
    return TestRunOut(
        id=record.id,
        role_id=record.role_id,
        version_id=record.version_id,
        test_input=record.test_input,
        test_output=record.test_output,
        knowledge_retrieved=record.knowledge_retrieved or [],
        tested_at=record.tested_at,
    )


@router.get("/role-assets/{role_id}/tests", response_model=list[TestRunOut])
async def get_test_history(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = TestService(db)
    records = await svc.get_test_history(role_id)
    return [
        TestRunOut(
            id=r.id,
            role_id=r.role_id,
            version_id=r.version_id,
            test_input=r.test_input,
            test_output=r.test_output,
            knowledge_retrieved=r.knowledge_retrieved or [],
            human_rating=r.human_rating,
            tested_at=r.tested_at,
        )
        for r in records
    ]


@router.post("/test-runs/{test_id}/rate", response_model=TestRunOut)
async def rate_test(test_id: str, data: TestRunRating, db: AsyncSession = Depends(get_db)):
    svc = TestService(db)
    record = await svc.rate_test(test_id, data.human_rating)
    if not record:
        raise HTTPException(status_code=404, detail="测试记录不存在")
    await db.commit()
    return TestRunOut(
        id=record.id,
        role_id=record.role_id,
        version_id=record.version_id,
        test_input=record.test_input,
        test_output=record.test_output,
        knowledge_retrieved=record.knowledge_retrieved or [],
        human_rating=record.human_rating,
        tested_at=record.tested_at,
    )
