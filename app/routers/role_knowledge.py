"""角色知识绑定路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.schemas.knowledge import (
    KnowledgeBaseItem,
    KnowledgeCatalogItem,
    KnowledgeRefCreate,
    KnowledgeRefOut,
)
from app.services.knowledge_platform import knowledge_platform
from app.services.role_service import RoleService

router = APIRouter(tags=["角色知识绑定"], dependencies=[Depends(get_current_user)])


@router.get("/knowledge/bases", response_model=list[KnowledgeBaseItem])
async def knowledge_bases():
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
    if not await knowledge_platform.health():
        raise HTTPException(status_code=503, detail="知识平台不可达，无法浏览知识")
    knowledge_bases = await knowledge_platform.list_knowledge_bases()
    target_kb_id = await knowledge_platform.resolve_runtime_kb_id(
        kb_id or knowledge_platform.default_package_id,
        knowledge_bases=knowledge_bases,
    )
    if not target_kb_id:
        raise HTTPException(status_code=503, detail="当前没有可用的知识库")
    version_id = await knowledge_platform.current_version_id()
    files = await knowledge_platform.list_files(target_kb_id)
    return [
        KnowledgeCatalogItem(**knowledge_platform.normalize_file(item, target_kb_id, version_id))
        for item in files
    ]


@router.get("/role-assets/{role_id}/knowledge", response_model=list[KnowledgeRefOut])
async def list_knowledge(role_id: str, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    role = await svc.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    refs = await svc.get_knowledge_refs(role.current_version_id, role.id)
    return [
        KnowledgeRefOut(
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
        for ref in refs
    ]


@router.post("/role-assets/{role_id}/knowledge", response_model=KnowledgeRefOut, status_code=201)
async def bind_knowledge(role_id: str, data: KnowledgeRefCreate, db: AsyncSession = Depends(get_db)):
    svc = RoleService(db)
    role = await svc.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if not await knowledge_platform.health():
        raise HTTPException(status_code=503, detail="知识平台不可达，无法绑定知识")

    knowledge_version_id = data.knowledge_version_id or await knowledge_platform.current_version_id()
    if not knowledge_version_id:
        raise HTTPException(status_code=503, detail="无法获取知识平台版本标识")

    knowledge_bases = await knowledge_platform.list_knowledge_bases()
    target_kb_id = await knowledge_platform.resolve_runtime_kb_id(
        data.kb_id or knowledge_platform.default_package_id,
        knowledge_object_id=data.knowledge_object_id,
        knowledge_bases=knowledge_bases,
    )
    if not target_kb_id:
        raise HTTPException(status_code=400, detail="无法解析知识库标识，请重新选择知识库")

    ref = await svc.bind_knowledge(
        role_id=role_id,
        kb_id=target_kb_id,
        knowledge_object_id=data.knowledge_object_id,
        knowledge_version_id=knowledge_version_id,
        title=data.title,
        kind=data.type,
    )
    assert ref is not None
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
    svc = RoleService(db)
    ok = await svc.unbind_knowledge(role_id, knowledge_ref_id)
    if not ok:
        raise HTTPException(status_code=404, detail="绑定记录不存在")
    await db.commit()
