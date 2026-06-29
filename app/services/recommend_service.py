"""资产市场推荐服务（v0.5 兼容版）"""
import json
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.ops_signal import OpsSignal
from app.schemas.marketplace import RecommendItem, RecommendResponse
from app.services.llm_service import llm_service
from app.services.role_service import RoleService


OUTPUT_KEYWORDS = {
    "decision_advice": ["决策", "判断", "建议", "投资", "评估"],
    "risk_analysis": ["风险", "风控", "排查", "识别", "分析"],
    "policy_explanation": ["制度", "政策", "条款", "规定", "流程", "依据"],
    "review_findings": ["审查", "审核", "评审", "检查", "审阅"],
}

OUTPUT_LABELS = {
    "decision_advice": "决策建议",
    "risk_analysis": "风险分析",
    "policy_explanation": "制度解释",
    "review_findings": "专业审查",
}

OUT_OF_SCOPE_MARKERS = ["火星", "跨星际", "魔法", "预言", "平行宇宙"]

DOMAIN_SIGNAL_GROUPS = {
    "investment": {
        "label": "投资管理",
        "terms": [
            "投资",
            "投资项目",
            "项目投资",
            "投资管理",
            "投资决策",
            "投决",
            "投前",
            "投后",
            "项目评估",
            "立项评估",
            "收益测算",
            "财务测算",
            "可研",
            "尽调",
        ],
    },
    "operations": {
        "label": "经营管理",
        "terms": [
            "经营复盘",
            "经营分析",
            "经营管理",
            "预算偏差",
            "预算分析",
            "预算",
            "经营指标",
            "管理层判断",
            "投资复盘",
        ],
    },
    "compliance": {
        "label": "制度合规",
        "terms": [
            "制度",
            "政策",
            "条款",
            "规定",
            "流程",
            "法务",
            "合规",
            "合同",
            "内控",
        ],
    },
    "project": {
        "label": "项目治理",
        "terms": [
            "项目管理",
            "项目治理",
            "项目复盘",
            "项目评审",
            "项目审查",
            "里程碑",
            "排期",
            "交付",
        ],
    },
    "procurement": {
        "label": "采购供应",
        "terms": [
            "采购",
            "招标",
            "投标",
            "供应商",
            "采购审查",
            "采购评审",
        ],
    },
    "data_governance": {
        "label": "数据治理",
        "terms": [
            "数据治理",
            "数据架构",
            "数据建模",
            "数据模型",
            "数据标准",
            "数据质量",
            "元数据",
            "数据血缘",
            "主数据",
            "数据仓库",
            "数仓",
        ],
    },
}

SIGNAL_LABELS = {
    "business_domain": "业务域",
    "domain": "领域语义",
    "scenario": "适用场景",
    "role_text": "核心职责",
    "output_type": "输出契约",
}


def _meets_pool_criteria(detail) -> bool:
    version_id = getattr(detail, "published_version_id", None) or getattr(detail, "role_version_id", None)
    business_domain = getattr(detail, "business_domain", None)
    summary = getattr(detail, "bio", None) or getattr(detail, "summary", None)
    return bool(
        version_id
        and business_domain
        and detail.output_type
        and detail.briefing.applicable_scenarios
        and summary
    )


async def recommend(intent: str, category: str | None, business_domain: str | None, db: AsyncSession) -> RecommendResponse:
    if any(marker in intent for marker in OUT_OF_SCOPE_MARKERS):
        return RecommendResponse(
            matched=False,
            result_type="out_of_scope",
            recommendations=[],
            unmatched_intent_summary="该需求不属于企业正常业务决策场景范围",
        )

    svc = RoleService(db)
    pairs = await svc.list_with_published_version(category=category, business_domain=business_domain)

    candidates = []
    for role, published_version in pairs:
        detail = await svc.build_version_public_detail(published_version.id)
        if not detail or not _meets_pool_criteria(detail):
            continue
        recall = _score(intent, detail)
        if not recall["qualified"]:
            continue
        candidates.append((detail, recall))

    if not candidates:
        await _record_no_match_signal(intent, category, business_domain, db)
        return RecommendResponse(
            matched=False,
            result_type="no_match",
            recommendations=[],
            unmatched_intent_summary=_build_unmatched_summary(intent),
        )

    candidates.sort(key=lambda item: item[1]["score"], reverse=True)
    judged = await _llm_judge(intent, candidates[:8])
    if judged is None:
        return RecommendResponse(
            matched=False,
            result_type="service_error",
            recommendations=[],
            service_error_message="AI 推荐服务暂时不可用，请稍后重试。",
        )
    if judged.get("is_out_of_scope"):
        return RecommendResponse(
            matched=False,
            result_type="out_of_scope",
            recommendations=[],
            unmatched_intent_summary="该需求不属于企业正常业务决策场景范围",
        )

    judge_by_role = {
        item["role_id"]: item
        for item in judged.get("role_judgments", [])
        if item.get("match") and item.get("score", 0) >= 0.5
    }

    items = _build_judged_items(candidates[:8], judge_by_role)
    if not items:
        items = _build_strong_recall_items(candidates[:8])

    if not items:
        await _record_no_match_signal(intent, category, business_domain, db)
        return RecommendResponse(
            matched=False,
            result_type="no_match",
            recommendations=[],
            unmatched_intent_summary=_build_unmatched_summary(intent),
        )

    return RecommendResponse(matched=True, result_type="matched", recommendations=items)


