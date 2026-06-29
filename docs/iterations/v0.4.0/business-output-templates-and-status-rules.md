# v0.4.0 业务输出模板字段定义与消费状态规则

> 版本：v0.4.0 | 日期：2026-05-26 | Formal Status：Draft
> 类型：角色产品本地候选规格 / 集成验证规格
> 公共契约边界：模板字段定义不等同于冻结跨项目公共契约；决策产品要稳定依赖 structured_result 字段时，必须上提公共契约裁决

---

## 1. DD-11 四类业务输出模板完整字段定义

### 1.1 模板总览

| 模板 ID | 中文名 | 适用场景 | 核心消费者 |
|---|---|---|---|
| decision_advice | 决策建议 | 高管决策、决策产品、重大事项评估 | 决策产品、高管 |
| risk_analysis | 风险分析 | 经营分析、风控、财务、项目管理 | 风控团队、经营管理层 |
| policy_explanation | 制度解释 | 制度、合规、人力、财务、行政流程 | 合规团队、一线业务人员 |
| review_findings | 专业审查 | 法务、合同、方案、技术、项目文档审查 | 法务/技术审查人员 |

### 1.2 decision_advice（决策建议）

角色消费时 `structured_result` 按此结构输出。

| 字段名 | 中文名 | 类型 | 必填 | 业务含义 | 示例 | 适用场景 |
|---|---|---|---|---|---|---|
| position | 立场/倾向 | String | 必填 | 角色对该决策事项的整体判断方向，正面/负面/中立/谨慎 | "谨慎支持，但需满足前置条件" | 决策产品需要明确倾向以辅助决策 |
| key_reasons | 关键理由 | Array\<String\> | 必填 | 支撑立场的主要理由，每条应独立且可追溯 | ["项目 ROI 达 18%，高于门槛 12%", "核心团队已到位"] | 决策方需要可拆解的论证链 |
| major_risks | 主要风险 | Array\<RiskItem\> | 必填 | 该决策事项的主要风险项 | [{"risk": "市场波动导致 ROI 下滑", "level": "medium", "mitigation": "设置阶段性复盘门禁"}] | 决策方需要风险意识 |
| preconditions | 前置条件 | Array\<String\> | 可选 | 立场生效的前提条件或假设 | ["第一阶段预算必须到位", "核心人员不得在 3 个月内调离"] | 立场有条件生效时必须标注 |
| suggested_actions | 建议动作 | Array\<String\> | 必填 | 角色建议的下一步动作 | ["批准第一阶段启动", "设置 3 个月复盘门禁", "指定项目 Owner"] | 决策方需要可执行的建议 |
| references | 引用依据 | Array\<ReferenceItem\> | 必填 | 立场和理由的依据来源 | [{"source": "2026 Q1 经营报告", "section": "ROI 分析", "type": "knowledge"}] | 决策必须有可追溯依据 |

RiskItem 子结构：

| 字段名 | 中文名 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| risk | 风险描述 | String | 必填 | 风险事项 |
| level | 风险等级 | Enum: high/medium/low | 必填 | 风险严重程度 |
| mitigation | 缓解措施 | String | 可选 | 建议的风险缓解方法 |

ReferenceItem 子结构：

| 字段名 | 中文名 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| source | 来源名称 | String | 必填 | 知识/文档/数据来源名称 |
| section | 涉及章节 | String | 可选 | 来源中的具体位置 |
| type | 依据类型 | Enum: knowledge/external_data/regulation/expert_opinion | 必填 | 依据的分类 |

### 1.3 risk_analysis（风险分析）

