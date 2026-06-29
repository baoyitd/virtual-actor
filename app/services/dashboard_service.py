"""运营看板服务 — 5 维度数据聚合"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_asset import RoleAsset
from app.models.usage_record import UsageRecord
from app.schemas.dashboard import DashboardStats


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stats(self) -> DashboardStats:
        # 资产概览
        total_stmt = select(func.count(RoleAsset.id))
        total_result = await self.db.execute(total_stmt)
        total_roles = total_result.scalar_one() or 0

        status_stmt = select(RoleAsset.status, func.count(RoleAsset.id)).group_by(RoleAsset.status)
        status_result = await self.db.execute(status_stmt)
        by_status = {row[0]: row[1] for row in status_result.all()}

        category_stmt = select(RoleAsset.category, func.count(RoleAsset.id)).group_by(RoleAsset.category)
        category_result = await self.db.execute(category_stmt)
        by_category = {row[0]: row[1] for row in category_result.all()}

        # 创建运营：creation_source 分布
        creation_stmt = select(RoleAsset.creation_source, func.count(RoleAsset.id)).group_by(RoleAsset.creation_source)
        creation_result = await self.db.execute(creation_stmt)
        creation_by_source = {row[0]: row[1] for row in creation_result.all()}

        # 消费运营：usage_records 6 状态分布
        total_consume_stmt = select(func.count(UsageRecord.id))
        total_consume_result = await self.db.execute(total_consume_stmt)
        total_consume_calls = total_consume_result.scalar_one() or 0

        consume_status_stmt = select(UsageRecord.status, func.count(UsageRecord.id)).group_by(UsageRecord.status)
        consume_status_result = await self.db.execute(consume_status_stmt)
        consume_by_status = {row[0]: row[1] for row in consume_status_result.all()}

        # 风险运营：boundary_blocked 和 undefined 比例
        if total_consume_calls > 0:
            boundary_blocked_count = consume_by_status.get("boundary_blocked", 0)
            undefined_count = consume_by_status.get("undefined", 0)
            boundary_blocked_ratio = boundary_blocked_count / total_consume_calls
            undefined_ratio = undefined_count / total_consume_calls
        else:
            boundary_blocked_ratio = 0.0
            undefined_ratio = 0.0

        return DashboardStats(
            total_roles=total_roles,
            by_status=by_status,
            by_category=by_category,
            total_consume_calls=total_consume_calls,
            consume_by_status=consume_by_status,
            creation_by_source=creation_by_source,
            boundary_blocked_ratio=boundary_blocked_ratio,
            undefined_ratio=undefined_ratio,
        )