def _build_judged_items(candidates: list[tuple], judge_by_role: dict[str, dict[str, object]]) -> list[RecommendItem]:
    items: list[RecommendItem] = []
    for detail, recall in candidates:
        judge = judge_by_role.get(detail.role_id)
        if not judge:
            continue
        items.append(
            _build_recommend_item(
                detail,
                recall,
                reason_summary=judge.get("reason_summary"),
                match_score=judge.get("score", recall["score"]),
            )
        )
        if len(items) >= 3:
            break
    return items


def _build_strong_recall_items(candidates: list[tuple]) -> list[RecommendItem]:
    items: list[RecommendItem] = []
    for detail, recall in candidates:
        if not _is_strong_direct_match(recall):
            continue
        items.append(_build_recommend_item(detail, recall, reason_summary=None, match_score=recall["score"]))
        if len(items) >= 3:
            break
    return items


def _is_strong_direct_match(recall: dict[str, object]) -> bool:
    matched_signals = set(recall.get("matched_signals") or [])
    score = float(recall.get("score") or 0)
    return (
        "business_domain" in matched_signals
        and bool({"scenario", "role_text"} & matched_signals)
        and score >= 1.0
    )


def _build_recommend_item(detail, recall: dict[str, object], reason_summary: str | None, match_score: float) -> RecommendItem:
    final_reason_summary = (reason_summary or "").strip() or _build_reason_summary(detail, recall)
    return RecommendItem(
        role_id=detail.role_id,
        role_version_id=detail.role_version_id,
        role_name=detail.name,
        bio=detail.summary,
        recommendation_reason=final_reason_summary,
        reason_summary=final_reason_summary,
        reason_evidence=_build_reason_evidence(detail, recall),
        matched_dimensions=_build_matched_dimensions(recall["matched_signals"]),
        caution=_build_caution(detail),
        applicable_problems=detail.briefing.applicable_scenarios[:2],
        applicable_scenarios_label="、".join(detail.briefing.applicable_scenarios[:3]),
        output_type=detail.output_type,
        knowledge_boundary=detail.knowledge_boundary,
        version_number=None,
        version_status="published",
        tags=[],
        match_score=match_score,
    )


def _score(intent: str, detail) -> dict[str, object]:
    score = 0.0
    matched_signals: list[str] = []

    lowered = intent.lower()
    role_fragments = [
        detail.name or "",
        detail.summary or "",
        detail.main_duty_cluster or "",
        detail.business_domain or "",
        *list(getattr(detail, "tags", []) or []),
        *list(detail.briefing.applicable_scenarios or []),
    ]
    role_text = " ".join(fragment.lower() for fragment in role_fragments if fragment)
    intent_domain_hits = _extract_domain_hits(lowered)
    role_domain_hits = _extract_domain_hits(role_text)
    overlap_domains = [key for key in intent_domain_hits if key in role_domain_hits]

    if detail.business_domain:
        business_domain_text = detail.business_domain.lower()
        business_domain_hits = _extract_domain_hits(business_domain_text)
        if business_domain_text in lowered:
            score += 0.55
            matched_signals.append("business_domain")
        elif any(key in intent_domain_hits for key in business_domain_hits):
            score += 0.4
            matched_signals.append("business_domain")

    if overlap_domains:
        score += 0.45
        matched_signals.append("domain")

    if _fragments_match_intent(intent_domain_hits, detail.briefing.applicable_scenarios, lowered):
        score += 0.25
        matched_signals.append("scenario")

    if _fragments_match_intent(intent_domain_hits, [detail.main_duty_cluster, detail.summary, detail.name], lowered):
        score += 0.2
        matched_signals.append("role_text")

    intent_output_types = _extract_output_matches(lowered)
    has_strong_signal = any(signal in matched_signals for signal in ("business_domain", "domain", "scenario", "role_text"))
    if detail.output_type in intent_output_types and has_strong_signal:
        score += 0.15
        matched_signals.append("output_type")

    matched_signals = _unique(matched_signals)
    return {
        "score": round(score, 3),
        "matched_signals": matched_signals,
        "qualified": score >= 0.45 and has_strong_signal,
        "domain_labels": [DOMAIN_SIGNAL_GROUPS[key]["label"] for key in overlap_domains],
    }


