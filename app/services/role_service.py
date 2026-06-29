"""v0.5 角色 CRUD、版本、门禁与详情聚合服务"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.data_asset import DataAsset
from app.models.knowledge_ref import KnowledgeRef, ValidatedKnowledgeVersion
from app.models.role_asset import RoleAsset
from app.models.role_version import RoleVersion, RoleVersionField
from app.models.test_run import TestRunRecord
from app.models.test_validation_record import TestValidationRecord
from app.schemas.role import (
    BriefingSaveRequest,
    DataAssetBindingSummary,
    DataCapabilitySummary,
    KnowledgeBindingInput,
    KnowledgeStatusSummary,
    Layer,
    LegacyInfo,
    ModelBinding,
    OutputMode,
    ProgressItem,
    ReadinessPanel,
    RequirementItem,
    RoleCreate,
    RoleDetail,
    RoleListItem,
    RoleStatus,
    RoleUpdate,
    RoleVersionPublicResponse,
    RoleWorkspaceSummary,
    ValidationSummary,
)
from app.services.briefing_service import BriefingService
from app.services.data_asset_service import DataAssetService
from app.services.knowledge_platform import knowledge_platform


class RoleService:
    VERSION_FIELD_NAMES = {
        "name",
        "bio",
        "tags",
        "main_duty_cluster",
        "point_of_view",
        "decision_style",
        "identity_background",
        "speaking_style",
        "knowledge_boundary",
        "data_asset_binding_ids",
        "output_mode",
        "output_type",
        "output_schema",
        "model_binding",
    }
    ASSET_FIELD_NAMES = {
        "name",
        "bio",
        "tags",
        "category",
        "owner",
        "maintainer",
        "business_domain",
        "visibility",
        "enterprise_role_mapping",
    }
    LEGACY_FIELDS = {
        "responsibility_boundary",
        "capability_boundary",
        "capability_level",
        "collaboration_mode",
    }
    LAYER_MAP = {
        "name": Layer.L1,
        "bio": Layer.L1,
        "tags": Layer.L1,
        "main_duty_cluster": Layer.L1,
        "point_of_view": Layer.L1,
        "decision_style": Layer.L1,
        "identity_background": Layer.L1,
        "speaking_style": Layer.L1,
        "knowledge_boundary": Layer.L2,
        "data_asset_binding_ids": Layer.L3,
        "output_mode": Layer.L4,
        "output_type": Layer.L4,
        "output_schema": Layer.L4,
        "model_binding": Layer.L4,
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.briefing_service = BriefingService(db)
        self.data_asset_service = DataAssetService(db)

    async def create(self, data: RoleCreate, creation_source: str = "manual") -> RoleAsset:
        await self.data_asset_service.ensure_existing(data.data_asset_binding_ids or [])
        role = RoleAsset(
            name=data.name,
            bio=data.bio,
            tags=data.tags or [],
            category=data.category,
            owner=data.owner or "",
            maintainer=data.maintainer,
            business_domain=data.business_domain,
            visibility=data.visibility,
            creation_source=creation_source,
            enterprise_role_mapping=data.enterprise_role_mapping or [],
        )
        self.db.add(role)
        await self.db.flush()

        version = RoleVersion(role_id=role.id, version_number=1, status=RoleStatus.DRAFT.value)
        self.db.add(version)
        await self.db.flush()

        await self._save_fields(version.id, self._payload_to_field_dict(data))
        role.current_version_id = version.id
        if data.knowledge_bindings:
            await self._replace_knowledge_refs(role, data.knowledge_bindings)

        if any(
            [
                data.applicable_scenarios,
                data.usage_notes,
                data.support_basis_summary,
            ]
        ):
            await self.save_briefing(
                role.id,
                BriefingSaveRequest(
                    applicable_scenarios=data.applicable_scenarios,
                    usage_notes=data.usage_notes,
                    support_basis_summary=data.support_basis_summary,
                ),
                promote_to_test=False,
            )
        await self.db.flush()
        return role

    async def get(self, role_id: str) -> RoleAsset | None:
        role = await self.db.get(RoleAsset, role_id)
        if role:
            await self.db.refresh(role)
        return role

    async def delete(self, role_id: str) -> bool:
        role = await self.get(role_id)
        if not role:
            return False
        await self.db.delete(role)
        await self.db.flush()
        return True

    async def list_by_status(
        self,
        status: RoleStatus | None = None,
        category: str | None = None,
        owner: str | None = None,
        business_domain: str | None = None,
        visibility: str | None = None,
    ) -> list[RoleAsset]:
        stmt = select(RoleAsset).order_by(RoleAsset.updated_at.desc())
        if status:
            stmt = stmt.where(RoleAsset.status == status.value)
        if category:
            stmt = stmt.where(RoleAsset.category == category)
        if owner:
            stmt = stmt.where(RoleAsset.owner == owner)
        if business_domain:
            stmt = stmt.where(RoleAsset.business_domain == business_domain)
        if visibility:
            stmt = stmt.where(RoleAsset.visibility == visibility)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_with_published_version(
        self,
        category: str | None = None,
        business_domain: str | None = None,
    ) -> list[tuple[RoleAsset, RoleVersion]]:
        roles = await self.list_by_status(category=category, business_domain=business_domain)
        pairs: list[tuple[RoleAsset, RoleVersion]] = []
        for role in roles:
            if role.status == RoleStatus.ARCHIVED.value:
                continue
            published = await self.get_latest_published_version(role.id)
            if published:
                pairs.append((role, published))
        return pairs

    async def update(self, role_id: str, data: RoleUpdate | dict) -> RoleAsset | None:
        role = await self.get(role_id)
        if not role:
            return None

        update_data = (
            data.model_dump(exclude_unset=True) if isinstance(data, RoleUpdate) else dict(data)
        )
        if not update_data:
            return role

        knowledge_bindings_provided = "knowledge_bindings" in update_data
        knowledge_bindings = update_data.pop("knowledge_bindings", None)
        version_updates = {k: v for k, v in update_data.items() if k in self.VERSION_FIELD_NAMES}
        asset_updates = {k: v for k, v in update_data.items() if k in self.ASSET_FIELD_NAMES}

        if version_updates or knowledge_bindings_provided:
            role = await self.ensure_editable_version(role)
            await self._set_role_status(role, RoleStatus.DRAFT)
            if "data_asset_binding_ids" in version_updates:
                await self.data_asset_service.ensure_existing(version_updates.get("data_asset_binding_ids") or [])

        if knowledge_bindings_provided:
            await self._replace_knowledge_refs(role, knowledge_bindings or [])
            if not knowledge_bindings:
                version_updates["knowledge_boundary"] = None

        if "model_binding" in version_updates:
            version_updates["model_binding"] = self._serialize_model_binding(version_updates.get("model_binding"))

        for key, value in asset_updates.items():
            setattr(role, key, value)
        role.updated_at = datetime.now(timezone.utc)

        if "knowledge_boundary" in version_updates and role.current_version_id:
            current_refs = await self.get_knowledge_refs(role.current_version_id, role.id)
            if not current_refs:
                version_updates["knowledge_boundary"] = None

        if version_updates and role.current_version_id:
            await self._update_fields(role.current_version_id, version_updates)
            if {"name", "bio", "tags"} & set(version_updates):
                role.name = update_data.get("name", role.name)
                role.bio = update_data.get("bio", role.bio)
                role.tags = update_data.get("tags", role.tags)

        await self.db.flush()
        return role

    async def change_status(self, role_id: str, new_status: RoleStatus) -> RoleAsset | None:
        role = await self.get(role_id)
        if not role:
            return None
        await self._set_role_status(role, new_status)
        await self.db.flush()
        return role

    async def archive(self, role_id: str) -> RoleAsset | None:
        return await self.change_status(role_id, RoleStatus.ARCHIVED)

    async def publish(self, role_id: str, published_by: str = "system") -> RoleAsset | None:
        role = await self.get(role_id)
        if not role or not role.current_version_id:
            return None
        if role.status == RoleStatus.ARCHIVED.value:
            raise ValueError("已归档角色需先重新形成可编辑版本，再执行发布")

        detail = await self.build_detail(role.id)
        if not detail.publish_readiness.ready:
            reasons = [item.label for item in detail.publish_readiness.hard_requirements if item.status != "met"]
            raise ValueError(f"发布前仍有未闭合项：{', '.join(reasons)}")

        current_version = await self.get_current_version(role)
        await self._set_role_status(role, RoleStatus.PUBLISHED)
        if current_version:
            current_version.published_at = datetime.now(timezone.utc)
            current_version.published_by = published_by

        await self.db.execute(
            sa_delete(ValidatedKnowledgeVersion).where(
                ValidatedKnowledgeVersion.version_id == role.current_version_id
            )
        )
        knowledge_refs = await self.get_knowledge_refs(role.current_version_id, role.id)
        for ref in knowledge_refs:
            if ref.knowledge_version_id:
                self.db.add(
                    ValidatedKnowledgeVersion(
                        version_id=role.current_version_id,
                        knowledge_object_id=ref.knowledge_object_id,
                        knowledge_version_id=ref.knowledge_version_id,
                    )
                )
        await self.db.flush()
        return role

    async def ensure_editable_version(self, role: RoleAsset) -> RoleAsset:
        current_version = await self.get_current_version(role)
        if not current_version or current_version.status not in {
            RoleStatus.PUBLISHED.value,
            RoleStatus.ARCHIVED.value,
        }:
            return role

        new_version = RoleVersion(
            role_id=role.id,
            version_number=current_version.version_number + 1,
            status=RoleStatus.DRAFT.value,
        )
        self.db.add(new_version)
        await self.db.flush()

        await self._copy_fields(current_version.id, new_version.id)
        await self._copy_knowledge_refs(current_version.id, new_version.id, role.id)
        await self._copy_briefing(current_version.id, new_version.id)

        role.current_version_id = new_version.id
        role.status = RoleStatus.DRAFT.value
        role.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return role

    async def get_current_version(self, role: RoleAsset) -> RoleVersion | None:
        if not role.current_version_id:
            return None
        return await self.db.get(RoleVersion, role.current_version_id)

    async def get_latest_published_version(self, role_id: str) -> RoleVersion | None:
        stmt = (
            select(RoleVersion)
            .where(RoleVersion.role_id == role_id, RoleVersion.status == RoleStatus.PUBLISHED.value)
            .order_by(RoleVersion.version_number.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_version_by_id(self, version_id: str) -> RoleVersion | None:
        version = await self.db.get(RoleVersion, version_id)
        if version:
            await self.db.refresh(version)
        return version

    async def list_versions(self, role_id: str) -> list[RoleVersion]:
        stmt = (
            select(RoleVersion)
            .where(RoleVersion.role_id == role_id)
            .order_by(RoleVersion.version_number.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_version_fields(self, version_id: str | None) -> dict:
        if not version_id:
            return self._normalize_fields({})
        stmt = select(RoleVersionField).where(RoleVersionField.version_id == version_id)
        result = await self.db.execute(stmt)
        fields = {row.field_name: row.field_value for row in result.scalars().all()}
        return self._normalize_fields(fields)

    async def get_knowledge_refs(self, version_id: str | None, role_id: str) -> list[KnowledgeRef]:
        if version_id:
            stmt = (
                select(KnowledgeRef)
                .where(KnowledgeRef.role_id == role_id, KnowledgeRef.version_id == version_id)
                .order_by(KnowledgeRef.bound_at.desc())
            )
            result = await self.db.execute(stmt)
            refs = list(result.scalars().all())
            if refs:
                await self._hydrate_runtime_kb_ids(refs)
                return refs

        legacy_stmt = (
            select(KnowledgeRef)
            .where(KnowledgeRef.role_id == role_id, KnowledgeRef.version_id.is_(None))
            .order_by(KnowledgeRef.bound_at.desc())
        )
        result = await self.db.execute(legacy_stmt)
        refs = list(result.scalars().all())
        if refs:
            await self._hydrate_runtime_kb_ids(refs)
        return refs

    async def bind_knowledge(
        self,
        role_id: str,
        kb_id: str,
        knowledge_object_id: str,
        knowledge_version_id: str | None,
        title: str | None,
        kind: str | None,
    ) -> KnowledgeRef | None:
        role = await self.get(role_id)
        if not role:
            return None
        role = await self.ensure_editable_version(role)
        ref = KnowledgeRef(
            role_id=role.id,
            version_id=role.current_version_id,
            kb_id=kb_id,
            knowledge_object_id=knowledge_object_id,
            knowledge_version_id=knowledge_version_id,
            title=title,
            type=kind,
            knowledge_source="knowledge-platform",
            bound_at=datetime.now(timezone.utc),
        )
        self.db.add(ref)
        await self.db.flush()
        return ref

    async def _replace_knowledge_refs(
        self,
        role: RoleAsset,
        bindings: list[KnowledgeBindingInput] | list[dict],
    ) -> None:
        if not role.current_version_id:
            raise ValueError("角色当前版本不存在，无法保存知识绑定")

        await self.db.execute(
            sa_delete(KnowledgeRef).where(
                KnowledgeRef.role_id == role.id,
                KnowledgeRef.version_id == role.current_version_id,
            )
        )

        normalized_bindings = self._normalize_knowledge_bindings(bindings)
        if not normalized_bindings:
            await self.db.flush()
            return

        if not await knowledge_platform.health():
            raise ConnectionError("知识平台不可达，无法保存知识绑定")

        default_version_id = await knowledge_platform.current_version_id()
        if not default_version_id:
            raise ConnectionError("无法获取知识平台版本标识，无法保存知识绑定")

        knowledge_bases = await knowledge_platform.list_knowledge_bases()
        bound_at = datetime.now(timezone.utc)

        for item in normalized_bindings:
            target_kb_id = await knowledge_platform.resolve_runtime_kb_id(
                item.kb_id or knowledge_platform.default_package_id,
                knowledge_object_id=item.knowledge_object_id,
                knowledge_bases=knowledge_bases,
            )
            if not target_kb_id:
                raise ValueError("无法解析知识库标识，请重新选择知识库")

            self.db.add(
                KnowledgeRef(
                    role_id=role.id,
                    version_id=role.current_version_id,
                    kb_id=target_kb_id,
                    knowledge_object_id=item.knowledge_object_id,
                    knowledge_version_id=item.knowledge_version_id or default_version_id,
                    title=item.title,
                    type=item.type,
                    knowledge_source="knowledge-platform",
                    bound_at=bound_at,
                )
            )
        await self.db.flush()

    async def unbind_knowledge(self, role_id: str, knowledge_ref_id: str) -> bool:
        role = await self.get(role_id)
        if not role:
            return False
        role = await self.ensure_editable_version(role)
        stmt = sa_delete(KnowledgeRef).where(
            KnowledgeRef.id == knowledge_ref_id,
            KnowledgeRef.role_id == role_id,
            KnowledgeRef.version_id == role.current_version_id,
        )
        result = await self.db.execute(stmt)
        if result.rowcount and role.current_version_id:
            remaining = await self.get_knowledge_refs(role.current_version_id, role.id)
            if not remaining:
                await self._update_fields(role.current_version_id, {"knowledge_boundary": None})
        await self.db.flush()
        return bool(result.rowcount)

    async def _hydrate_runtime_kb_ids(self, refs: list[KnowledgeRef]) -> None:
        """运行态解析 kb_id 供展示使用，不落库。"""
        bases = await knowledge_platform.list_knowledge_bases()
        if not bases:
            return
        for ref in refs:
            resolved = knowledge_platform.resolve_runtime_kb_id_from_bases(
                ref.kb_id,
                knowledge_object_id=ref.knowledge_object_id,
                knowledge_bases=bases,
            )
            if resolved and resolved != ref.kb_id:
                ref.kb_id = resolved

    async def get_bound_data_assets(self, fields: dict) -> list[DataAsset]:
        binding_ids = fields.get("data_asset_binding_ids") or []
        return await self.data_asset_service.resolve_many(binding_ids)

    async def save_briefing(
        self,
        role_id: str,
        payload: BriefingSaveRequest,
        *,
        promote_to_test: bool = True,
    ) -> RoleDetail:
        role = await self.get(role_id)
        if not role:
            raise ValueError("角色不存在")
        role = await self.ensure_editable_version(role)
        fields = await self.get_version_fields(role.current_version_id)
        detail = await self.build_detail(role.id)
        generated = self.briefing_service.build_generated_payload(
            role=role,
            fields=fields,
            knowledge_status=detail.briefing.knowledge_status,
            data_status=detail.briefing.data_capability_status,
            validation_summary=detail.briefing.validation_summary,
        )
        source_hash = self.briefing_service.compute_source_hash(
            role=role,
            fields=fields,
            knowledge_refs=await self.get_knowledge_refs(role.current_version_id, role.id),
            data_assets=await self.get_bound_data_assets(fields),
            validation_summary=detail.briefing.validation_summary,
        )
        saved = await self.briefing_service.get_saved(role.current_version_id)
        scenarios = (
            list(payload.applicable_scenarios)
            if payload.applicable_scenarios is not None
            else list((saved.applicable_scenarios if saved else generated["applicable_scenarios"]) or [])
        )
        usage_notes = (
            payload.usage_notes
            if payload.usage_notes is not None
            else (saved.usage_notes if saved else generated["usage_notes"])
        )
        support_basis_summary = (
            payload.support_basis_summary
            if payload.support_basis_summary is not None
            else (
                saved.support_basis_summary if saved else generated["support_basis_summary"]
            )
        )

        if payload.confirm_current and saved:
            scenarios = list(saved.applicable_scenarios or [])
            usage_notes = saved.usage_notes
            support_basis_summary = saved.support_basis_summary

        await self.briefing_service.save(
            role.current_version_id,
            applicable_scenarios=scenarios,
            usage_notes=usage_notes,
            support_basis_summary=support_basis_summary,
            source_hash=source_hash,
            generated_payload=generated,
        )
        if promote_to_test:
            self._validate_test_entry(fields)
            await self._set_role_status(role, RoleStatus.TEST)
        return await self.build_detail(role.id)

    async def regenerate_briefing(self, role_id: str) -> RoleDetail:
        role = await self.get(role_id)
        if not role:
            raise ValueError("角色不存在")
        role = await self.ensure_editable_version(role)
        fields = await self.get_version_fields(role.current_version_id)
        knowledge_refs = await self.get_knowledge_refs(role.current_version_id, role.id)
        data_assets = await self.get_bound_data_assets(fields)
        validation_summary = await self.get_validation_summary(role.id, role.current_version_id)
        knowledge_status = await self._build_knowledge_status(knowledge_refs)
        data_status = self._build_data_status(data_assets)
        generated = self.briefing_service.build_generated_payload(
            role=role,
            fields=fields,
            knowledge_status=knowledge_status,
            data_status=data_status,
            validation_summary=validation_summary,
        )
        await self.briefing_service.save(
            role.current_version_id,
            applicable_scenarios=generated["applicable_scenarios"],
            usage_notes=generated["usage_notes"],
            support_basis_summary=generated["support_basis_summary"],
            source_hash=await self._current_briefing_source_hash(role),
            generated_payload=generated,
        )
        return await self.build_detail(role.id)

    async def build_detail(self, role_id: str) -> RoleDetail | None:
        role = await self.get(role_id)
        if not role:
            return None
        fields = await self.get_version_fields(role.current_version_id)
        knowledge_refs = await self.get_knowledge_refs(role.current_version_id, role.id)
        data_assets = await self.get_bound_data_assets(fields)
        validation_summary = await self.get_validation_summary(role.id, role.current_version_id)
        knowledge_status = await self._build_knowledge_status(knowledge_refs)
        data_status = self._build_data_status(data_assets)
        source_hash = self.briefing_service.compute_source_hash(
            role, fields, knowledge_refs, data_assets, validation_summary
        )
        saved_briefing = await self.briefing_service.get_saved(role.current_version_id) if role.current_version_id else None
        briefing = self.briefing_service.build_view(
            role=role,
            fields=fields,
            saved_briefing=saved_briefing,
            knowledge_status=knowledge_status,
            data_status=data_status,
            validation_summary=validation_summary,
            current_source_hash=source_hash,
        )
        definition_progress = self._build_definition_progress(fields, knowledge_status, data_status, briefing)
        share_readiness = self._build_share_readiness(role, fields, briefing)
        publish_readiness = self._build_publish_readiness(role, fields, briefing, validation_summary)
        legacy = self._build_legacy_info(fields, briefing)
        validated = []
        if role.current_version_id:
            result = await self.db.execute(
                select(ValidatedKnowledgeVersion).where(
                    ValidatedKnowledgeVersion.version_id == role.current_version_id
                )
            )
            validated = result.scalars().all()
        published_version = await self.get_latest_published_version(role.id)
        stats = await self.get_with_test_stats(role.id, role.current_version_id)

        return RoleDetail(
            role_id=role.id,
            role_version_id=role.current_version_id,
            published_version_id=published_version.id if published_version else None,
            name=fields.get("name") or role.name,
            bio=fields.get("bio") or role.bio,
            tags=fields.get("tags") or role.tags or [],
            status=RoleStatus(role.status),
            category=role.category,
            owner=role.owner or "",
            maintainer=role.maintainer,
            business_domain=role.business_domain,
            visibility=role.visibility,
            creation_source=role.creation_source,
            enterprise_role_mapping=list(role.enterprise_role_mapping or []),
            main_duty_cluster=fields.get("main_duty_cluster"),
            point_of_view=fields.get("point_of_view"),
            decision_style=fields.get("decision_style"),
            identity_background=fields.get("identity_background"),
            speaking_style=fields.get("speaking_style"),
            knowledge_boundary=fields.get("knowledge_boundary"),
            output_mode=OutputMode(fields.get("output_mode", OutputMode.FREEFORM.value)),
            output_type=fields.get("output_type"),
            output_schema=fields.get("output_schema"),
            model_binding=self._normalize_model_binding(fields.get("model_binding")),
            knowledge_refs=[
                {
                    "id": ref.id,
                    "role_id": ref.role_id,
                    "kb_id": ref.kb_id,
                    "knowledge_object_id": ref.knowledge_object_id,
                    "knowledge_version_id": ref.knowledge_version_id,
                    "title": ref.title,
                    "type": ref.type,
                    "knowledge_source": ref.knowledge_source,
                    "bound_at": ref.bound_at,
                }
                for ref in knowledge_refs
            ],
            validated_knowledge_versions=[
                {
                    "knowledge_object_id": item.knowledge_object_id,
                    "knowledge_version_id": item.knowledge_version_id,
                }
                for item in validated
            ],
            data_asset_bindings=[
                DataAssetBindingSummary(
                    id=asset.id,
                    display_name=asset.display_name,
                    datasource_ref=asset.datasource_ref,
                    database_name=asset.database_name,
                    table_name=asset.table_name,
                    scope_summary=asset.scope_summary,
                    freshness=asset.freshness,
                    owner_team=asset.owner_team,
                    status=asset.status,
                )
                for asset in data_assets
            ],
            briefing=briefing,
            definition_progress=definition_progress,
            share_readiness=share_readiness,
            publish_readiness=publish_readiness,
            legacy=legacy,
            has_test_record=stats["has_test_record"],
            latest_test_rating=stats["latest_test_rating"],
            latest_tested_at=stats["latest_tested_at"],
            latest_validation_status=validation_summary.latest_status,
            test_run_count=stats["test_run_count"],
            created_at=role.created_at,
            updated_at=role.updated_at,
        )

    async def build_workbench_summary(self, role_id: str) -> RoleWorkspaceSummary | None:
        detail = await self.build_detail(role_id)
        if not detail:
            return None
        return RoleWorkspaceSummary(
            role_id=detail.role_id,
            role_version_id=detail.role_version_id,
            status=detail.status,
            definition_progress=detail.definition_progress,
            share_readiness=detail.share_readiness,
            publish_readiness=detail.publish_readiness,
            legacy=detail.legacy,
        )

    async def build_version_public_detail(self, version_id: str) -> RoleVersionPublicResponse | None:
        version = await self.get_version_by_id(version_id)
        if not version:
            return None
        role = await self.get(version.role_id)
        if not role:
            return None
        fields = await self.get_version_fields(version.id)
        knowledge_refs = await self.get_knowledge_refs(version.id, role.id)
        data_assets = await self.get_bound_data_assets(fields)
        validation_summary = await self.get_validation_summary(role.id, version.id)
        knowledge_status = await self._build_knowledge_status(knowledge_refs)
        data_status = self._build_data_status(data_assets)
        source_hash = self.briefing_service.compute_source_hash(
            role, fields, knowledge_refs, data_assets, validation_summary
        )
        saved_briefing = await self.briefing_service.get_saved(version.id)
        briefing = self.briefing_service.build_view(
            role=role,
            fields=fields,
            saved_briefing=saved_briefing,
            knowledge_status=knowledge_status,
            data_status=data_status,
            validation_summary=validation_summary,
            current_source_hash=source_hash,
        )
        result = await self.db.execute(
            select(ValidatedKnowledgeVersion).where(ValidatedKnowledgeVersion.version_id == version.id)
        )
        validated = result.scalars().all()

        return RoleVersionPublicResponse(
            role_id=role.id,
            role_version_id=version.id,
            name=fields.get("name") or role.name,
            summary=fields.get("bio") or role.bio,
            business_domain=role.business_domain,
            main_duty_cluster=fields.get("main_duty_cluster"),
            point_of_view=fields.get("point_of_view"),
            knowledge_boundary=fields.get("knowledge_boundary"),
            output_mode=OutputMode(fields.get("output_mode", OutputMode.FREEFORM.value)),
            output_type=fields.get("output_type"),
            output_schema=fields.get("output_schema"),
            model_binding=self._normalize_model_binding(fields.get("model_binding")),
            data_asset_bindings=[
                DataAssetBindingSummary(
                    id=asset.id,
                    display_name=asset.display_name,
                    datasource_ref=asset.datasource_ref,
                    database_name=asset.database_name,
                    table_name=asset.table_name,
                    scope_summary=asset.scope_summary,
                    freshness=asset.freshness,
                    owner_team=asset.owner_team,
                    status=asset.status,
                )
                for asset in data_assets
            ],
            briefing=briefing,
            knowledge_refs=[
                {
                    "id": ref.id,
                    "role_id": ref.role_id,
                    "knowledge_object_id": ref.knowledge_object_id,
                    "knowledge_version_id": ref.knowledge_version_id,
                    "title": ref.title,
                    "type": ref.type,
                    "knowledge_source": ref.knowledge_source,
                    "bound_at": ref.bound_at,
                }
                for ref in knowledge_refs
            ],
            validated_knowledge_versions=[
                {
                    "knowledge_object_id": item.knowledge_object_id,
                    "knowledge_version_id": item.knowledge_version_id,
                }
                for item in validated
            ],
            has_test_record=validation_summary.has_record,
            latest_tested_at=validation_summary.latest_tested_at,
            test_run_count=validation_summary.total_count,
        )

    async def get_with_test_stats(self, role_id: str, version_id: str | None = None) -> dict:
        validation_stmt = select(TestValidationRecord).where(TestValidationRecord.role_asset_id == role_id)
        test_run_stmt = select(TestRunRecord).where(TestRunRecord.role_id == role_id)
        if version_id:
            validation_stmt = validation_stmt.where(TestValidationRecord.role_version_id == version_id)
            test_run_stmt = test_run_stmt.where(TestRunRecord.version_id == version_id)
        validation_result = await self.db.execute(validation_stmt)
        test_result = await self.db.execute(test_run_stmt)
        validations = validation_result.scalars().all()
        test_runs = test_result.scalars().all()

        latest_tested_candidates = [
            *(item.created_at for item in validations if item.created_at),
            *(item.tested_at for item in test_runs if item.tested_at),
        ]
        latest_tested_at = max(latest_tested_candidates) if latest_tested_candidates else None
        latest_rating = max((item.human_rating for item in test_runs if item.human_rating), default=None)
        return {
            "has_test_record": bool(validations or test_runs),
            "latest_test_rating": latest_rating,
            "latest_tested_at": latest_tested_at,
            "test_run_count": len(validations) + len(test_runs),
        }

    async def get_validation_summary(self, role_id: str, version_id: str | None) -> ValidationSummary:
        stats = await self.get_with_test_stats(role_id, version_id)
        latest_validation_status = None
        if version_id:
            stmt = (
                select(TestValidationRecord)
                .where(
                    TestValidationRecord.role_asset_id == role_id,
                    TestValidationRecord.role_version_id == version_id,
                )
                .order_by(TestValidationRecord.created_at.desc())
            )
            result = await self.db.execute(stmt)
            latest = result.scalars().first()
            if latest:
                latest_validation_status = latest.status
        return ValidationSummary(
            has_record=stats["has_test_record"],
            latest_status=latest_validation_status,
            latest_tested_at=stats["latest_tested_at"],
            total_count=stats["test_run_count"],
        )

    async def _save_fields(self, version_id: str, fields: dict) -> None:
        for field_name, field_value in fields.items():
            if field_name not in self.VERSION_FIELD_NAMES:
                continue
            if field_value is None:
                continue
            self.db.add(
                RoleVersionField(
                    version_id=version_id,
                    layer=self.LAYER_MAP[field_name].value,
                    field_name=field_name,
                    field_value=field_value,
                )
            )
        await self.db.flush()

    async def _update_fields(self, version_id: str, fields: dict) -> None:
        for field_name, field_value in fields.items():
            if field_name not in self.VERSION_FIELD_NAMES:
                continue
            await self.db.execute(
                sa_delete(RoleVersionField).where(
                    RoleVersionField.version_id == version_id,
                    RoleVersionField.field_name == field_name,
                )
            )
            if field_value is not None:
                self.db.add(
                    RoleVersionField(
                        version_id=version_id,
                        layer=self.LAYER_MAP[field_name].value,
                        field_name=field_name,
                        field_value=field_value,
                    )
                )
        await self.db.flush()

    async def _copy_fields(self, source_version_id: str, target_version_id: str) -> None:
        stmt = select(RoleVersionField).where(RoleVersionField.version_id == source_version_id)
        result = await self.db.execute(stmt)
        for field in result.scalars().all():
            self.db.add(
                RoleVersionField(
                    version_id=target_version_id,
                    layer=field.layer,
                    field_name=field.field_name,
                    field_value=field.field_value,
                )
            )
        await self.db.flush()

    async def _copy_knowledge_refs(self, source_version_id: str, target_version_id: str, role_id: str) -> None:
        refs = await self.get_knowledge_refs(source_version_id, role_id)
        for ref in refs:
            self.db.add(
                KnowledgeRef(
                    role_id=role_id,
                    version_id=target_version_id,
                    kb_id=ref.kb_id,
                    knowledge_object_id=ref.knowledge_object_id,
                    knowledge_version_id=ref.knowledge_version_id,
                    title=ref.title,
                    type=ref.type,
                    knowledge_source=ref.knowledge_source,
                    bound_at=ref.bound_at,
                )
            )
        await self.db.flush()

    async def _copy_briefing(self, source_version_id: str, target_version_id: str) -> None:
        saved = await self.briefing_service.get_saved(source_version_id)
        if not saved:
            return
        await self.briefing_service.save(
            version_id=target_version_id,
            applicable_scenarios=list(saved.applicable_scenarios or []),
            usage_notes=saved.usage_notes,
            support_basis_summary=saved.support_basis_summary,
            source_hash=saved.source_hash,
            generated_payload=saved.last_generated_payload or {},
        )

    def _payload_to_field_dict(self, data: RoleCreate) -> dict:
        model_binding = self._serialize_model_binding(data.model_binding)
        return {
            "name": data.name,
            "bio": data.bio,
            "tags": data.tags or [],
            "main_duty_cluster": data.main_duty_cluster,
            "point_of_view": data.point_of_view,
            "decision_style": data.decision_style,
            "identity_background": data.identity_background,
            "speaking_style": data.speaking_style,
            "knowledge_boundary": data.knowledge_boundary if data.knowledge_bindings else None,
            "data_asset_binding_ids": data.data_asset_binding_ids or [],
            "output_mode": data.output_mode.value,
            "output_type": data.output_type,
            "output_schema": data.output_schema,
            "model_binding": model_binding,
        }

    def _normalize_knowledge_bindings(
        self,
        bindings: list[KnowledgeBindingInput] | list[dict],
    ) -> list[KnowledgeBindingInput]:
        normalized: list[KnowledgeBindingInput] = []
        seen: set[tuple[str | None, str]] = set()
        for raw in bindings:
            item = raw if isinstance(raw, KnowledgeBindingInput) else KnowledgeBindingInput(**raw)
            key = (item.kb_id, item.knowledge_object_id)
            if key in seen:
                continue
            seen.add(key)
            normalized.append(item)
        return normalized

    def _normalize_fields(self, fields: dict) -> dict:
        normalized = dict(fields)
        normalized.setdefault("tags", [])
        normalized.setdefault("data_asset_binding_ids", [])
        normalized.setdefault("output_mode", OutputMode.FREEFORM.value)
        normalized["model_binding"] = self._serialize_model_binding(normalized.get("model_binding"))
        return normalized

    def _default_model_binding(self) -> ModelBinding:
        return ModelBinding(
            model_provider=settings.LLM_PROVIDER or "openai",
            model_name=settings.AI_CREATE_MODEL or "deepseek-v4-pro",
            temperature=0.3,
            max_tokens=4096,
            fallback_enabled=False,
            inherited=True,
        )

    def _serialize_model_binding(self, raw: ModelBinding | dict | None) -> dict:
        raw_dict = raw.model_dump(exclude_none=True) if isinstance(raw, ModelBinding) else dict(raw or {})
        normalized = self._normalize_model_binding(raw_dict)
        explicit_model_name = str(raw_dict.get("model_name") or "").strip()
        has_model_override = bool(explicit_model_name and explicit_model_name != "default" and not bool(raw_dict.get("inherited", False)))

        payload = {
            "temperature": normalized.temperature,
            "max_tokens": normalized.max_tokens,
            "fallback_enabled": bool(normalized.fallback_enabled),
            "inherited": not has_model_override,
        }
        if has_model_override:
            payload["model_name"] = normalized.model_name
        return payload

    def _normalize_model_binding(self, raw: dict | None) -> ModelBinding:
        payload = self._default_model_binding().model_dump()
        if isinstance(raw, dict):
            passthrough_keys = ("temperature", "max_tokens", "fallback_enabled")
            for key in passthrough_keys:
                if raw.get(key) is not None:
                    payload[key] = raw[key]

            raw_model_name = str(raw.get("model_name") or "").strip()
            inherits_system_model = bool(raw.get("inherited", False)) or not raw_model_name or raw_model_name == "default"
            if not inherits_system_model:
                payload["model_name"] = raw_model_name

            payload["inherited"] = inherits_system_model
        return ModelBinding(**payload)

    async def _build_knowledge_status(self, knowledge_refs: list[KnowledgeRef]) -> KnowledgeStatusSummary:
        if not knowledge_refs:
            return KnowledgeStatusSummary(
                state="unbound",
                label="未绑定真实知识",
                detail="当前未绑定真实知识，运行时会如实表达知识限制。",
            )
        tier_counts = await knowledge_platform.get_tier_distribution(knowledge_refs)
        tier_detail = ""
        if tier_counts:
            tier_parts = [f"{count}篇{tier}" for tier, count in sorted(tier_counts.items())]
            tier_detail = f"（含{'、'.join(tier_parts)}）"
        return KnowledgeStatusSummary(
            state="bound",
            label="已绑定真实知识",
            detail=f"已绑定 {len(knowledge_refs)} 条知识项{tier_detail}，发布时将记录知识版本追溯。",
            tier_summary=tier_counts or None,
        )

    def _build_data_status(self, data_assets: list[DataAsset]) -> DataCapabilitySummary:
        if not data_assets:
            return DataCapabilitySummary(
                state="unbound",
                label="未授权结构化业务数据",
                detail="当前未授权结构化业务数据，运行时不会隐式取数。",
            )
        active = [asset for asset in data_assets if asset.status == "active"]
        inactive = [asset for asset in data_assets if asset.status != "active"]
        detail = f"已绑定 {len(data_assets)} 条数据资产，当前可用 {len(active)} 条。"
        if inactive:
            detail += " 存在已停用资产，运行时会如实降级。"
        return DataCapabilitySummary(
            state="bound",
            label="已授权结构化业务数据",
            detail=detail,
        )

    def _build_definition_progress(
        self,
        fields: dict,
        knowledge_status: KnowledgeStatusSummary,
        data_status: DataCapabilitySummary,
        briefing,
    ) -> list[ProgressItem]:
        l1_complete = bool(fields.get("main_duty_cluster"))
        structured_ready = True
        if fields.get("output_mode") == OutputMode.STRUCTURED.value:
            structured_ready = bool(fields.get("output_type")) and bool(fields.get("output_schema"))
        return [
            ProgressItem(
                key="l1",
                label="L1 身份与判断",
                state="complete" if l1_complete else "missing",
                detail="核心职责已明确" if l1_complete else "需补齐核心职责。",
            ),
            ProgressItem(
                key="l2",
                label="L2 知识依据",
                state="complete" if knowledge_status.state == "bound" else "empty",
                detail=knowledge_status.detail,
            ),
            ProgressItem(
                key="l3",
                label="L3 数据能力（可选）",
                state="complete" if data_status.state == "bound" else "empty",
                detail=data_status.detail,
            ),
            ProgressItem(
                key="l4",
                label="L4 输出方式与运行",
                state="complete" if structured_ready else "missing",
                detail=(
                    "输出方式已明确。"
                    if structured_ready
                    else "已选择结构化输出，但还缺少 output_type 或 output_schema。"
                ),
            ),
            ProgressItem(
                key="briefing",
                label="使用前说明与调用预览",
                state="complete" if self._is_briefing_fresh(briefing.status) else getattr(briefing.status, "value", briefing.status),
                detail=briefing.source_hint,
            ),
        ]

    def _build_share_readiness(self, role: RoleAsset, fields: dict, briefing) -> ReadinessPanel:
        hard = [
            self._requirement("main_duty_cluster", "核心职责", bool(fields.get("main_duty_cluster")), "workspace", "identity"),
            self._requirement("owner", "Owner", bool(role.owner), "publish", None),
            self._requirement("business_domain", "业务域", bool(role.business_domain), "publish", None),
            self._requirement("category", "分类", bool(role.category), "publish", None),
            self._requirement("applicable_scenarios", "适用场景", bool(briefing.applicable_scenarios), "briefing", None),
            self._requirement("usage_notes", "使用说明", bool(briefing.usage_notes), "briefing", None),
            self._requirement(
                "support_basis_summary",
                "可信依据摘要",
                bool(briefing.support_basis_summary),
                "briefing",
                None,
            ),
            self._requirement(
                "briefing_fresh",
                "说明卡需确认更新",
                self._is_briefing_fresh(briefing.status),
                "briefing",
                None,
            ),
        ]
        soft = [
            self._hint("point_of_view", "分析视角", bool(fields.get("point_of_view")), "workspace", "identity"),
            self._hint(
                "enterprise_role_mapping",
                "企业实际角色映射",
                bool(role.enterprise_role_mapping),
                "publish",
                None,
            ),
        ]
        return ReadinessPanel(
            stage="share",
            ready=all(item.status == "met" for item in hard),
            hard_requirements=hard,
            soft_hints=soft,
        )

    def _build_publish_readiness(
        self,
        role: RoleAsset,
        fields: dict,
        briefing,
        validation_summary: ValidationSummary,
    ) -> ReadinessPanel:
        structured_ready = True
        if fields.get("output_mode") == OutputMode.STRUCTURED.value:
            structured_ready = bool(fields.get("output_type")) and bool(fields.get("output_schema"))
        hard = [
            self._requirement("main_duty_cluster", "核心职责", bool(fields.get("main_duty_cluster")), "workspace", "identity"),
            self._requirement("owner", "Owner", bool(role.owner), "publish", None),
            self._requirement("business_domain", "业务域", bool(role.business_domain), "publish", None),
            self._requirement("category", "分类", bool(role.category), "publish", None),
            self._requirement("applicable_scenarios", "适用场景", bool(briefing.applicable_scenarios), "briefing", None),
            self._requirement("usage_notes", "使用说明", bool(briefing.usage_notes), "briefing", None),
            self._requirement(
                "support_basis_summary",
                "可信依据摘要",
                bool(briefing.support_basis_summary),
                "briefing",
                None,
            ),
            self._requirement("has_test_record", "至少一次角色测试", validation_summary.has_record, "publish", None),
            self._requirement(
                "structured_contract",
                "结构化输出契约",
                structured_ready,
                "workspace",
                "output",
            ),
            self._requirement(
                "briefing_fresh",
                "说明卡需确认更新",
                self._is_briefing_fresh(briefing.status),
                "briefing",
                None,
            ),
        ]
        soft = [
            self._hint("point_of_view", "分析视角", bool(fields.get("point_of_view")), "workspace", "identity"),
            self._hint(
                "enterprise_role_mapping",
                "企业实际角色映射",
                bool(role.enterprise_role_mapping),
                "publish",
                None,
            ),
        ]
        return ReadinessPanel(
            stage="publish",
            ready=all(item.status == "met" for item in hard),
            hard_requirements=hard,
            soft_hints=soft,
        )

    def _build_legacy_info(self, fields: dict, briefing) -> LegacyInfo:
        legacy_fields = {key: value for key, value in fields.items() if key in self.LEGACY_FIELDS}
        is_legacy = bool(legacy_fields)
        missing = []
        if is_legacy:
            if not fields.get("main_duty_cluster"):
                missing.append("main_duty_cluster")
            if briefing.status == "missing":
                missing.extend(["applicable_scenarios", "usage_notes", "support_basis_summary"])
            if not fields.get("output_mode"):
                missing.append("output_mode")
        return LegacyInfo(is_legacy=is_legacy, missing_requirements=missing, legacy_fields=legacy_fields)

    def _requirement(
        self,
        key: str,
        label: str,
        ok: bool,
        route_screen: str | None,
        route_step: str | None,
    ) -> RequirementItem:
        return RequirementItem(
            key=key,
            label=label,
            status="met" if ok else "missing",
            message="已满足" if ok else f"需补齐 {label}",
            route_screen=route_screen,
            route_step=route_step,
        )

    def _hint(
        self,
        key: str,
        label: str,
        ok: bool,
        route_screen: str | None,
        route_step: str | None,
    ) -> RequirementItem:
        return RequirementItem(
            key=key,
            label=label,
            status="met" if ok else "attention",
            message="已补齐" if ok else f"建议补齐 {label}",
            route_screen=route_screen,
            route_step=route_step,
        )

    def _validate_test_entry(self, fields: dict) -> None:
        if not fields.get("main_duty_cluster"):
            raise ValueError("进入测试前需先补齐核心职责")

    async def _set_role_status(self, role: RoleAsset, new_status: RoleStatus) -> None:
        role.status = new_status.value
        current_version = await self.get_current_version(role)
        if current_version:
            current_version.status = new_status.value
            current_version.is_deprecated = new_status == RoleStatus.ARCHIVED
        role.updated_at = datetime.now(timezone.utc)

    async def _current_briefing_source_hash(self, role: RoleAsset) -> str:
        fields = await self.get_version_fields(role.current_version_id)
        knowledge_refs = await self.get_knowledge_refs(role.current_version_id, role.id)
        data_assets = await self.get_bound_data_assets(fields)
        validation_summary = await self.get_validation_summary(role.id, role.current_version_id)
        return self.briefing_service.compute_source_hash(
            role, fields, knowledge_refs, data_assets, validation_summary
        )

    async def get_briefing_source_hash_for_version(self, role_id: str, version_id: str) -> str:
        role = await self.get(role_id)
        if not role:
            raise ValueError("角色不存在")
        fields = await self.get_version_fields(version_id)
        knowledge_refs = await self.get_knowledge_refs(version_id, role.id)
        data_assets = await self.get_bound_data_assets(fields)
        validation_summary = await self.get_validation_summary(role.id, version_id)
        return self.briefing_service.compute_source_hash(
            role, fields, knowledge_refs, data_assets, validation_summary
        )

    def _is_briefing_fresh(self, status) -> bool:
        return getattr(status, "value", status) == "fresh"
