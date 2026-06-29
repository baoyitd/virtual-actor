"""运营看板路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["运营看板"], dependencies=[Depends(get_current_user)])


@router.get("/stats", response_model=DashboardStats)
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    """运营看板 5 维度统计数据"""
    svc = DashboardService(db)
    return await svc.get_stats()