| 字段名 | 中文名 | 类型 | 必填 | 业务含义 | 示例 | 适用场景 |
|---|---|---|---|---|---|---|
| key_findings | 关键发现 | Array\<String\> | 必填 | 分析中最重要的发现 | ["合同条款中 3 处风险点需修订", "付款条款与集团制度不一致"] | 消费方需要快速定位核心问题 |
| risk_items | 风险项 | Array\<RiskDetailItem\> | 必填 | 详细风险清单 | [{"item": "付款条件超出 90 天", "severity": "high", "impact": "违反集团资金管理制度", "mitigation": "修改为 60 天内付款"}] | 风控需要逐项评估 |
| overall_risk_level | 综合风险等级 | Enum: critical/high/medium/low | 必填 | 基于所有风险项的综合判定 | "high" | 决策方需要一目了然的总体判断 |
| impact_scope | 影响范围 | String | 必填 | 风险影响的业务范围 | "涉及财务合规和合同履约两个维度" | 风控需要判断影响面 |
| suggested_mitigations | 建议缓解措施 | Array\<String\> | 必填 | 针对综合风险的缓解建议 | ["修订付款条款", "增加违约金条款", "设置履约保证金"] | 风控需要可执行的建议 |
| references | 引用依据 | Array\<ReferenceItem\> | 必填 | 风险判定的依据来源 | [{"source": "集团资金管理制度 v3.2", "section": "付款周期", "type": "regulation"}] | 风险判定必须有依据 |

RiskDetailItem 子结构：

| 字段名 | 中文名 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| item | 风险描述 | String | 必填 | 具体风险事项 |
| severity | 严重等级 | Enum: critical/high/medium/low | 必填 | 风险严重程度 |
| impact | 影响说明 | String | 必填 | 风险对业务的具体影响 |
| mitigation | 缓解措施 | String | 可选 | 针对该风险的缓解建议 |

### 1.4 policy_explanation（制度解释）

| 字段名 | 中文名 | 类型 | 必填 | 业务含义 | 示例 | 适用场景 |
|---|---|---|---|---|---|---|
| applicable_clauses | 适用条款 | Array\<ClauseItem\> | 必填 | 与请求相关的制度条款 | [{"clause": "《人力管理制度》第 7.3 条", "content": "员工离职需提前 30 天书面通知"}] | 解释必须基于具体条款 |
| clause_explanation | 条款解释 | String | 必填 | 对适用条款的通俗化解释 | "员工必须提前 30 天以书面形式通知公司离职意向，口头通知不生效" | 一线人员需要业务语言解释 |
| allowed_actions | 可做事项 | Array\<String\> | 必填 | 条款允许的操作 | ["提前 30 天提交书面离职申请", "在离职前完成交接清单"] | 一线人员需要明确可做什么 |
| prohibited_actions | 不可做事项 | Array\<String\> | 必填 | 条款禁止的操作 | ["未提前通知直接离职", "口头通知视为无效"] | 一线人员需要明确不可做什么 |
| caveats | 注意事项 | Array\<String\> | 可选 | 条款适用中的特殊情况或边界条件 | ["试用期内离职规则不同，适用第 7.4 条", "高管离职有额外竞业限制"] | 防止用户忽略特殊情况 |
| references | 引用依据 | Array\<ReferenceItem\> | 必填 | 条款来源 | [{"source": "人力管理制度 v3.1", "section": "7.3 离职流程", "type": "regulation"}] | 解释必须有条款依据 |

ClauseItem 子结构：

| 字段名 | 中文名 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| clause | 条款标识 | String | 必填 | 制度条款编号或名称 |
| content | 条款原文 | String | 必填 | 条款的原始文本或摘要 |

### 1.5 review_findings（专业审查）

| 字段名 | 中文名 | 类型 | 必填 | 业务含义 | 示例 | 适用场景 |
|---|---|---|---|---|---|---|
| issues | 问题项 | Array\<IssueItem\> | 必填 | 审查发现的问题清单 | [{"title": "合同违约金条款缺失", "severity": "high", "description": "合同未约定违约金比例和计算方式", "suggestion": "增加违约金条款，按日 0.05% 计算"}] | 审查必须逐项列出问题 |
| items_to_confirm | 需确认事项 | Array\<String\> | 可选 | 审查中无法判定、需人工确认的事项 | ["甲方资质文件是否为最新版本", "关联方交易是否已报备"] | 审查不能代替人工判断 |
| overall_severity | 综合严重等级 | Enum: critical/high/medium/low/acceptable | 必填 | 基于所有问题项的综合判定 | "high" | 审查方需要总体判断 |
| references | 引用依据 | Array\<ReferenceItem\> | 必填 | 审查判定的依据来源 | [{"source": "合同审查标准 v2.1", "section": "违约金条款", "type": "regulation"}] | 审查意见必须有依据 |

