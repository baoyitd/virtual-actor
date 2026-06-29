"""FastAPI 应用主入口"""
import asyncio
import logging
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app.routers import (
    auth,
    config,
    data_assets,
    role_ai,
    role_assets,
    role_consume,
    role_dashboard,
    role_exports,
    role_knowledge,
    role_marketplace,
    role_test,
    role_versions,
)

# ── 日志 ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("virtual-actor")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时运行 Alembic 迁移，关闭时释放数据库连接"""
    if os.getenv("DB_TESTING") != "1":
        project_root = Path(__file__).resolve().parent.parent
        command = [sys.executable, "-m", "alembic", "upgrade", "head"]
        last_error = ""
        for attempt in range(1, 6):
            result = subprocess.run(
                command,
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                logger.info("数据库迁移已完成")
                break

            last_error = (result.stderr or result.stdout).strip()
            if attempt < 5:
                logger.warning("数据库迁移第 %s 次尝试失败，3s 后重试: %s", attempt, last_error)
                await asyncio.sleep(3)
                continue

            logger.error("数据库迁移失败: %s", last_error)
            raise RuntimeError("数据库迁移失败，应用启动已阻断")

        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            from app.routers.config import seed_config_data
            await seed_config_data(session)

    yield
    await engine.dispose()
    logger.info("数据库连接已释放")


app = FastAPI(
    title="Virtual Actor — 角色产品",
    description="虚拟角色资产管理 API",
    version="0.5.1",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 统一异常处理中间件 ──

@app.middleware("http")
async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException:
        raise  # FastAPI 自行处理 HTTPException
    except Exception as e:
        logger.exception(f"未捕获异常: {request.method} {request.url.path}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"服务器内部错误: {str(e)}"},
        )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"全局异常: {request.method} {request.url.path}")
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误"})


app.include_router(role_consume.router)
app.include_router(role_ai.router)
app.include_router(role_marketplace.router)
app.include_router(role_dashboard.router)
app.include_router(auth.router)
app.include_router(role_assets.router)
app.include_router(role_versions.router)
app.include_router(role_test.router)
app.include_router(role_knowledge.router)
app.include_router(role_exports.router)
app.include_router(data_assets.router)
app.include_router(config.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "virtual-actor", "version": "0.5.1"}


@app.get("/health/knowledge-platform")
async def knowledge_platform_health():
    from app.services.knowledge_platform import knowledge_platform
    ok = await knowledge_platform.health()
    return {"knowledge_platform": "reachable" if ok else "unreachable"}


# React 正式用户入口；prototype 仅保留为迁移参考，不再作为用户入口。
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
static_dir = frontend_dist if os.path.exists(frontend_dist) else "frontend/dist"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
