"""AI 协作创建服务 — 生成 v0.5 草案但不落库"""
import json
import re

from app.config import settings
from app.schemas.ai_create import AIDraftRequest, AIDraftResponse
from app.schemas.role import OutputMode
from app.services.llm_service import llm_service


AI_CREATE_SYSTEM_PROMPT = """你是企业数字角色设计助手。
请根据用户提供的角色意图，输出一个符合 v0.5 平台骨架的 JSON 草案。

输出 JSON 字段：
{
  "name": "...",
  "bio": "...",
  "tags": ["..."],
  "main_duty_cluster": "...",
  "point_of_view": "...",
  "decision_style": "...",
  "identity_background": "...",
  "speaking_style": "...",
  "knowledge_boundary": "...",
  "output_mode": "freeform 或 structured",
  "output_type": "decision_advice/risk_analysis/policy_explanation/review_findings/null",
  "output_schema": {},
  "category": "...",
  "business_domain": "...",
  "applicable_scenarios": ["..."],
  "usage_notes": "...",
  "support_basis_summary": "..."
}

规则：
1. 草案只服务于平台内编辑，不绑定真实知识，不绑定数据资产。
2. 若用户明显需要稳定模板，则 output_mode=structured，否则默认 freeform。
3. 所有字段使用中文商务表达。
4. 输出必须是单个 JSON 对象。"""


OUTPUT_TYPE_KEYWORDS = {
    "decision_advice": ["决策", "判断", "建议", "评估", "方案", "投资"],
    "risk_analysis": ["风险", "合规", "排查", "分析", "风控"],
    "policy_explanation": ["制度", "流程", "规定", "条款", "政策", "解释"],
    "review_findings": ["审查", "审核", "评审", "检查", "审阅"],
}


def _fallback_draft(data: AIDraftRequest) -> AIDraftResponse:
    description = data.description.strip()
    output_type = None
    output_mode = OutputMode.FREEFORM
    for candidate, keywords in OUTPUT_TYPE_KEYWORDS.items():
        if any(keyword in description for keyword in keywords):
            output_type = candidate
            output_mode = OutputMode.STRUCTURED
            break

    short_name = re.split(r"[，。；、\s]", description)[0][:12] or "数字角色草案"
    business_domain = data.business_domain or ("经营管理" if "经营" in description else None)
    return AIDraftResponse(
        name=short_name,
        bio=f"面向企业业务场景，提供与“{short_name}”相关的判断和建议。",
        tags=[token for token in ["经营", "分析", "治理", "决策"] if token in description][:3],
        main_duty_cluster=f"围绕{short_name}相关任务，负责识别关键问题、解释原因，并输出可执行建议与风险提示。",
        point_of_view="优先从业务目标、关键约束和可执行性三个维度看问题。",
        decision_style="平衡型：先澄清前提，再给出综合判断",
        identity_background="具备相关业务分析和跨部门协同经验，能够在信息不完整时先澄清关键前提。",
        speaking_style="先给结论，再给依据与限制，使用管理层能快速理解的商务语言。",
        knowledge_boundary="基于已绑定知识回答，暂不覆盖未授权的外部事实或未提供的内部资料。",
        output_mode=output_mode,
        output_type=output_type,
        output_schema={} if output_mode == OutputMode.STRUCTURED else None,
        category=data.category or "自定义",
        business_domain=business_domain,
        applicable_scenarios=[
            f"{short_name}相关判断",
            "需要先澄清目标与约束的业务分析任务",
            "希望沉淀成稳定角色能力的高频问题场景",
        ],
        usage_notes="面向调用该角色的同事，请提供任务背景、目标对象、关键约束和已有上下文，再让角色输出结论、依据与限制。",
        support_basis_summary="系统预期该角色基于角色定义、知识状态、数据能力状态与测试记录形成可信说明，当前草案仅供编辑确认。",
        ai_generation_note="已使用规则化回退草案，请人工继续修订。",
    )


async def generate_draft(data: AIDraftRequest) -> AIDraftResponse:
    user_message = f"角色意图：{data.description}"
    if data.category:
        user_message += f"\n分类偏好：{data.category}"
    if data.business_domain:
        user_message += f"\n业务域：{data.business_domain}"

    llm_output = await llm_service.chat(
        system_prompt=AI_CREATE_SYSTEM_PROMPT,
        user_message=user_message,
        model=settings.AI_CREATE_MODEL,
        temperature=settings.AI_CREATE_TEMPERATURE,
        max_tokens=settings.AI_CREATE_MAX_TOKENS,
    )

    if not llm_output.startswith("[LLM 调用失败"):
        try:
            json_start = llm_output.find("{")
            json_end = llm_output.rfind("}") + 1
            parsed = json.loads(llm_output[json_start:json_end])
            return AIDraftResponse(
                name=parsed.get("name") or _fallback_draft(data).name,
                bio=parsed.get("bio") or _fallback_draft(data).bio,
                tags=parsed.get("tags") or [],
                main_duty_cluster=parsed.get("main_duty_cluster"),
                point_of_view=parsed.get("point_of_view"),
                decision_style=parsed.get("decision_style"),
                identity_background=parsed.get("identity_background"),
                speaking_style=parsed.get("speaking_style"),
                knowledge_boundary=parsed.get("knowledge_boundary"),
                output_mode=parsed.get("output_mode", OutputMode.FREEFORM),
                output_type=parsed.get("output_type"),
                output_schema=parsed.get("output_schema"),
                category=parsed.get("category") or data.category or "自定义",
                business_domain=parsed.get("business_domain") or data.business_domain,
                applicable_scenarios=parsed.get("applicable_scenarios") or [],
                usage_notes=parsed.get("usage_notes"),
                support_basis_summary=parsed.get("support_basis_summary"),
            )
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    return _fallback_draft(data)