IssueItem 子结构：

| 字段名 | 中文名 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| title | 问题标题 | String | 必填 | 简明问题描述 |
| severity | 严重等级 | Enum: critical/high/medium/low | 必填 | 问题严重程度 |
| description | 问题说明 | String | 必填 | 问题的详细描述 |
| suggestion | 修改建议 | String | 可选 | 针对该问题的修改建议 |

### 1.6 与 structured_result 的关系

1. 角色配置 `output_type` 为上述 4 个模板之一时，消费输出的 `structured_result` 必须按对应模板结构输出。
2. 所有必填字段必须存在且类型正确；可选字段如角色知识不足以生成，可省略但不能用空字符串替代。
3. `references` 在所有模板中均为必填——消费输出必须有可追溯依据，这是治理底线。
4. 消费结果 `status` 非 success 时，`structured_result` 可为空对象 `{}`，但 `answer` 和 `status_reason` 必须解释原因。

### 1.7 模板选择与 AI 推荐

1. AI 创建角色草案时，基于角色意图自动推荐 `output_type`。
2. 推荐逻辑：
   - 角色意图包含"决策/判断/建议"关键词 → 推荐 decision_advice
   - 角色意图包含"风险/合规/分析"关键词 → 推荐 risk_analysis
   - 角色意图包含"制度/规定/流程/解释"关键词 → 推荐 policy_explanation
   - 角色意图包含"审查/审核/评审/检查"关键词 → 推荐 review_findings
3. 用户可在草案中修改 AI 推荐的 `output_type`。
4. v0.4 不支持自定义 Schema；v0.4.x 补自定义字段治理。

---

## 2. boundary_status 复合结构与枚举值

### 2.1 结构定义

`boundary_status` 是 knowledge_boundary 和 capability_boundary 两个维度的组合对象：

```json
{
  "knowledge_boundary": "enum_value",
  "capability_boundary": "enum_value"
}
```

### 2.2 各维度枚举值

| 枚举值 | 中文名 | 含义 |
|---|---|---|
| within_boundary | 边界内 | 请求在该维度边界内，角色可以基于该维度能力正常响应 |
| near_boundary | 接近边界 | 请求接近该维度边界但未越界；角色可以响应但结果可能不够全面或需标注局限性 |
| out_of_scope | 越界 | 请求超出该维度边界；角色不应作为该维度的正常结论继续流转 |
| not_applicable | 不适用 | 该维度边界判定不适用（如系统失败时无法判定边界状态） |

### 2.3 命中规则

#### knowledge_boundary 命中规则

| 场景 | 命中值 | 说明 |
|---|---|---|
| 用户问题属于角色知识边界范围内，且绑定知识足以支撑回答 | within_boundary | 正常命中 |
| 用户问题属于角色知识边界范围内，但绑定知识不足以完全支撑可靠回答 | near_boundary | 知识有覆盖但不完整 |
| 用户问题超出角色声明的知识边界 | out_of_scope | 越界——请求不属于角色知识范围 |
| 系统失败无法判定 | not_applicable | 无法执行边界判定 |

#### capability_boundary 命中规则

| 场景 | 命中值 | 说明 |
|---|---|---|
| 用户请求属于角色能力层级范围内（如 A1 角色被要求问答建议） | within_boundary | 正常命中 |
| 用户请求接近角色能力边界（如 A1 角色被要求生成结构化分析但未要求执行动作） | near_boundary | 接近上限但未越界 |
| 用户请求超出角色能力层级（如 A1 角色被要求执行付款动作） | out_of_scope | 越界——请求超出能力层级 |
| 系统失败无法判定 | not_applicable | 无法执行边界判定 |

---

## 3. 6 状态与 boundary_status 联动规则

### 3.1 联动总表

