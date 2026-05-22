"""角色 CRUD + 状态迁移"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role_asset import RoleAsset
from app.models.role_version import RoleVersion, RoleVersionField
from app.models.knowledge_ref import KnowledgeRef, ValidatedKnowledgeVersion
from app.models.test_run import TestRunRecord
from app.schemas.role import RoleCreate, RoleUpdate, RoleStatus, Layer


class RoleService:
    """角色资产管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ──── CRUD ────

    async def create(self, data: RoleCreate) -> RoleAsset:
        role = RoleAsset(
            name=data.name,
            bio=data.bio,
            tags=data.tags or [],
        )
        self.db.add(role)
        await self.db.flush()

        # 创建第一个版本（draft）
        version = RoleVersion(
            role_id=role.id,
            version_number=1,
            status="draft",
        )
        self.db.add(version)
        await self.db.flush()

        # 写入版本字段快照
        await self._save_fields(version.id, data)

        role.current_version_id = version.id
        await self.db.flush()
        return role

    async def get(self, role_id: str) -> RoleAsset | None:
        stmt = (
            select(RoleAsset)
            .where(RoleAsset.id == role_id)
            .options(selectinload(RoleAsset.knowledge_refs))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_test_stats(self, role_id: str) -> dict | None:
        """获取角色 + 测试统计"""
        role = await self.get(role_id)
        if not role:
            return None

        # 测试统计
        test_stmt = select(TestRunRecord).where(TestRunRecord.role_id == role_id)
        test_result = await self.db.execute(test_stmt)
        tests = test_result.scalars().all()

        return {
            "role": role,
            "has_test_record": len(tests) > 0,
            "latest_test_rating": max((t.human_rating for t in tests if t.human_rating), default=None),
            "latest_tested_at": max((t.tested_at for t in tests if t.tested_at), default=None),
            "test_run_count": len(tests),
        }

    async def update(self, role_id: str, data: RoleUpdate) -> RoleAsset | None:
        role = await self.get(role_id)
        if not role:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if role.status == RoleStatus.PUBLISHED.value and role.current_version_id:
            await self._fork_current_version(role, update_data)
            role.status = RoleStatus.DRAFT.value

        # 分离 RoleAsset 字段和版本字段
        asset_fields = {"name", "bio", "tags"}
        asset_update = {k: v for k, v in update_data.items() if k in asset_fields}
        if asset_update:
            asset_update["updated_at"] = datetime.now(timezone.utc)
            stmt = update(RoleAsset).where(RoleAsset.id == role_id).values(**asset_update)
            await self.db.execute(stmt)

        # 更新版本字段快照
        version_fields = {
            k: v for k, v in update_data.items()
            if k not in asset_fields and k != "model_binding"
        }
        if data.model_binding:
            version_fields["model_binding"] = data.model_binding.model_dump()

        snapshot_fields = {k: v for k, v in update_data.items() if k in asset_fields}
        version_fields.update(snapshot_fields)

        if version_fields and role.current_version_id:
            await self._update_fields(role.current_version_id, version_fields)

        await self.db.flush()
        return await self.get(role_id)

    async def list_by_status(self, status: RoleStatus | None = None) -> list[RoleAsset]:
        stmt = select(RoleAsset).options(selectinload(RoleAsset.knowledge_refs))
        if status:
            stmt = stmt.where(RoleAsset.status == status.value)
        stmt = stmt.order_by(RoleAsset.updated_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ──── 状态迁移 ────

    async def change_status(self, role_id: str, new_status: RoleStatus) -> RoleAsset | None:
        role = await self.get(role_id)
        if not role:
            return None
        role.status = new_status.value
        role.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return role

    async def publish(self, role_id: str, published_by: str = "system") -> RoleAsset | None:
        """发布角色：状态 → published，版本生成 publish 记录"""
        role = await self.get(role_id)
        if not role or not role.current_version_id:
            return None
        if not role.knowledge_refs:
            raise ValueError("发布前至少需要绑定 1 条知识")

        test_stmt = select(TestRunRecord).where(
            TestRunRecord.role_id == role_id,
            TestRunRecord.version_id == role.current_version_id,
        )
        test_result = await self.db.execute(test_stmt)
        if not test_result.scalars().first():
            raise ValueError("发布前至少需要完成 1 次角色测试")

        role.status = RoleStatus.PUBLISHED.value
        role.updated_at = datetime.now(timezone.utc)

        # 更新版本发布信息
        stmt = (
            update(RoleVersion)
            .where(RoleVersion.id == role.current_version_id)
            .values(
                status=RoleStatus.PUBLISHED.value,
                published_at=datetime.now(timezone.utc),
                published_by=published_by,
            )
        )
        await self.db.execute(stmt)

        from sqlalchemy import delete as sa_delete
        await self.db.execute(
            sa_delete(ValidatedKnowledgeVersion).where(
                ValidatedKnowledgeVersion.version_id == role.current_version_id
            )
        )
        for ref in role.knowledge_refs:
            if not ref.knowledge_version_id:
                raise ValueError("存在未记录知识版本的绑定，无法发布")
            self.db.add(
                ValidatedKnowledgeVersion(
                    version_id=role.current_version_id,
                    knowledge_object_id=ref.knowledge_object_id,
                    knowledge_version_id=ref.knowledge_version_id,
                )
            )
        await self.db.flush()
        return role

    async def archive(self, role_id: str) -> RoleAsset | None:
        role = await self.get(role_id)
        if not role:
            return None
        role.status = RoleStatus.ARCHIVED.value
        role.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return role

    async def delete(self, role_id: str) -> bool:
        role = await self.get(role_id)
        if not role:
            return False
        await self.db.delete(role)
        await self.db.flush()
        return True

    # ──── 版本字段 ────

    LAYER_MAP = {
        "name": Layer.L1_IDENTITY,
        "bio": Layer.L1_IDENTITY,
        "tags": Layer.L1_IDENTITY,
        "identity_background": Layer.L2_MIND,
        "point_of_view": Layer.L2_MIND,
        "decision_style": Layer.L2_MIND,
        "responsibility_boundary": Layer.L2_MIND,
        "speaking_style": Layer.L2_MIND,
        "knowledge_boundary": Layer.L3_KNOWLEDGE,
        "collaboration_mode": Layer.L4_CAPABILITY,
        "capability_boundary": Layer.L4_CAPABILITY,
        "model_binding": Layer.L5_CONFIG,
        "memory_strategy": Layer.L5_CONFIG,
    }

    async def _save_fields(self, version_id: str, data: RoleCreate | RoleUpdate) -> None:
        fields_to_save = {
            "name": data.name,
            "bio": data.bio,
            "tags": data.tags or [],
            "model_binding": data.model_binding.model_dump(),
        }
        for attr in [
            "identity_background", "point_of_view", "decision_style",
            "responsibility_boundary", "speaking_style",
            "collaboration_mode", "capability_boundary",
        ]:
            val = getattr(data, attr, None)
            if val is not None:
                fields_to_save[attr] = val

        for field_name, field_value in fields_to_save.items():
            layer = self.LAYER_MAP.get(field_name, Layer.L2_MIND)
            f = RoleVersionField(
                version_id=version_id,
                layer=layer.value,
                field_name=field_name,
                field_value=field_value,
            )
            self.db.add(f)
        await self.db.flush()

    async def _update_fields(self, version_id: str, fields: dict) -> None:
        """更新已有版本的字段值"""
        from sqlalchemy import delete as sa_delete
        for field_name, field_value in fields.items():
            layer = self.LAYER_MAP.get(field_name, Layer.L2_MIND)
            # 删除旧值
            await self.db.execute(
                sa_delete(RoleVersionField).where(
                    RoleVersionField.version_id == version_id,
                    RoleVersionField.field_name == field_name,
                )
            )
            # 插入新值
            f = RoleVersionField(
                version_id=version_id,
                layer=layer.value,
                field_name=field_name,
                field_value=field_value,
            )
            self.db.add(f)
        await self.db.flush()

    async def _fork_current_version(self, role: RoleAsset, updates: dict) -> None:
        """已发布版本不可覆写；编辑时派生新的草稿版本并设为当前版本。"""
        current_fields = await self.get_version_fields(role.current_version_id)
        max_stmt = select(func.max(RoleVersion.version_number)).where(RoleVersion.role_id == role.id)
        max_result = await self.db.execute(max_stmt)
        next_number = (max_result.scalar_one() or 0) + 1

        new_version = RoleVersion(
            role_id=role.id,
            version_number=next_number,
            status=RoleStatus.DRAFT.value,
            change_note="由已发布版本编辑派生",
        )
        self.db.add(new_version)
        await self.db.flush()

        current_fields.update({k: v for k, v in updates.items() if k not in {"model_binding"}})
        if "model_binding" in updates and updates["model_binding"] is not None:
            mb = updates["model_binding"]
            current_fields["model_binding"] = mb.model_dump() if hasattr(mb, "model_dump") else mb
        for field_name, field_value in current_fields.items():
            layer = self.LAYER_MAP.get(field_name, Layer.L2_MIND)
            self.db.add(
                RoleVersionField(
                    version_id=new_version.id,
                    layer=layer.value,
                    field_name=field_name,
                    field_value=field_value,
                )
            )
        role.current_version_id = new_version.id

    async def get_version_fields(self, version_id: str) -> dict:
        """读取版本字段快照，组装为字典"""
        stmt = select(RoleVersionField).where(RoleVersionField.version_id == version_id)
        result = await self.db.execute(stmt)
        fields = result.scalars().all()
        data = {}
        for f in fields:
            data[f.field_name] = f.field_value
        return data
