"""业务输出模板定义 + 结构化结果校验

按真源 business-output-templates-and-status-rules.md §1.2~1.5 完整定义 4 类模板。
每类模板字段数不等、含子结构（RiskItem/ReferenceItem/IssueItem/ClauseItem 等），
references 在所有模板中均为必填。
"""

OUTPUT_TEMPLATES = {
    "decision_advice": {
        "label": "决策建议",
        "fields": {
            "position": {"type": "string", "required": True, "label": "立场/倾向"},
            "key_reasons": {"type": "array[string]", "required": True, "label": "关键理由"},
            "major_risks": {"type": "array[RiskItem]", "required": True, "label": "主要风险"},
            "preconditions": {"type": "array[string]", "required": False, "label": "前置条件"},
            "suggested_actions": {"type": "array[string]", "required": True, "label": "建议动作"},
            "references": {"type": "array[ReferenceItem]", "required": True, "label": "引用依据"},
        },
        "sub_structures": {
            "RiskItem": {
                "risk": {"type": "string", "required": True, "label": "风险描述"},
                "level": {"type": "enum[high/medium/low]", "required": True, "label": "风险等级"},
                "mitigation": {"type": "string", "required": False, "label": "缓解措施"},
            },
            "ReferenceItem": {
                "source": {"type": "string", "required": True, "label": "来源名称"},
                "section": {"type": "string", "required": False, "label": "涉及章节"},
                "type": {"type": "enum[knowledge/external_data/regulation/expert_opinion]", "required": True, "label": "依据类型"},
            },
        },
    },
    "risk_analysis": {
        "label": "风险分析",
        "fields": {
            "key_findings": {"type": "array[string]", "required": True, "label": "关键发现"},
            "risk_items": {"type": "array[RiskDetailItem]", "required": True, "label": "风险项"},
            "overall_risk_level": {"type": "enum[critical/high/medium/low]", "required": True, "label": "综合风险等级"},
            "impact_scope": {"type": "string", "required": True, "label": "影响范围"},
            "suggested_mitigations": {"type": "array[string]", "required": True, "label": "建议缓解措施"},
            "references": {"type": "array[ReferenceItem]", "required": True, "label": "引用依据"},
        },
        "sub_structures": {
            "RiskDetailItem": {
                "item": {"type": "string", "required": True, "label": "风险描述"},
                "severity": {"type": "enum[critical/high/medium/low]", "required": True, "label": "严重等级"},
                "impact": {"type": "string", "required": True, "label": "影响说明"},
                "mitigation": {"type": "string", "required": False, "label": "缓解措施"},
            },
            "ReferenceItem": {
                "source": {"type": "string", "required": True, "label": "来源名称"},
                "section": {"type": "string", "required": False, "label": "涉及章节"},
                "type": {"type": "enum[knowledge/external_data/regulation/expert_opinion]", "required": True, "label": "依据类型"},
            },
        },
    },
    "policy_explanation": {
        "label": "制度解释",
        "fields": {
            "applicable_clauses": {"type": "array[ClauseItem]", "required": True, "label": "适用条款"},
            "clause_explanation": {"type": "string", "required": True, "label": "条款解释"},
            "allowed_actions": {"type": "array[string]", "required": True, "label": "可做事项"},
            "prohibited_actions": {"type": "array[string]", "required": True, "label": "不可做事项"},
            "caveats": {"type": "array[string]", "required": False, "label": "注意事项"},
            "references": {"type": "array[ReferenceItem]", "required": True, "label": "引用依据"},
        },
        "sub_structures": {
            "ClauseItem": {
                "clause": {"type": "string", "required": True, "label": "条款标识"},
                "content": {"type": "string", "required": True, "label": "条款原文"},
            },
            "ReferenceItem": {
                "source": {"type": "string", "required": True, "label": "来源名称"},
                "section": {"type": "string", "required": False, "label": "涉及章节"},
                "type": {"type": "enum[knowledge/external_data/regulation/expert_opinion]", "required": True, "label": "依据类型"},
            },
        },
    },
    "review_findings": {
        "label": "专业审查",
        "fields": {
            "issues": {"type": "array[IssueItem]", "required": True, "label": "问题项"},
            "items_to_confirm": {"type": "array[string]", "required": False, "label": "需确认事项"},
            "overall_severity": {"type": "enum[critical/high/medium/low/acceptable]", "required": True, "label": "综合严重等级"},
            "references": {"type": "array[ReferenceItem]", "required": True, "label": "引用依据"},
        },
        "sub_structures": {
            "IssueItem": {
                "title": {"type": "string", "required": True, "label": "问题标题"},
                "severity": {"type": "enum[critical/high/medium/low]", "required": True, "label": "严重等级"},
                "description": {"type": "string", "required": True, "label": "问题说明"},
                "suggestion": {"type": "string", "required": False, "label": "修改建议"},
            },
            "ReferenceItem": {
                "source": {"type": "string", "required": True, "label": "来源名称"},
                "section": {"type": "string", "required": False, "label": "涉及章节"},
                "type": {"type": "enum[knowledge/external_data/regulation/expert_opinion]", "required": True, "label": "依据类型"},
            },
        },
    },
}


def get_template(output_type: str) -> dict | None:
    """返回指定 output_type 的模板定义（含字段和子结构）"""
    return OUTPUT_TEMPLATES.get(output_type)


def get_default_schema(output_type: str) -> dict:
    """返回指定 output_type 的默认空 schema（所有必填字段设为空占位）"""
    template = OUTPUT_TEMPLATES.get(output_type)
    if not template:
        return {}
    schema = {}
    for field_name, field_def in template["fields"].items():
        if field_def["type"].startswith("array"):
            schema[field_name] = []
        elif field_def["type"].startswith("enum"):
            schema[field_name] = ""
        else:
            schema[field_name] = ""
    return schema


def validate_structured_result(output_type: str, structured_result: dict) -> list[str]:
    """校验 structured_result 是否符合模板要求。返回不合规字段列表。"""
    template = OUTPUT_TEMPLATES.get(output_type)
    if not template:
        return ["unknown output_type"]

    errors = []
    for field_name, field_def in template["fields"].items():
        if field_def["required"]:
            if field_name not in structured_result:
                errors.append(f"{field_name}: 缺失必填字段")
            elif structured_result[field_name] is None:
                errors.append(f"{field_name}: 必填字段为 null")

    # references 必填且非空数组
    if "references" in structured_result:
        refs = structured_result["references"]
        if not isinstance(refs, list) or len(refs) == 0:
            errors.append("references: 必填且必须为非空数组")

    return errors


def is_structured_result_compliant(output_type: str, structured_result: dict) -> bool:
    """判断 structured_result 是否完全合规"""
    return len(validate_structured_result(output_type, structured_result)) == 0