| 消费状态 | knowledge_boundary | capability_boundary | 联动说明 |
|---|---|---|---|
| success | within_boundary 或 near_boundary | within_boundary 或 near_boundary | 两个维度都在边界内或接近边界；near_boundary 时 answer 应标注局限性 |
| boundary_blocked | 至少一个 out_of_scope | 任意值 | 至少一个维度越界则阻断；另一维度可能 within 或 not_applicable |
| insufficient_context | within_boundary | within_boundary | 请求属于范围但输入不足以可靠回答；两个维度均在边界内 |
| insufficient_knowledge | near_boundary 或 within_boundary | within_boundary | 知识维度接近或在内（请求属于范围但知识不足）；能力维度在内 |
| system_failed | not_applicable | not_applicable | 系统异常导致无法判定任何维度 |
| undefined | not_applicable | not_applicable | 无法稳定归类时两个维度均标为不适用 |

### 3.2 联动校验规则

后端在生成消费输出时，必须校验 status 与 boundary_status 的联动一致性：

1. status = success 时，boundary_status 两个维度不得为 out_of_scope 或 not_applicable。
2. status = boundary_blocked 时，boundary_status 至少一个维度必须为 out_of_scope。
3. status = insufficient_context 时，两个维度必须为 within_boundary（不允许 near_boundary，因为 insufficient_context 的语义是"输入不足以判定"，而非"边界接近"）。
4. status = insufficient_knowledge 时，knowledge_boundary 必须为 near_boundary 或 within_boundary（请求属于范围但知识不足），capability_boundary 必须为 within_boundary。
5. status = system_failed 或 undefined 时，两个维度必须为 not_applicable。

### 3.3 保守判定策略

1. insufficient_context 和 insufficient_knowledge 采用保守判定——当 LLM 判断置信度不够时，优先降入 undefined 而不是硬判。
2. near_boundary 标注不等于越界，answer 中应明确告知用户结果的局限性。
3. boundary_blocked 的 out_of_scope 必须有明确的 boundary 声明支撑（角色声明的 knowledge_boundary 或 capability_boundary 或 capability_level）。

---

## 4. 消费输出示例

### 4.1 success 示例

```json
{
  "status": "success",
  "status_reason": "角色在知识边界和能力边界内完成决策建议",
  "answer": "基于 Q1 经营报告和项目评估，建议谨慎批准第一阶段启动...",
  "structured_result": {
    "position": "谨慎支持，但需满足前置条件",
    "key_reasons": ["项目 ROI 达 18%", "核心团队已到位"],
    "major_risks": [{"risk": "市场波动导致 ROI 下滑", "level": "medium", "mitigation": "设置阶段性复盘门禁"}],
    "preconditions": ["第一阶段预算必须到位"],
    "suggested_actions": ["批准第一阶段启动", "设置 3 个月复盘门禁"],
    "references": [{"source": "2026 Q1 经营报告", "section": "ROI 分析", "type": "knowledge"}]
  },
  "role_id": "uuid-001",
  "role_version_id": "uuid-v001",
  "usage_record_id": "uuid-u001",
  "created_at": "2026-05-26T10:00:00Z",
  "sources": [{"name": "2026 Q1 经营报告", "type": "knowledge"}],
  "boundary_status": {
    "knowledge_boundary": "within_boundary",
    "capability_boundary": "within_boundary"
  },
  "output_type": "decision_advice"
}
```

### 4.2 boundary_blocked 示例

```json
{
  "status": "boundary_blocked",
  "status_reason": "该请求要求角色执行付款动作，超出 A1 问答建议能力层级",
  "answer": "该请求超出本角色能力边界，无法执行付款动作。本角色定位为 A1 问答建议层级，不具备执行能力。建议转人工处理或使用具备 A3 执行能力的角色。",
  "structured_result": {},
  "role_id": "uuid-002",
  "role_version_id": "uuid-v002",
  "usage_record_id": "uuid-u002",
  "created_at": "2026-05-26T10:05:00Z",
  "sources": [],
  "boundary_status": {
    "knowledge_boundary": "within_boundary",
    "capability_boundary": "out_of_scope"
  },
  "output_type": "decision_advice"
}
```

### 4.3 insufficient_context 示例

