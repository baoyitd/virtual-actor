"""数据资产管理服务"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_asset import DataAsset


class DataAssetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> DataAsset:
        asset = DataAsset(**kwargs)
        self.db.add(asset)
        await self.db.flush()
        return asset

    async def get(self, asset_id: str) -> DataAsset | None:
        return await self.db.get(DataAsset, asset_id)

    async def list(self, status: str | None = None) -> list[DataAsset]:
        stmt = select(DataAsset).order_by(DataAsset.updated_at.desc(), DataAsset.created_at.desc())
        if status:
            stmt = stmt.where(DataAsset.status == status)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, asset_id: str, **kwargs) -> DataAsset | None:
        asset = await self.get(asset_id)
        if not asset:
            return None
        for key, value in kwargs.items():
            setattr(asset, key, value)
        asset.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return asset

    async def resolve_many(self, asset_ids: list[str]) -> list[DataAsset]:
        if not asset_ids:
            return []
        stmt = select(DataAsset).where(DataAsset.id.in_(asset_ids))
        result = await self.db.execute(stmt)
        by_id = {asset.id: asset for asset in result.scalars().all()}
        return [by_id[asset_id] for asset_id in asset_ids if asset_id in by_id]

    async def ensure_existing(self, asset_ids: list[str]) -> list[DataAsset]:
        assets = await self.resolve_many(asset_ids)
        if len(assets) != len(set(asset_ids)):
            missing = sorted(set(asset_ids) - {asset.id for asset in assets})
            raise ValueError(f"存在未配置的数据资产项：{', '.join(missing)}")
        return assets
