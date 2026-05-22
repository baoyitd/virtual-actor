"""登录与当前用户接口。"""
from fastapi import APIRouter, HTTPException

from app.auth import AuthUser, CurrentUser, LoginRequest, TokenResponse, create_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    if data.username != settings.AUTH_USERNAME or data.password != settings.AUTH_PASSWORD:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    user = AuthUser(username=data.username)
    return TokenResponse(access_token=create_token(data.username), user=user)


@router.post("/logout")
async def logout(_: CurrentUser):
    return {"status": "ok"}


@router.get("/me", response_model=AuthUser)
async def me(user: CurrentUser):
    return user