```json
{
  "status": "insufficient_context",
  "status_reason": "用户请求属于角色范围，但缺少项目预算和团队信息，不足以给出可靠决策建议",
  "answer": "您的请求属于本角色的决策建议范围，但当前输入信息不足以给出可靠判断。请补充：项目预算金额、核心团队配置、预期时间线。",
  "structured_result": {},
  "role_id": "uuid-003",
  "role_version_id": "uuid-v003",
  "usage_record_id": "uuid-u003",
  "created_at": "2026-05-26T10:10:00Z",
  "sources": [],
  "boundary_status": {
    "knowledge_boundary": "within_boundary",
    "capability_boundary": "within_boundary"
  },
  "output_type": "decision_advice"
}
```

### 4.4 insufficient_knowledge 示例

```json
{
  "status": "insufficient_knowledge",
  "status_reason": "请求属于角色能力范围，但当前绑定知识未覆盖该项目的历史绩效数据",
  "answer": "本角色具备决策建议能力，但当前绑定知识中缺少该项目的历史绩效数据，无法给出完整建议。建议补充相关知识后重新调用。",
  "structured_result": {},
  "role_id": "uuid-004",
  "role_version_id": "uuid-v004",
  "usage_record_id": "uuid-u004",
  "created_at": "2026-05-26T10:15:00Z",
  "sources": [{"name": "项目简介文档", "type": "knowledge"}],
  "boundary_status": {
    "knowledge_boundary": "near_boundary",
    "capability_boundary": "within_boundary"
  },
  "output_type": "decision_advice"
}
```

### 4.5 system_failed 示例

此示例对应"已处理的下游失败"场景：LLM 调用超时或知识平台不可达，但系统仍能生成包含 status=system_failed 的完整固定治理外壳。此时返回 HTTP 200 + 固定治理外壳，生成 usage_record，计入 6 状态统计。

与"未捕获服务异常"（HTTP 500）的区别：HTTP 500 是框架级崩溃或数据库连接断开等系统无法生成治理外壳的情况，此时不返回固定治理外壳，不生成 usage_record，不计入 6 状态统计。

```json
{
  "status": "system_failed",
  "status_reason": "LLM 服务超时，无法完成调用",
  "answer": "系统暂时无法响应，请稍后重试。",
  "structured_result": {},
  "role_id": "uuid-005",
  "role_version_id": "uuid-v005",
  "usage_record_id": "uuid-u005",
  "created_at": "2026-05-26T10:20:00Z",
  "sources": [],
  "boundary_status": {
    "knowledge_boundary": "not_applicable",
    "capability_boundary": "not_applicable"
  },
  "output_type": "decision_advice"
}
```

### 4.6 undefined 示例

```json
{
  "status": "undefined",
  "status_reason": "LLM 输出内容无法稳定归类到已知状态，需人工复核",
  "answer": "本角色的响应无法被系统稳定归类，建议人工复核后判断是否可使用。",
  "structured_result": {},
  "role_id": "uuid-006",
  "role_version_id": "uuid-v006",
  "usage_record_id": "uuid-u006",
  "created_at": "2026-05-26T10:25:00Z",
  "sources": [],
  "boundary_status": {
    "knowledge_boundary": "not_applicable",
    "capability_boundary": "not_applicable"
  },
  "output_type": "decision_advice"
}
```

---

## 5. 公共契约边界说明

1. 模板字段定义、boundary_status 枚举值和联动规则均为 v0.4 角色产品内部设计定义。
2. 不等同于冻结跨项目公共契约。
3. 决策产品要稳定依赖 structured_result 字段结构时，必须上提公共契约裁决。
4. boundary_status 枚举值如需进入跨项目公共契约，也必须上提裁决。
5. v0.4.x 可扩展自定义字段和更多模板，但扩展前需规划方复审。

---

## 6. 与 DD 项的支撑关系

| DD 项 | 本文档支撑点 |
|---|---|
| DD-11 | 4 模板完整字段定义 |
| DD-16 | 6 状态定义 + boundary_status 联动规则 |
| DD-03 | 使用台展示 structured_result、status、boundary_status 的数据结构依据 |
| DD-14 | 决策产品消费 decision_advice 的输出结构依据 |
| DD-15 | Dify 消费角色时的输出结构依据 |
| DD-10 | AI 推荐 output_type 的推荐逻辑依据 |
