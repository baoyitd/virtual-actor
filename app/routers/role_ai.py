"""AI 协作创建路由 — 草案生成（不落库）"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.schemas.ai_create import AIDraftRequest, AIDraftResponse
from app.services.ai_create_service import generate_draft

router = APIRouter(prefix="/role-assets", tags=["AI 协作创建"], dependencies=[Depends(get_current_user)])


@router.post("/ai-draft", response_model=AIDraftResponse)
async def ai_generate_draft(data: AIDraftRequest):
    """AI 生成角色草案（不落库），用户编辑确认后通过 POST /role-assets 保存"""
    try:
        result = await generate_draft(data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))