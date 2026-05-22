"""基础登录鉴权：内部商业试用使用的 HMAC Bearer Token。"""
import base64
import hashlib
import hmac
import json
import time
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.config import settings


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthUser(BaseModel):
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": int(time.time()) + settings.AUTH_TOKEN_TTL_HOURS * 3600,
    }
    payload_raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()
    payload_part = _b64(payload_raw)
    signature = hmac.new(
        settings.AUTH_SECRET.encode(),
        payload_part.encode(),
        hashlib.sha256,
    ).digest()
    return f"{payload_part}.{_b64(signature)}"


def verify_token(token: str) -> AuthUser:
    try:
        payload_part, signature_part = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="认证令牌格式无效") from exc

    expected = hmac.new(
        settings.AUTH_SECRET.encode(),
        payload_part.encode(),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(_b64(expected), signature_part):
        raise HTTPException(status_code=401, detail="认证令牌无效")

    try:
        payload = json.loads(_unb64(payload_part))
    except Exception as exc:
        raise HTTPException(status_code=401, detail="认证令牌无法解析") from exc

    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=401, detail="认证令牌已过期")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="认证令牌缺少用户信息")
    return AuthUser(username=username)


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    return verify_token(authorization.split(" ", 1)[1].strip())


CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
