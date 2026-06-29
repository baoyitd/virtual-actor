"""运营看板 Schema"""
from pydantic import BaseModel


class DashboardStats(BaseModel):
    """运营看板统计数据"""
    total_roles: int = 0
    by_status: dict[str, int] = {}
    by_category: dict[str, int] = {}
    total_consume_calls: int = 0
    consume_by_status: dict[str, int] = {}
    creation_by_source: dict[str, int] = {}
    boundary_blocked_ratio: float = 0.0
    undefined_ratio: float = 0.0