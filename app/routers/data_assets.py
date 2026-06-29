"""数据资产管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.schemas.data_asset import DataAssetCreate, DataAssetOut, DataAssetUpdate
from app.services.data_asset_service import DataAssetService

router = APIRouter(prefix="/data-assets", tags=["数据资产管理"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[DataAssetOut])
async def list_data_assets(
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    svc = DataAssetService(db)
    assets = await svc.list(status=status)
    return [DataAssetOut.model_validate(asset) for asset in assets]


@router.post("", response_model=DataAssetOut, status_code=201)
async def create_data_asset(data: DataAssetCreate, db: AsyncSession = Depends(get_db)):
    svc = DataAssetService(db)
    asset = await svc.create(**data.model_dump())
    await db.commit()
    return DataAssetOut.model_validate(asset)


@router.patch("/{asset_id}", response_model=DataAssetOut)
async def update_data_asset(asset_id: str, data: DataAssetUpdate, db: AsyncSession = Depends(get_db)):
    svc = DataAssetService(db)
    asset = await svc.update(asset_id, **data.model_dump(exclude_unset=True))
    if not asset:
        raise HTTPException(status_code=404, detail="数据资产不存在")
    await db.commit()
    return DataAssetOut.model_validate(asset)