async def _llm_judge(intent: str, candidates: list[tuple]) -> dict | None:
    if not candidates:
        return None

    candidate_payload = []
    for detail, recall in candidates:
        candidate_payload.append(
            {
                "role_id": detail.role_id,
                "role_name": detail.name,
                "bio": detail.summary,
                "tags": list(getattr(detail, "tags", []) or []),
                "business_domain": getattr(detail, "business_domain", None),
                "main_duty_cluster": detail.main_duty_cluster,
                "applicable_scenarios": detail.briefing.applicable_scenarios,
                "output_type": detail.output_type,
                "knowledge_boundary": detail.knowledge_boundary,
                "recall_score": recall["score"],
                "matched_signals": recall["matched_signals"],
                "domain_labels": recall["domain_labels"],
            }
        )

    llm_output = await llm_service.chat(
        system_prompt=(
            "你是企业角色资产市场的推荐裁决器。"
            "请先判断用户意图是否属于企业正常业务场景；若不属于，is_out_of_scope=true。"
            "若属于，只在候选角色的 business_domain、main_duty_cluster、applicable_scenarios 与用户任务真实匹配时，才返回 match=true。"
            "若用户表达的是较宽的业务目标，可返回 1-3 个与该目标直接相关、职责互补的角色。"
            "不要因为用户没有写出细化子任务，就把本应匹配的角色全部判成不匹配。"
            "不得因为泛化关键词、结构化输出或语气相似就判定匹配。"
            '只返回 JSON：{"is_out_of_scope":bool,"role_judgments":[{"role_id":"...","match":bool,"score":0.0,"reason_summary":"..."}]}'
        ),
        user_message=json.dumps(
            {"intent": intent, "candidates": candidate_payload},
            ensure_ascii=False,
            indent=2,
        ),
        model=settings.AI_RECOMMEND_MODEL,
        temperature=settings.AI_RECOMMEND_TEMPERATURE,
        max_tokens=settings.AI_RECOMMEND_MAX_TOKENS,
    )
    if llm_output.startswith("[LLM 调用失败"):
        return None
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

    judgments = []
    raw_judgments = parsed.get("role_judgments", [])
    if isinstance(raw_judgments, list):
        for item in raw_judgments:
            if not isinstance(item, dict) or not item.get("role_id"):
                continue
            score = item.get("score")
            try:
                normalized_score = float(score)
            except (TypeError, ValueError):
                normalized_score = 0.0
            judgments.append(
                {
                    "role_id": item["role_id"],
                    "match": bool(item.get("match")),
                    "score": normalized_score,
                    "reason_summary": str(item.get("reason_summary") or item.get("reason") or "").strip(),
                }
            )

    return {
        "is_out_of_scope": bool(parsed.get("is_out_of_scope")),
        "role_judgments": judgments,
    }


def _extract_domain_hits(text: str) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for key, config in DOMAIN_SIGNAL_GROUPS.items():
        matched_terms = [term for term in config["terms"] if term in text]
        if matched_terms:
            hits[key] = matched_terms
    return hits


def _extract_output_matches(text: str) -> set[str]:
    matched = set()
    for output_type, keywords in OUTPUT_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            matched.add(output_type)
    return matched


