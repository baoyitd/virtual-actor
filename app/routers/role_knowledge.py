"""角色知识绑定路由"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.knowledge_ref import KnowledgeRef
from app.models.role_asset import RoleAsset
from app.schemas.knowledge import KnowledgeBaseItem, KnowledgeCatalogItem, KnowledgeRefOut, KnowledgeRefCreate
from app.services.knowledge_platform import knowledge_platform

router = APIRouter(tags=["角色知识绑定"], dependencies=[Depends(get_current_user)])


@router.get("/knowledge/bases", response_model=list[KnowledgeBaseItem])
async def knowledge_bases():
    """返回当前登录账号可访问的知识库列表。"""
    if not await knowledge_platform.health():
        raise HTTPException(status_code=503, detail="知识平台不可达，无法浏览知识")
    items = await knowledge_platform.list_knowledge_bases()
    bases = [
        KnowledgeBaseItem(**knowledge_platform.normalize_knowledge_base(item))
        for item in items
    ]
    return [item for item in bases if item.kb_id]


@router.get("/knowledge/catalog", response_model=list[KnowledgeCatalogItem])
async def knowledge_catalog(kb_id: str | None = None):
    """从真实知识平台读取可绑定知识列表。"""
    if not await knowledge_platform.health():
        raise HTTPException(status_code=503, detail="知识平台不可达，无法浏览知识")
    target_kb_id = kb_id or knowledge_platform.kb_eve_id
    version_id = await knowledge_platform.current_version_id()
    files = await knowledge_platform.list_files(target_kb_id)
    return [
        KnowledgeCatalogItem(**knowledge_platform.normalize_file(item, target_kb_id, version_id))
        for item in files
    ]


@router.get("/role-assets/{role_id}/knowledge", response_model=list[KnowledgeRefOut])
async def list_knowledge(role_id: str, db: AsyncSession = Depends(get_db)):
    """获取角色已绑定的知识列表"""
    stmt = select(KnowledgeRef).where(KnowledgeRef.role_id == role_id)
    result = await db.execute(stmt)
    refs = result.scalars().all()
    return [
        KnowledgeRefOut(
            id=ref.id,
            role_id=ref.role_id,
            kb_id=ref.kb_id or knowledge_platform.kb_eve_id,
            knowledge_object_id=ref.knowledge_object_id,
            knowledge_version_id=ref.knowledge_version_id,
            title=ref.title,
            type=ref.type,
            knowledge_source=ref.knowledge_source,
            bound_at=ref.bound_at,
        )
        for ref in refs
    ]


@router.post("/role-assets/{role_id}/knowledge", response_model=KnowledgeRefOut, status_code=201)
async def bind_knowledge(role_id: str, data: KnowledgeRefCreate, db: AsyncSession = Depends(get_db)):
    """为角色绑定一条知识"""
    # 验证角色存在
    role = await db.get(RoleAsset, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if not await knowledge_platform.health():
        raise HTTPException(status_code=503, detail="知识平台不可达，无法绑定知识")

    knowledge_version_id = data.knowledge_version_id or await knowledge_platform.current_version_id()
    if not knowledge_version_id:
        raise HTTPException(status_code=503, detail="无法获取知识平台版本标识")

    ref = KnowledgeRef(
        role_id=role_id,
        kb_id=data.kb_id or knowledge_platform.kb_eve_id,
        knowledge_object_id=data.knowledge_object_id,
        knowledge_version_id=knowledge_version_id,
        title=data.title,
        type=data.type,
        knowledge_source="knowledge-platform",
        bound_at=datetime.now(timezone.utc),
    )
    db.add(ref)
    await db.flush()
    await db.commit()

    return KnowledgeRefOut(
        id=ref.id,
        role_id=ref.role_id,
        kb_id=ref.kb_id,
        knowledge_object_id=ref.knowledge_object_id,
        knowledge_version_id=ref.knowledge_version_id,
        title=ref.title,
        type=ref.type,
        knowledge_source=ref.knowledge_source,
        bound_at=ref.bound_at,
    )


@router.delete("/role-assets/{role_id}/knowledge/{knowledge_ref_id}", status_code=204)
async def unbind_knowledge(role_id: str, knowledge_ref_id: str, db: AsyncSession = Depends(get_db)):
    """解除角色与知识的绑定"""
    stmt = sa_delete(KnowledgeRef).where(
        KnowledgeRef.id == knowledge_ref_id,
        KnowledgeRef.role_id == role_id,
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="绑定记录不存在")
    await db.flush()
    await db.commit()
