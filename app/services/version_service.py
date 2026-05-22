"""版本管理 + 发布逻辑"""
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role_version import RoleVersion
from app.models.knowledge_ref import ValidatedKnowledgeVersion


class VersionService:
    """角色版本管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_published_version(self, role_id: str) -> RoleVersion | None:
        stmt = (
            select(RoleVersion)
            .where(
                RoleVersion.role_id == role_id,
                RoleVersion.status == "published",
            )
            .order_by(RoleVersion.version_number.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, version_id: str) -> RoleVersion | None:
        stmt = (
            select(RoleVersion)
            .where(RoleVersion.id == version_id)
            .options(selectinload(RoleVersion.validated_knowledge))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_versions(self, role_id: str) -> list[RoleVersion]:
        stmt = (
            select(RoleVersion)
            .where(RoleVersion.role_id == role_id)
            .order_by(RoleVersion.version_number.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_new_version(self, role_id: str, previous_version: RoleVersion) -> RoleVersion:
        """基于前一个版本创建新草稿版本"""
        new_version = RoleVersion(
            role_id=role_id,
            version_number=previous_version.version_number + 1,
            status="draft",
        )
        self.db.add(new_version)
        await self.db.flush()
        return new_version

    async def save_validated_knowledge(
        self, version_id: str, knowledge_versions: list[dict]
    ) -> None:
        """保存知识版本溯源记录"""
        from sqlalchemy import delete as sa_delete
        await self.db.execute(
            sa_delete(ValidatedKnowledgeVersion).where(
                ValidatedKnowledgeVersion.version_id == version_id
            )
        )
        for kv in knowledge_versions:
            vk = ValidatedKnowledgeVersion(
                version_id=version_id,
                knowledge_object_id=kv.get("knowledge_object_id", ""),
                knowledge_version_id=kv.get("knowledge_version_id", ""),
            )
            self.db.add(vk)
        await self.db.flush()