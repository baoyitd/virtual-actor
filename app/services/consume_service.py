"""统一消费服务 — v0.5 运行态闭环"""
import json
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_version import RoleVersion
from app.models.test_validation_record import TestValidationRecord
from app.models.usage_record import UsageRecord
from app.schemas.consume import (
    ConsumeRecordListQuery,
    ConsumeRecordOut,
    ConsumeRequest,
    ConsumeResponse,
    TestValidationRecordOut,
    TestConsumeRequest,
    TestConsumeResponse,
)
from app.schemas.role import BoundaryDimension, CallerType, ConsumeStatus, OutputMode, RoleStatus
from app.services.data_runtime_service import data_runtime_service
from app.services.knowledge_platform import (
    KnowledgePlatformError,
    KnowledgePlatformRefusalError,
    knowledge_platform,
)
from app.services.llm_service import llm_service
from app.services.output_schema_service import OUTPUT_TEMPLATES, get_default_schema
from app.services.role_service import RoleService


ACTION_KEYWORDS = ["执行", "操作", "删除", "修改", "审批", "付款", "转账", "写入", "提交"]
KNOWLEDGE_REQUIRED_KEYWORDS = ["制度", "口径", "依据", "条款", "政策", "规则"]


class ConsumeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_service = RoleService(db)

    async def consume(self, role_id: str, data: ConsumeRequest) -> ConsumeResponse:
        role = await self.role_service.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色资产不存在")
        if role.status == RoleStatus.ARCHIVED.value:
            raise HTTPException(status_code=403, detail="已归档角色不支持新的正式消费")

        version = await self._resolve_published_version(role_id, data.role_version_id)
        if not version:
            raise HTTPException(status_code=403, detail="角色当前无可消费的已发布版本")

        result = await self._execute(
            role_id=role.id,
            role_name=role.name,
            role_bio=role.bio,
            version_id=version.id,
            query=data.query,
            context=data.context,
            caller_type=(data.caller_type or CallerType.HUMAN).value,
            caller_id=data.caller_id or "",
            output_type_override=data.output_type,
        )

        record = UsageRecord(
            id=str(uuid.uuid4()),
            role_asset_id=role.id,
            role_version_id=version.id,
            caller_id=data.caller_id or "",
            caller_type=(data.caller_type or CallerType.HUMAN).value,
            query=data.query,
            context=data.context or "",
            answer=result["answer"],
            structured_result=result["structured_result"],
            output_type=result["output_type"],
            status=result["status"],
            status_reason=result["status_reason"],
            boundary_status=result["boundary_status"],
            sources=result["sources"],
            knowledge_snapshot=result["knowledge_snapshot"],
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(record)
        await self.db.flush()

        return ConsumeResponse(
            status=ConsumeStatus(result["status"]),
            status_reason=result["status_reason"],
            answer=result["answer"],
            boundary_status=result["boundary_status"],
            structured_result=result["structured_result"],
            output_type=result["output_type"],
            sources=result["sources"],
            role_id=role.id,
            role_version_id=version.id,
            usage_record_id=record.id,
            created_at=datetime.now(timezone.utc),
        )

    async def test_consume(self, role_id: str, data: TestConsumeRequest) -> TestConsumeResponse:
        role = await self.role_service.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色资产不存在")
        if role.status != RoleStatus.TEST.value:
            raise HTTPException(status_code=403, detail="test-consume 只允许 test 状态角色")

        version_id = data.role_version_id or role.current_version_id
        if not version_id:
            raise HTTPException(status_code=400, detail="角色无可测试版本")
        version = await self._validate_version_ownership(role_id, version_id)

        result = await self._execute(
            role_id=role.id,
            role_name=role.name,
            role_bio=role.bio,
            version_id=version.id,
            query=data.query,
            context=data.context,
            caller_type=CallerType.HUMAN.value,
            caller_id=data.caller_id or "",
            output_type_override=data.output_type,
        )

        record = TestValidationRecord(
            id=str(uuid.uuid4()),
            role_asset_id=role.id,
            role_version_id=version.id,
            caller_id=data.caller_id or "",
            caller_type=CallerType.HUMAN.value,
            query=data.query,
            context=data.context or "",
            answer=result["answer"],
            structured_result=result["structured_result"],
            output_type=result["output_type"],
            status=result["status"],
            status_reason=result["status_reason"],
            boundary_status=result["boundary_status"],
            sources=result["sources"],
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(record)
        await self.db.flush()

        return TestConsumeResponse(
            status=ConsumeStatus(result["status"]),
            status_reason=result["status_reason"],
            answer=result["answer"],
            boundary_status=result["boundary_status"],
            structured_result=result["structured_result"],
            output_type=result["output_type"],
            sources=result["sources"],
            role_id=role.id,
            role_version_id=version.id,
            validation_record_id=record.id,
            created_at=datetime.now(timezone.utc),
        )

    async def get_consume_records(self, role_id: str, query: ConsumeRecordListQuery) -> list[ConsumeRecordOut]:
        stmt = select(UsageRecord).where(UsageRecord.role_asset_id == role_id)
        if query.status:
            stmt = stmt.where(UsageRecord.status == query.status.value)
        if query.caller_type:
            stmt = stmt.where(UsageRecord.caller_type == query.caller_type.value)
        stmt = stmt.order_by(UsageRecord.created_at.desc()).offset(query.offset).limit(query.limit)
        result = await self.db.execute(stmt)
        records = result.scalars().all()
        return [
            ConsumeRecordOut(
                id=item.id,
                role_asset_id=item.role_asset_id,
                role_version_id=item.role_version_id,
                caller_id=item.caller_id,
                caller_type=item.caller_type,
                query=item.query,
                context=item.context,
                answer=item.answer,
                structured_result=item.structured_result,
                output_type=item.output_type,
                status=item.status,
                status_reason=item.status_reason,
                boundary_status=item.boundary_status,
                sources=item.sources,
                created_at=item.created_at,
            )
            for item in records
        ]

    async def get_test_validation_records(
        self,
        role_id: str,
        version_id: str | None = None,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[TestValidationRecordOut]:
        stmt = select(TestValidationRecord).where(TestValidationRecord.role_asset_id == role_id)
        if version_id:
            stmt = stmt.where(TestValidationRecord.role_version_id == version_id)
        stmt = stmt.order_by(TestValidationRecord.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        records = result.scalars().all()
        return [
            TestValidationRecordOut(
                validation_record_id=item.id,
                role_id=item.role_asset_id,
                role_version_id=item.role_version_id,
                query=item.query,
                context=item.context,
                answer=item.answer,
                structured_result=item.structured_result,
                output_type=item.output_type,
                status=ConsumeStatus(item.status),
                status_reason=item.status_reason or "",
                boundary_status=item.boundary_status,
                sources=item.sources or [],
                created_at=item.created_at,
            )
            for item in records
        ]

    async def _resolve_published_version(self, role_id: str, version_id: str | None) -> RoleVersion | None:
        if version_id:
            version = await self._validate_version_ownership(role_id, version_id)
            if version.status != RoleStatus.PUBLISHED.value:
                raise HTTPException(status_code=403, detail="指定版本未发布，不能正式消费")
            return version
        return await self.role_service.get_latest_published_version(role_id)

    async def _validate_version_ownership(self, role_id: str, version_id: str) -> RoleVersion:
        version = await self.db.get(RoleVersion, version_id)
        if not version or version.role_id != role_id:
            raise HTTPException(status_code=400, detail="指定的版本不属于该角色")
        if version.is_deprecated:
            raise HTTPException(status_code=400, detail="指定版本不可消费（已归档）")
        return version

    async def _execute(
        self,
        role_id: str,
        role_name: str,
        role_bio: str,
        version_id: str,
        query: str,
        context: str | None,
        caller_type: str,
        caller_id: str,
        output_type_override: str | None,
    ) -> dict:
        fields = await self.role_service.get_version_fields(version_id)
        effective_role_name = fields.get("name") or role_name
        effective_role_bio = fields.get("bio") or role_bio
        if output_type_override:
            fields["output_mode"] = OutputMode.STRUCTURED.value
            fields["output_type"] = output_type_override
            if not fields.get("output_schema"):
                fields["output_schema"] = get_default_schema(output_type_override)

        knowledge_refs = await self.role_service.get_knowledge_refs(version_id, role_id)
        data_assets = await self.role_service.get_bound_data_assets(fields)

        boundary_status = {
            "knowledge_boundary": BoundaryDimension.NOT_APPLICABLE.value,
            "capability_boundary": BoundaryDimension.WITHIN_BOUNDARY.value,
        }
        if self._is_action_request(query):
            boundary_status["capability_boundary"] = BoundaryDimension.OUT_OF_SCOPE.value
            return self._response_payload(
                status=ConsumeStatus.BOUNDARY_BLOCKED.value,
                status_reason="当前角色只支持分析与建议，不支持直接执行或写入动作",
                answer="该请求涉及执行型动作，已超出当前平台角色的运行边界。",
                output_type=fields.get("output_type"),
                structured_result={},
                boundary_status=boundary_status,
                sources=[],
                knowledge_snapshot=None,
            )

        if len(query.strip()) < 4 and not (context or "").strip():
            return self._response_payload(
                status=ConsumeStatus.INSUFFICIENT_CONTEXT.value,
                status_reason="输入信息不足，无法形成可靠结果",
                answer="请补充任务背景、判断对象和关键约束后再调用该角色。",
                output_type=fields.get("output_type"),
                structured_result={},
                boundary_status=boundary_status,
                sources=[],
                knowledge_snapshot=None,
            )

        knowledge_chunks = []
        knowledge_snapshot = None
        if knowledge_refs:
            boundary_status["knowledge_boundary"] = self._evaluate_knowledge_boundary(query, fields.get("knowledge_boundary"))
            if boundary_status["knowledge_boundary"] == BoundaryDimension.OUT_OF_SCOPE.value:
                return self._response_payload(
                    status=ConsumeStatus.BOUNDARY_BLOCKED.value,
                    status_reason="请求超出当前知识边界声明范围",
                    answer="该请求超出当前角色声明的知识覆盖范围，请补充更匹配的知识绑定或换用其他角色。",
                    output_type=fields.get("output_type"),
                    structured_result={},
                    boundary_status=boundary_status,
                    sources=[],
                    knowledge_snapshot=None,
                )
            if not await knowledge_platform.health():
                return self._response_payload(
                    status=ConsumeStatus.SYSTEM_FAILED.value,
                    status_reason="知识平台不可达",
                    answer="知识平台当前不可达，暂时无法完成带知识支撑的调用。",
                    output_type=fields.get("output_type"),
                    structured_result={},
                    boundary_status=boundary_status,
                    sources=[],
                    knowledge_snapshot=None,
                )
            kb_ids = sorted({ref.kb_id for ref in knowledge_refs})
            bound_object_ids = [ref.knowledge_object_id for ref in knowledge_refs]
            try:
                knowledge_chunks = await knowledge_platform.retrieve(kb_ids, query, knowledge_object_ids=bound_object_ids)
            except KnowledgePlatformRefusalError:
                return self._response_payload(
                    status=ConsumeStatus.BOUNDARY_BLOCKED.value,
                    status_reason="知识平台路由判定当前问题越界",
                    answer="知识平台判定该请求不属于当前角色绑定知识的正式覆盖范围。",
                    output_type=fields.get("output_type"),
                    structured_result={},
                    boundary_status=boundary_status,
                    sources=[],
                    knowledge_snapshot=None,
                )
            except KnowledgePlatformError as exc:
                return self._response_payload(
                    status=ConsumeStatus.SYSTEM_FAILED.value,
                    status_reason=str(exc),
                    answer="知识检索当前失败，无法基于已绑定知识给出可靠结果，请稍后重试。",
                    output_type=fields.get("output_type"),
                    structured_result={},
                    boundary_status=boundary_status,
                    sources=[],
                    knowledge_snapshot=None,
                )
            except Exception:
                return self._response_payload(
                    status=ConsumeStatus.SYSTEM_FAILED.value,
                    status_reason="知识检索失败",
                    answer="知识检索当前失败，无法基于已绑定知识给出可靠结果，请稍后重试。",
                    output_type=fields.get("output_type"),
                    structured_result={},
                    boundary_status=boundary_status,
                    sources=[],
                    knowledge_snapshot=None,
                )
            knowledge_snapshot = {
                "kb_ids": kb_ids,
                "knowledge_object_ids": [ref.knowledge_object_id for ref in knowledge_refs],
            }
            if self._contains_knowledge_error(knowledge_chunks):
                return self._response_payload(
                    status=ConsumeStatus.SYSTEM_FAILED.value,
                    status_reason="知识检索失败",
                    answer="知识检索当前失败，无法基于已绑定知识给出可靠结果，请稍后重试。",
                    output_type=fields.get("output_type"),
                    structured_result={},
                    boundary_status=boundary_status,
                    sources=[],
                    knowledge_snapshot=None,
                )
        if not knowledge_refs and self._query_requires_knowledge(query):
            return self._response_payload(
                status=ConsumeStatus.INSUFFICIENT_KNOWLEDGE.value,
                status_reason="当前角色未绑定真实知识，无法对该类问题给出知识支撑结果",
                answer="该任务依赖真实知识或制度依据，但当前角色未绑定相关知识，请先补充知识绑定后再调用。",
                output_type=fields.get("output_type"),
                structured_result={},
                boundary_status=boundary_status,
                sources=[],
                knowledge_snapshot=None,
            )

        if knowledge_refs and not knowledge_chunks and self._query_requires_knowledge(query):
            return self._response_payload(
                status=ConsumeStatus.INSUFFICIENT_KNOWLEDGE.value,
                status_reason="已绑定知识未覆盖当前查询主题",
                answer="当前已绑定知识未覆盖该查询主题，请补充更匹配的知识后再调用。",
                output_type=fields.get("output_type"),
                structured_result={},
                boundary_status=boundary_status,
                sources=[],
                knowledge_snapshot=knowledge_snapshot,
            )

        data_findings = data_runtime_service.query(data_assets, query)
        sources = self._build_sources(knowledge_chunks, data_findings)
        fallback_answer = self._build_answer(
            role_name=effective_role_name,
            role_bio=effective_role_bio,
            fields=fields,
            query=query,
            context=context,
            knowledge_chunks=knowledge_chunks,
            data_findings=data_findings,
        )
        fallback_structured_result = self._build_structured_result(
            fields=fields,
            query=query,
            knowledge_chunks=knowledge_chunks,
            data_findings=data_findings,
            answer=fallback_answer,
        )
        llm_answer, llm_structured_result = await self._generate_with_model(
            role_name=effective_role_name,
            role_bio=effective_role_bio,
            fields=fields,
            query=query,
            context=context,
            knowledge_chunks=knowledge_chunks,
            data_findings=data_findings,
        )
        answer = self._finalize_answer(
            preferred_answer=llm_answer,
            fallback_answer=fallback_answer,
            knowledge_chunks=knowledge_chunks,
            data_findings=data_findings,
        )
        structured_result = llm_structured_result or fallback_structured_result

        return self._response_payload(
            status=ConsumeStatus.SUCCESS.value,
            status_reason="角色已按当前知识、数据和输出契约完成响应",
            answer=answer,
            output_type=fields.get("output_type"),
            structured_result=structured_result,
            boundary_status=boundary_status,
            sources=sources,
            knowledge_snapshot=knowledge_snapshot,
        )

    async def _generate_with_model(
        self,
        role_name: str,
        role_bio: str,
        fields: dict,
        query: str,
        context: str | None,
        knowledge_chunks: list[dict],
        data_findings: list[dict],
    ) -> tuple[str | None, dict | None]:
        model_binding = self.role_service._normalize_model_binding(fields.get("model_binding"))
        system_prompt = self._build_system_prompt(role_name, role_bio, fields)
        user_message = self._build_user_message(
            query=query,
            context=context,
            fields=fields,
            knowledge_chunks=knowledge_chunks,
            data_findings=data_findings,
        )

        # 第1次调用：以角色立场自由回答，产出完整自然语言原文
        llm_output = await llm_service.chat(
            system_prompt=system_prompt,
            user_message=user_message,
            model=model_binding.model_name,
            temperature=model_binding.temperature,
            max_tokens=model_binding.max_tokens,
        )
        if llm_output.startswith("[LLM 调用失败"):
            return None, None

        output_mode = fields.get("output_mode", OutputMode.FREEFORM.value)
        output_type = fields.get("output_type")

        # 自由输出模式：直接返回原文，不做结构化提取
        if output_mode != OutputMode.STRUCTURED.value or not output_type:
            return llm_output.strip(), None

        # 第2次调用：从原文中提取结构化字段
        structured_result = await self._extract_structured_result(
            raw_answer=llm_output,
            output_type=output_type,
            fields=fields,
            knowledge_chunks=knowledge_chunks,
            data_findings=data_findings,
            model_binding=model_binding,
        )

        return llm_output.strip(), structured_result

    async def _extract_structured_result(
        self,
        raw_answer: str,
        output_type: str,
        fields: dict,
        knowledge_chunks: list[dict],
        data_findings: list[dict],
        model_binding,
    ) -> dict | None:
        """第2次 LLM 调用：从自然语言原文中按模板提取结构化字段"""
        template = OUTPUT_TEMPLATES.get(output_type, {})
        required_fields = list((template.get("fields") or {}).keys())

        extraction_prompt = (
            "你是一个结构化提取器。以下是一段角色回答的原文，请从中提取结构化字段。\n\n"
            f"输出模板类型：{output_type}\n"
            f"必须包含的字段：{required_fields}\n"
            "references 必须是非空数组，体现实际依据来源（知识来源和数据来源）。\n"
            "只输出 JSON 对象，不要输出任何其他内容。"
        )

        extraction_user_message = f"角色回答原文：\n\n{raw_answer}"

        if knowledge_chunks:
            extraction_user_message += "\n\n知识来源（用于 references）：\n" + "\n".join(
                f"- {chunk.get('source', '知识平台')}（权威层级：{chunk.get('tier', '未知')}）"
                for chunk in knowledge_chunks[:3]
                if not chunk.get("error")
            )

        if data_findings:
            extraction_user_message += "\n\n数据来源（用于 references）：\n" + "\n".join(
                f"- {item['display_name']}" for item in data_findings[:3]
            )

        if fields.get("output_schema"):
            extraction_user_message += "\n\n角色级输出扩展：\n" + json.dumps(
                fields["output_schema"], ensure_ascii=False, indent=2
            )

        llm_output = await llm_service.chat(
            system_prompt=extraction_prompt,
            user_message=extraction_user_message,
            model=model_binding.model_name,
            temperature=0.1,
            max_tokens=model_binding.max_tokens,
        )

        if llm_output.startswith("[LLM 调用失败"):
            return None

        parsed = self._parse_json_response(llm_output)
        return parsed

    def _build_sources(self, knowledge_chunks: list[dict], data_findings: list[dict]) -> list[dict]:
        sources = [
            {
                "type": "knowledge",
                "source": chunk.get("source", ""),
                "title": chunk.get("title", ""),
                "score": chunk.get("score", 0),
                "tier": chunk.get("tier", ""),
                "doc_role": chunk.get("doc_role", ""),
                "evidence_type": chunk.get("evidence_type", ""),
            }
            for chunk in knowledge_chunks
            if not chunk.get("error")
        ]
        for item in data_findings:
            sources.append({"type": "data", "source": item["display_name"], "score": 1.0})
        return sources

    def _build_answer(
        self,
        role_name: str,
        role_bio: str,
        fields: dict,
        query: str,
        context: str | None,
        knowledge_chunks: list[dict],
        data_findings: list[dict],
    ) -> str:
        duty = fields.get("main_duty_cluster") or role_bio or f"{role_name} 的职责"
        sections = [f"角色视角：{role_name} 围绕“{duty}”给出如下判断。"]
        if context:
            sections.append(f"业务上下文：{context}")
        if knowledge_chunks:
            sections.append(
                "知识依据："
                + "；".join(
                    f"[{chunk.get('tier', '')}]{chunk.get('chunk', '')[:60]}"
                    for chunk in knowledge_chunks[:2]
                )
            )
        else:
            sections.append("知识依据：当前未使用到真实知识支撑，结论应结合人工复核。")
        if data_findings:
            observations = []
            for item in data_findings[:2]:
                observations.extend(item["observations"][:1])
            sections.append("数据观察：" + "；".join(observations))
        else:
            sections.append("数据观察：当前未授权或未命中结构化业务数据。")
        sections.append(
            f"结论建议：针对“{query}”，建议先确认目标、约束与可执行动作，再根据上述依据形成后续判断。"
        )
        return "\n".join(sections)

    def _build_system_prompt(self, role_name: str, role_bio: str, fields: dict) -> str:
        lines = [
            f"你是企业数字角色\u201c{role_name}\u201d。",
            f"角色摘要：{role_bio}",
            f"核心职责：{fields.get('main_duty_cluster') or '未补齐'}",
        ]
        if fields.get("point_of_view"):
            lines.append(f"分析视角：{fields['point_of_view']}")
        if fields.get("decision_style"):
            lines.append(f"决策风格：{fields['decision_style']}")
        if fields.get("identity_background"):
            lines.append(f"身份背景：{fields['identity_background']}")
        if fields.get("speaking_style"):
            lines.append(f"表达风格：{fields['speaking_style']}")
        if fields.get("knowledge_boundary"):
            lines.append(f"知识边界：{fields['knowledge_boundary']}")
        lines.extend(
            [
                "你必须如实表达知识、数据和边界限制，不能把未绑定或未命中的能力包装成已具备。",
                "回答时优先给出结论，再给依据、限制和建议动作。",
                "输出自然语言正文，不需要 JSON 包装。",
            ]
        )
        return "\n".join(lines)

    def _build_user_message(
        self,
        query: str,
        context: str | None,
        fields: dict,
        knowledge_chunks: list[dict],
        data_findings: list[dict],
    ) -> str:
        segments = [f"用户问题：{query}"]
        if context:
            segments.append(f"业务上下文：{context}")
        if knowledge_chunks:
            segments.append(
                "知识依据：\n"
                + "\n".join(
                    f"- 来源：{chunk.get('source') or '知识平台'}；权威层级：{chunk.get('tier', '未知')}；内容：{chunk.get('chunk', '')[:400]}"
                    for chunk in knowledge_chunks[:3]
                    if not chunk.get("error")
                )
            )
        else:
            segments.append("知识依据：当前未命中可用知识内容。")
        if data_findings:
            segments.append(
                "结构化业务数据：\n"
                + "\n".join(
                    f"- {item['display_name']}：{'；'.join(item['observations'][:2])}"
                    for item in data_findings[:3]
                )
            )
        else:
            segments.append("结构化业务数据：当前未授权或未命中数据资产。")

        if fields.get("output_mode") == OutputMode.STRUCTURED.value and fields.get("output_schema"):
            segments.append(
                "角色级输出扩展：\n"
                + json.dumps(fields["output_schema"], ensure_ascii=False, indent=2)
            )
        return "\n\n".join(segments)

    def _build_structured_result(
        self,
        fields: dict,
        query: str,
        knowledge_chunks: list[dict],
        data_findings: list[dict],
        answer: str,
    ) -> dict:
        output_mode = fields.get("output_mode", OutputMode.FREEFORM.value)
        output_type = fields.get("output_type")
        if output_mode != OutputMode.STRUCTURED.value or not output_type:
            return {}

        references = [
            {"source": chunk.get("source", "知识平台"), "type": "knowledge"}
            for chunk in knowledge_chunks[:3]
            if not chunk.get("error")
        ]
        references.extend(
            {"source": item["display_name"], "type": "external_data"} for item in data_findings[:3]
        )
        if not references:
            references.append({"source": "平台运行时状态", "type": "expert_opinion"})

        if output_type == "decision_advice":
            payload = {
                "position": "建议继续推进，但需先补充关键前提",
                "key_reasons": [
                    "角色职责与当前问题匹配，能够给出判断框架。",
                    "当前知识与数据状态已被如实纳入结论依据。",
                ],
                "major_risks": [
                    {"risk": "上下文仍可能不完整", "level": "medium", "mitigation": "补充目标和约束"}
                ],
                "suggested_actions": [
                    "确认业务目标与判断对象",
                    "补充缺失资料后再次复用该角色",
                ],
                "references": references,
            }
        elif output_type == "risk_analysis":
            payload = {
                "key_findings": ["当前任务存在资料完整性与执行边界两类主要风险。"],
                "risk_items": [
                    {
                        "item": "输入前提不完整可能导致判断偏差",
                        "severity": "medium",
                        "impact": "影响结论可信度",
                        "mitigation": "补充上下文后再复核",
                    }
                ],
                "overall_risk_level": "medium",
                "impact_scope": "影响本次业务判断与后续动作优先级",
                "suggested_mitigations": ["先补资料", "必要时换用更匹配的角色"],
                "references": references,
            }
        elif output_type == "policy_explanation":
            payload = {
                "applicable_clauses": [
                    {"clause": "平台消费契约", "content": "当前回答基于已绑定知识与数据能力形成"}
                ],
                "clause_explanation": "该角色会根据已绑定知识与数据范围解释制度或流程限制。",
                "allowed_actions": ["继续读取与分析", "补充上下文后再次提问"],
                "prohibited_actions": ["将当前回答等同于未绑定知识情况下的正式制度裁定"],
                "references": references,
            }
        else:
            payload = {
                "issues": [
                    {
                        "title": "输入条件仍需补充",
                        "severity": "medium",
                        "description": "当前材料足以给出初步判断，但还不能替代正式审查。",
                        "suggestion": "补齐前提和目标对象后再次审查。",
                    }
                ],
                "overall_severity": "medium",
                "references": references,
            }

        output_schema = fields.get("output_schema") or {}
        for key, value in output_schema.items():
            payload.setdefault(key, value if value not in (None, "") else "")
        return payload

    def _parse_json_response(self, llm_output: str) -> dict | None:
        """从 LLM 输出中提取 JSON 对象"""
        start = llm_output.find("{")
        end = llm_output.rfind("}") + 1
        if start == -1 or end <= start:
            return None
        try:
            parsed = json.loads(llm_output[start:end])
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, dict):
            return None
        return parsed

    def _query_requires_knowledge(self, query: str) -> bool:
        return any(keyword in query for keyword in KNOWLEDGE_REQUIRED_KEYWORDS)

    def _contains_knowledge_error(self, knowledge_chunks: list[dict]) -> bool:
        return any(isinstance(chunk, dict) and chunk.get("error") for chunk in knowledge_chunks)

    def _is_action_request(self, query: str) -> bool:
        return any(keyword in query for keyword in ACTION_KEYWORDS)

    def _evaluate_knowledge_boundary(self, query: str, boundary_text: str | None) -> str:
        if not boundary_text:
            return BoundaryDimension.WITHIN_BOUNDARY.value
        for marker in ["暂不覆盖", "不覆盖", "不包含", "不处理"]:
            if marker in boundary_text:
                excluded = boundary_text.split(marker, 1)[1]
                for token in [item.strip(" ，。；、") for item in excluded.replace("和", "、").split("、")]:
                    if token and token in query:
                        return BoundaryDimension.OUT_OF_SCOPE.value
        return BoundaryDimension.WITHIN_BOUNDARY.value

    def _response_payload(
        self,
        status: str,
        status_reason: str,
        answer: str,
        output_type: str | None,
        structured_result: dict,
        boundary_status: dict,
        sources: list[dict],
        knowledge_snapshot: dict | None,
    ) -> dict:
        return {
            "status": status,
            "status_reason": status_reason,
            "answer": answer,
            "boundary_status": boundary_status,
            "structured_result": structured_result,
            "output_type": output_type,
            "sources": sources,
            "knowledge_snapshot": knowledge_snapshot,
        }

    def _finalize_answer(
        self,
        preferred_answer: str | None,
        fallback_answer: str,
        knowledge_chunks: list[dict],
        data_findings: list[dict],
    ) -> str:
        answer = (preferred_answer or "").strip()
        if not answer:
            return fallback_answer
        return answer