def _fragments_match_intent(intent_domain_hits: dict[str, list[str]], fragments: list[str] | tuple[str, ...], lowered_intent: str) -> bool:
    for fragment in fragments:
        if not fragment:
            continue
        lowered_fragment = fragment.lower()
        if len(lowered_fragment) >= 4 and (lowered_fragment in lowered_intent or lowered_intent in lowered_fragment):
            return True
        fragment_domain_hits = _extract_domain_hits(lowered_fragment)
        if any(key in intent_domain_hits for key in fragment_domain_hits):
            return True
    return False


def _build_reason_summary(detail, recall: dict[str, object]) -> str:
    scenarios = "、".join(detail.briefing.applicable_scenarios[:2])
    output_label = OUTPUT_LABELS.get(detail.output_type or "", detail.output_type or "自由输出")
    if scenarios:
        return f"更适合 {scenarios} 这类任务，可按 {output_label} 方式返回结果。"
    if detail.business_domain:
        return f"该角色面向 {detail.business_domain} 场景，可按 {output_label} 方式提供结果。"
    domain_labels = recall.get("domain_labels") or []
    if domain_labels:
        return f"该角色更贴近 {'、'.join(domain_labels[:2])} 类任务，可按 {output_label} 方式提供结果。"
    return f"该角色与当前业务意图存在实质匹配，可按 {output_label} 方式提供结果。"


def _build_reason_evidence(detail, recall: dict[str, object]) -> list[str]:
    evidence: list[str] = []
    matched_signals = set(recall.get("matched_signals") or [])

    if detail.business_domain and {"business_domain", "domain"} & matched_signals:
        evidence.append(f"业务域：{detail.business_domain}")
    if detail.briefing.applicable_scenarios and "scenario" in matched_signals:
        evidence.append(f"适用场景：{'、'.join(detail.briefing.applicable_scenarios[:2])}")
    if (detail.main_duty_cluster or detail.summary) and "role_text" in matched_signals:
        evidence.append(f"核心职责：{_truncate(detail.main_duty_cluster or detail.summary, 48)}")
    if detail.output_type and "output_type" in matched_signals:
        evidence.append(f"输出方式：{OUTPUT_LABELS.get(detail.output_type, detail.output_type)}")

    if not evidence and detail.briefing.applicable_scenarios:
        evidence.append(f"适用场景：{'、'.join(detail.briefing.applicable_scenarios[:2])}")
    if len(evidence) < 3 and detail.business_domain and f"业务域：{detail.business_domain}" not in evidence:
        evidence.append(f"业务域：{detail.business_domain}")
    if len(evidence) < 4 and detail.output_type:
        output_line = f"输出方式：{OUTPUT_LABELS.get(detail.output_type, detail.output_type)}"
        if output_line not in evidence:
            evidence.append(output_line)
    return evidence[:4]


def _build_matched_dimensions(matched_signals: list[str]) -> list[str]:
    return _unique([SIGNAL_LABELS[signal] for signal in matched_signals if signal in SIGNAL_LABELS])


def _build_caution(detail) -> str | None:
    if detail.knowledge_boundary:
        return detail.knowledge_boundary
    knowledge_status = getattr(detail.briefing, "knowledge_status", None)
    if knowledge_status and getattr(knowledge_status, "state", None) != "bound":
        return "当前未绑定知识，涉及制度依据或明确条款的问题可能需要补充知识后再使用。"
    return None


def _build_unmatched_summary(intent: str) -> str:
    hits = _extract_domain_hits(intent.lower())
    if "investment" in hits:
        return "当前已发布角色未覆盖投资管理 / 项目投资类任务"
    if "data_governance" in hits:
        return "当前已发布角色未覆盖数据治理 / 数据架构类任务"
    if "operations" in hits:
        return "当前已发布角色未覆盖经营复盘 / 预算分析类任务"
    if "compliance" in hits:
        return "当前已发布角色未覆盖制度合规类任务"
    if "project" in hits:
        return "当前已发布角色未覆盖项目治理类任务"
    if "procurement" in hits:
        return "当前已发布角色未覆盖采购供应类任务"
    return "当前已发布角色未覆盖该业务意图"


async def _record_no_match_signal(intent: str, category: str | None, business_domain: str | None, db: AsyncSession) -> None:
    db.add(
        OpsSignal(
            id=str(uuid.uuid4()),
            intent=intent,
            intent_summary=intent[:120],
            category=category,
            business_domain=business_domain,
            matched_output_type=None,
            signal_type="no_role_match",
        )
    )
    await db.flush()


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))
