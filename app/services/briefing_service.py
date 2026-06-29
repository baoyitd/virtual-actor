"""说明卡生成与生命周期服务"""
import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_briefing import RoleBriefing
from app.schemas.role import (
    BriefingStatus,
    DataCapabilitySummary,
    KnowledgeStatusSummary,
    OutputMode,
    OutputPreview,
    RoleBriefingView,
    ValidationSummary,
)
from app.services.output_schema_service import OUTPUT_TEMPLATES

_CONSUME_STATUS_LABELS = {
    "success": "成功返回",
    "insufficient_context": "上下文不足",
    "insufficient_knowledge": "知识不足",
    "boundary_blocked": "触发边界限制",
    "system_failed": "系统失败",
    "undefined": "未定义",
}


class BriefingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_saved(self, version_id: str) -> RoleBriefing | None:
        stmt = select(RoleBriefing).where(RoleBriefing.version_id == version_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(
        self,
        version_id: str,
        applicable_scenarios: list[str],
        usage_notes: str,
        support_basis_summary: str,
        source_hash: str,
        generated_payload: dict,
    ) -> RoleBriefing:
        briefing = await self.get_saved(version_id)
        if briefing is None:
            briefing = RoleBriefing(
                version_id=version_id,
                applicable_scenarios=applicable_scenarios,
                usage_notes=usage_notes,
                support_basis_summary=support_basis_summary,
                source_hash=source_hash,
                last_generated_payload=generated_payload,
            )
            self.db.add(briefing)
        else:
            briefing.applicable_scenarios = applicable_scenarios
            briefing.usage_notes = usage_notes
            briefing.support_basis_summary = support_basis_summary
            briefing.source_hash = source_hash
            briefing.last_generated_payload = generated_payload
            briefing.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return briefing

    def compute_source_hash(
        self,
        role,
        fields: dict,
        knowledge_refs: list,
        data_assets: list,
        validation_summary: ValidationSummary,
    ) -> str:
        payload = {
            "name": fields.get("name") or role.name,
            "bio": fields.get("bio") or role.bio,
            "main_duty_cluster": fields.get("main_duty_cluster"),
            "point_of_view": fields.get("point_of_view"),
            "decision_style": fields.get("decision_style"),
            "identity_background": fields.get("identity_background"),
            "speaking_style": fields.get("speaking_style"),
            "knowledge_boundary": fields.get("knowledge_boundary"),
            "knowledge_refs": [
                {
                    "kb_id": ref.kb_id,
                    "knowledge_object_id": ref.knowledge_object_id,
                    "knowledge_version_id": ref.knowledge_version_id,
                    "title": ref.title,
                }
                for ref in knowledge_refs
            ],
            "data_assets": [
                {
                    "id": asset.id,
                    "display_name": asset.display_name,
                    "scope_summary": asset.scope_summary,
                    "status": asset.status,
                }
                for asset in data_assets
            ],
            "output_mode": fields.get("output_mode", OutputMode.FREEFORM.value),
            "output_type": fields.get("output_type"),
            "output_schema": fields.get("output_schema"),
        }
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def build_generated_payload(
        self,
        role,
        fields: dict,
        knowledge_status: KnowledgeStatusSummary,
        data_status: DataCapabilitySummary,
        validation_summary: ValidationSummary,
    ) -> dict:
        role_name = fields.get("name") or role.name
        role_bio = fields.get("bio") or role.bio
        scenarios = self._build_scenarios(role, fields)
        usage_notes = self._build_usage_notes(role_name, fields)
        support_basis_summary = self._build_support_basis_summary(
            role_name=role_name,
            role_bio=role_bio,
            fields=fields,
            knowledge_status=knowledge_status,
            data_status=data_status,
            validation_summary=validation_summary,
        )
        return {
            "applicable_scenarios": scenarios,
            "usage_notes": usage_notes,
            "support_basis_summary": support_basis_summary,
        }

    def build_view(
        self,
        role,
        fields: dict,
        saved_briefing: RoleBriefing | None,
        knowledge_status: KnowledgeStatusSummary,
        data_status: DataCapabilitySummary,
        validation_summary: ValidationSummary,
        current_source_hash: str,
    ) -> RoleBriefingView:
        generated = self.build_generated_payload(role, fields, knowledge_status, data_status, validation_summary)
        output_preview = self._build_output_preview(fields)

        if saved_briefing is None:
            return RoleBriefingView(
                status=BriefingStatus.MISSING,
                applicable_scenarios=generated["applicable_scenarios"],
                usage_notes=generated["usage_notes"],
                support_basis_summary=generated["support_basis_summary"],
                knowledge_status=knowledge_status,
                data_capability_status=data_status,
                validation_summary=validation_summary,
                output_preview=output_preview,
                source_hint="系统已预生成说明卡草案，保存后才成为当前生效文本。",
                source_changed=False,
                saved_at=None,
            )

        source_changed = saved_briefing.source_hash != current_source_hash
        return RoleBriefingView(
            status=BriefingStatus.STALE if source_changed else BriefingStatus.FRESH,
            applicable_scenarios=list(saved_briefing.applicable_scenarios or []),
            usage_notes=saved_briefing.usage_notes,
            support_basis_summary=saved_briefing.support_basis_summary,
            knowledge_status=knowledge_status,
            data_capability_status=data_status,
            validation_summary=validation_summary,
            output_preview=output_preview,
            source_hint=(
                "说明来源已变化，需重新生成并保存，或沿用当前文字再显式保存。"
                if source_changed
                else "当前保存版说明卡与来源一致，可直接被使用前说明、发布和外供复用。"
            ),
            source_changed=source_changed,
            saved_at=saved_briefing.updated_at or saved_briefing.created_at,
        )

    def _build_scenarios(self, role, fields: dict) -> list[str]:
        seeds: list[str] = []
        duty = fields.get("main_duty_cluster") or ""
        business_domain = role.business_domain or ""
        output_type = fields.get("output_type")

        if duty:
            for piece in duty.replace("，", "、").replace("。", "、").split("、"):
                piece = piece.strip()
                if piece and len(piece) >= 4:
                    seeds.append(piece)
        if business_domain:
            seeds.append(f"{business_domain} 场景中的分析判断")
        if output_type:
            label = OUTPUT_TEMPLATES.get(output_type, {}).get("label", output_type)
            seeds.append(f"需要 {label} 输出的业务任务")
        role_bio = (fields.get("bio") or role.bio or "").strip("。")
        if role_bio:
            seeds.append(role_bio)

        deduped: list[str] = []
        for item in seeds:
            if item and item not in deduped:
                deduped.append(item)
        return deduped[:5] or ["需要先判断角色是否适合参与的业务任务"]

    def _build_usage_notes(self, role_name: str, fields: dict) -> str:
        output_mode = fields.get("output_mode", OutputMode.FREEFORM.value)
        output_type = fields.get("output_type")
        output_label = OUTPUT_TEMPLATES.get(output_type or "", {}).get("label")
        precondition = "请提供任务背景、目标对象、关键约束和你已经掌握的上下文。"
        result = "系统将以自由表达方式返回分析结论、依据和下一步建议。"
        if output_mode == OutputMode.STRUCTURED.value and output_label:
            result = f"系统将按 {output_label} 模板返回结构化结果，并保留引用依据。"
        return (
            f"面向需要调用“{role_name}”的同事或外部 AI 环境，{precondition}"
            f" 在输入信息完整、且任务与角色职责匹配时，{result}"
            " 若未绑定真实知识或数据资产，系统会如实表达限制，不把缺失能力包装成已具备。"
        )

    def _build_support_basis_summary(
        self,
        role_name: str,
        role_bio: str,
        fields: dict,
        knowledge_status: KnowledgeStatusSummary,
        data_status: DataCapabilitySummary,
        validation_summary: ValidationSummary,
    ) -> str:
        pieces = [
            f"角色“{role_name}”的定位为：{role_bio or '待补齐角色摘要'}。",
            f"核心职责：{fields.get('main_duty_cluster') or '待补齐'}。",
            f"知识状态：{knowledge_status.detail}",
            f"数据能力：{data_status.detail}",
        ]
        if validation_summary.has_record:
            pieces.append(
                f"最近验证：已完成 {validation_summary.total_count} 次测试，最近一次状态为 {_CONSUME_STATUS_LABELS.get(validation_summary.latest_status, validation_summary.latest_status or '已记录')}。"
            )
        else:
            pieces.append("最近验证：当前尚无测试记录，结论可信度应结合人工复核判断。")
        return " ".join(pieces)

    def _build_output_preview(self, fields: dict) -> OutputPreview:
        output_mode = fields.get("output_mode", OutputMode.FREEFORM.value)
        output_type = fields.get("output_type")
        if output_mode == OutputMode.STRUCTURED.value and output_type:
            template = OUTPUT_TEMPLATES.get(output_type, {})
            schema_preview = {
                "fields": list((template.get("fields") or {}).keys()),
                "label": template.get("label", output_type),
            }
            return OutputPreview(
                output_mode=OutputMode.STRUCTURED,
                output_type=output_type,
                summary=f"将返回 {template.get('label', output_type)} 模板的结构化结果。",
                schema_preview=schema_preview,
            )
        return OutputPreview(
            output_mode=OutputMode.FREEFORM,
            output_type=None,
            summary="将返回自由表达结果，默认包含结论、依据、限制和下一步建议。",
            schema_preview=None,
        )
