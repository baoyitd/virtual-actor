"""外供包生成服务"""
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export_package import RoleExportPackage
from app.schemas.export_package import ExportFileOut, ExportPackageOut, ExportPackageType


class ExportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_role(self, role_id: str) -> list[RoleExportPackage]:
        stmt = (
            select(RoleExportPackage)
            .where(RoleExportPackage.role_id == role_id)
            .order_by(RoleExportPackage.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get(self, package_id: str) -> RoleExportPackage | None:
        return await self.db.get(RoleExportPackage, package_id)

    async def generate(
        self,
        role,
        role_version_id: str,
        package_type: ExportPackageType,
        fields: dict,
        briefing,
        current_source_hash: str,
    ) -> RoleExportPackage:
        # 删除同类型的旧包，只保留最新一个
        from sqlalchemy import delete
        await self.db.execute(
            delete(RoleExportPackage).where(
                RoleExportPackage.role_id == role.id,
                RoleExportPackage.package_type == package_type.value,
            )
        )
        files = self._build_files(role, role_version_id, package_type, fields, briefing)
        record = RoleExportPackage(
            role_id=role.id,
            role_version_id=role_version_id,
            package_type=package_type.value,
            generation_source_hash=current_source_hash,
            files=files,
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    def to_schema(self, package: RoleExportPackage, current_source_hash: str) -> ExportPackageOut:
        is_stale = package.generation_source_hash != current_source_hash
        return ExportPackageOut(
            package_id=package.id,
            package_type=ExportPackageType(package.package_type),
            role_id=package.role_id,
            role_version_id=package.role_version_id,
            is_stale=is_stale,
            created_at=package.created_at,
            files=[
                ExportFileOut(path=path, content=content)
                for path, content in sorted((package.files or {}).items())
            ],
            stale_reason=(
                "说明卡或数据能力来源已变化，需重新生成后再对外分发。"
                if is_stale
                else None
            ),
        )

    def _build_files(self, role, role_version_id: str, package_type: ExportPackageType, fields: dict, briefing) -> dict[str, str]:
        generated_at = datetime.now(timezone.utc).isoformat()
        output_mode = fields.get("output_mode", "freeform")
        output_type = fields.get("output_type")
        output_schema = fields.get("output_schema") or {}
        role_name = fields.get("name") or role.name
        role_bio = fields.get("bio") or role.bio
        caller_type = "external_tool" if package_type == ExportPackageType.TOOL else "external_skill"
        caller_id_example = "dify-tool" if package_type == ExportPackageType.TOOL else "codex-skill"

        common_files = {
            "package-manifest.json": json.dumps(
                {
                    "package_type": package_type.value,
                    "role_id": role.id,
                    "role_version_id": role_version_id,
                    "role_name": role_name,
                    "generated_at": generated_at,
                    "briefing_source": "platform-briefing-card",
                    "data_capability_runtime": "current-effective-config",
                },
                ensure_ascii=False,
                indent=2,
            ),
            "role-brief.md": self._render_role_brief(role_name, role_bio, briefing),
            "consume-contract.json": json.dumps(
                {
                    "base_url": "{{VIRTUAL_ACTOR_BASE_URL}}",
                    "endpoint": f"/role-assets/{role.id}/consume",
                    "method": "POST",
                    "content_type": "application/json",
                    "auth": {
                        "type": "bearer",
                        "header": "Authorization",
                        "prefix": "Bearer ",
                        "env": "VIRTUAL_ACTOR_TOKEN",
                    },
                    "role_id": role.id,
                    "role_version_id": role_version_id,
                    "writeback_required": True,
                    "caller_type": caller_type,
                    "input_boundary": {
                        "required_fields": {
                            "query": "最终用户请求或待处理任务原文",
                        },
                        "optional_fields": {
                            "context": "补充背景、约束、缺失信息或调用上下文",
                            "caller_id": "外部运行环境自定义标识，用于平台侧追溯",
                            "output_type": "可选，请求级输出类型覆盖；仅在需要结构化输出时传入",
                        },
                        "fixed_fields": {
                            "role_version_id": role_version_id,
                            "caller_type": caller_type,
                        },
                        "example_body": {
                            "query": "<end-user request>",
                            "context": "<optional background and constraints>",
                            "caller_type": caller_type,
                            "caller_id": caller_id_example,
                            "role_version_id": role_version_id,
                        },
                    },
                    "output_boundary": {
                        "success_http_status": 200,
                        "success_body_fields": [
                            "status",
                            "status_reason",
                            "answer",
                            "boundary_status",
                            "structured_result",
                            "output_type",
                            "sources",
                            "role_id",
                            "role_version_id",
                            "usage_record_id",
                            "created_at",
                        ],
                        "error_http_statuses": [400, 403, 404, 422],
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            "output-contract.json": json.dumps(
                {
                    "output_mode": output_mode,
                    "output_type": output_type,
                    "output_schema": output_schema if output_mode == "structured" else None,
                },
                ensure_ascii=False,
                indent=2,
            ),
            "writeback-policy.md": (
                "# Writeback Policy\n\n"
                "外部环境不得绕开平台直接运行角色，必须通过平台 consume API 调用。"
                " 平台侧会保留 role_id、role_version_id、status、boundary_status、structured_result"
                " 或自由输出摘要，以及对应 usage_record。"
            ),
        }

        if package_type == ExportPackageType.TOOL:
            dify_openapi = self._build_dify_openapi_spec(
                role_id=role.id,
                role_name=role_name,
                role_bio=role_bio,
                role_version_id=role_version_id,
            )
            common_files["tool-manifest.json"] = json.dumps(
                {
                    "name": role_name,
                    "provider": "virtual-actor",
                    "description": role_bio,
                    "auth": {"type": "bearer", "env": "VIRTUAL_ACTOR_TOKEN"},
                    "endpoint": "{{VIRTUAL_ACTOR_BASE_URL}}/role-assets/"
                    f"{role.id}/consume",
                },
                ensure_ascii=False,
                indent=2,
            )
            common_files["dify-openapi.json"] = json.dumps(
                dify_openapi,
                ensure_ascii=False,
                indent=2,
            )
            common_files["dify-provider-template.json"] = json.dumps(
                self._build_dify_provider_template(
                    role_id=role.id,
                    role_name=role_name,
                    role_bio=role_bio,
                    role_version_id=role_version_id,
                    dify_openapi=dify_openapi,
                ),
                ensure_ascii=False,
                indent=2,
            )
        else:
            common_files["SKILL.md"] = self._render_skill_markdown(
                role_id=role.id,
                role_name=role_name,
                role_version_id=role_version_id,
            )

        return common_files

    def _render_role_brief(self, role_name: str, role_bio: str, briefing) -> str:
        scenarios = "\n".join(f"- {item}" for item in briefing.applicable_scenarios) or "- 暂无"
        return (
            f"# {role_name}\n\n"
            f"## 一句话摘要\n{role_bio}\n\n"
            f"## 适用场景\n{scenarios}\n\n"
            f"## 使用说明\n{briefing.usage_notes}\n\n"
            f"## 可信依据与限制\n{briefing.support_basis_summary}\n\n"
            "## 数据能力声明\n"
            "数据能力按平台当前生效配置运行，不承诺版本冻结复现。"
        )

    def _render_skill_markdown(self, role_id: str, role_name: str, role_version_id: str) -> str:
        skill_name = f"virtual-actor-role-{role_id[:8]}-{role_version_id[:8]}"
        description = (
            f"Use when the user asks to use the exported {role_name} role. "
            "Read the sibling contract files and call the bound virtual-actor consume API exactly once."
        )
        return (
            "---\n"
            f"name: {self._yaml_scalar(skill_name)}\n"
            f"description: {self._yaml_scalar(description)}\n"
            "---\n\n"
            f"# {role_name}\n\n"
            "## Purpose\n"
            "Use this exported role through the platform consume contract instead of answering from memory.\n\n"
            "## Required Files\n"
            "1. `role-brief.md`\n"
            "2. `consume-contract.json`\n"
            "3. `output-contract.json`\n"
            "4. `writeback-policy.md`\n\n"
            "## Required Environment\n"
            "1. `VIRTUAL_ACTOR_BASE_URL`\n"
            "2. `VIRTUAL_ACTOR_TOKEN`\n\n"
            "## Execution Rules\n"
            "1. Read the sibling contract files before responding.\n"
            "2. Build the JSON request body from `consume-contract.json` and do not invent alternate wrapper fields.\n"
            "3. Invoke the bound consume API exactly once for the current user request.\n"
            "4. Use the contract `role_version_id` and `caller_type`; set `caller_id` to `codex-skill`.\n"
            "5. If the consume call fails, report the failure instead of fabricating a role answer.\n"
            "6. Base the final answer on the API response and preserve the returned `usage_record_id` when available.\n\n"
            "## Bound Contract\n"
            f"- role_id: `{role_id}`\n"
            f"- role_version_id: `{role_version_id}`\n"
            f"- endpoint: `/role-assets/{role_id}/consume`\n"
        )

    def _build_dify_openapi_spec(
        self,
        role_id: str,
        role_name: str,
        role_bio: str,
        role_version_id: str,
    ) -> dict:
        return {
            "openapi": "3.0.3",
            "info": {
                "title": role_name,
                "version": "1.0.0",
                "description": role_bio,
            },
            "servers": [
                {
                    "url": "{{VIRTUAL_ACTOR_BASE_URL}}",
                }
            ],
            "paths": {
                f"/role-assets/{role_id}/consume": {
                    "post": {
                        "operationId": "consumePublishedRole",
                        "summary": "Consume published role",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["query"],
                                        "properties": {
                                            "query": {
                                                "type": "string",
                                                "description": "Final user request",
                                            },
                                            "context": {
                                                "type": "string",
                                                "description": "Optional extra context",
                                            },
                                            "output_type": {
                                                "type": "string",
                                                "description": "Optional output type override",
                                            },
                                            "caller_id": {
                                                "type": "string",
                                                "description": "External caller id",
                                                "default": "dify-tool",
                                            },
                                            "caller_type": {
                                                "type": "string",
                                                "default": "external_tool",
                                                "enum": ["external_tool"],
                                            },
                                            "role_version_id": {
                                                "type": "string",
                                                "default": role_version_id,
                                                "enum": [role_version_id],
                                            },
                                        },
                                    }
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "status": {"type": "string"},
                                                "status_reason": {"type": "string"},
                                                "answer": {"type": "string"},
                                                "boundary_status": {"type": "object"},
                                                "structured_result": {"type": "object"},
                                                "output_type": {"type": "string"},
                                                "role_id": {"type": "string"},
                                                "role_version_id": {"type": "string"},
                                                "usage_record_id": {"type": "string"},
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    }
                }
            },
        }

    def _build_dify_provider_template(
        self,
        role_id: str,
        role_name: str,
        role_bio: str,
        role_version_id: str,
        dify_openapi: dict,
    ) -> dict:
        provider_name = f"virtual_actor_role_{role_id[:8]}_{role_version_id[:8]}"
        return {
            "provider": provider_name,
            "icon": {
                "background": "#E5F4FF",
                "content": "VA",
            },
            "credentials": {
                "auth_type": "api_key_header",
                "api_key_header": "Authorization",
                "api_key_value": "Bearer {{VIRTUAL_ACTOR_TOKEN}}",
                "api_key_header_prefix": "custom",
            },
            "schema_type": "openapi",
            "schema": json.dumps(dify_openapi, ensure_ascii=False),
            "privacy_policy": "",
            "custom_disclaimer": "",
            "labels": ["virtual-actor", "role-export"],
            "metadata": {
                "role_id": role_id,
                "role_name": role_name,
                "role_version_id": role_version_id,
                "base_url_placeholder": "{{VIRTUAL_ACTOR_BASE_URL}}",
                "description": role_bio,
            },
        }

    def _yaml_scalar(self, value: str) -> str:
        return json.dumps(value, ensure_ascii=False)
