# v0.4.0 设计增量

> 基线来源：v0.3.0-commercial-trial Accepted
> 用途：记录本轮相对 v0.3.0 的增量设计
> 前置文档：`research-brief.md`、`research-conclusion.md`、`mvp-requirements-consensus-2026-05-26.md`、`planning-response-to-worker-feedback-2026-05-26.md`
> Dossier 回写依据：规划方裁决批准定位升级、新增统一消费 API、DD-10 扩展、DD-16 不降级、UI/UX 硬约束

## 1. 背景与目标

v0.3.0 已完成内部商业试用验收，证明角色可以被创建、绑定知识、测试、评分、发布和追溯。但角色仍停留在"配置对象"层面，缺少企业资产治理属性和正式使用入口。

产品定位已从原"角色资产化与使用入口"升级为"企业数字角色资产运营平台"。MVP 主链路：

```text
AI 创建 -> 资产治理 -> 测试发布 -> 统一消费 -> 运营证据
```

主线定位：**企业数字角色资产运营平台**。

## 2. 关键设计增量

| 设计项 | 决策 | 优先级 | 影响范围 |
|---|---|---|---|
| DD-01 | 补角色资产治理属性：分类、所有者/维护人、适用业务域、可见范围 | P0 | RoleAsset schema、创建/编辑 UI、详情页、列表页 |
| DD-02 | 边界声明补齐与强化：knowledge_boundary 全链路补齐（schema/API/UI/详情展示）；capability_boundary 已有基础入口，做资产化展示和语义强化 | P0 | RoleCreate/RoleUpdate/RoleDetail 补 knowledge_boundary、创建/编辑 UI 补 knowledge_boundary、详情页强化两个边界声明展示 |
| DD-03 | 正式使用台：区分测试台和使用台，published 角色进入使用台，新增 usage_records；usage_records 冻结 role_version_id（UUID），记录使用者、查询、回复和时间 | P0 | 新增 UI 路由、新增 schema/API、前端路由变更 |
| DD-04 | **统一消费 API 设计与实现**：新增 POST /role-assets/{role_id}/consume，作为 MVP 主链路必要能力。详细设计见 `consume-api-design.md`。公共契约边界：角色产品内部候选接口，不等同于冻结跨项目公共契约 | P0 | 新增写入接口、消费输出结构、usage_records 升级、版本选择规则 |
| DD-05 | 执行能力模型定义：A1/A2/A3 层级标注、L4 capability_level 字段（版本级属性，进入 EAV 存储和版本快照） | P1 | RoleCreate/RoleUpdate/RoleDetail schema 补 capability_level、LAYER_MAP 补映射、UI 展示 |
| DD-07 | 历史版本详情入口：版本列表页 + 版本内容查看 | P2 | 新增 UI 路由、前端路由变更 |
| DD-08 | 详情页枚举中文映射 | P2 | 详情页、列表页前端显示 |
| DD-09 | 角色资产运营看板：资产总览、创建运营（AI 草案接受率）、质量运营、使用运营（含消费状态分布）、风险运营 | P0 | 新增 UI 路由、新增 usage_records 统计查询、creation_source 字段统计 |
| DD-10 | AI 协作创建：AI 生成角色草案 + 推荐 output_type + 生成 applicable_scenarios + 推荐输出 Schema 默认结构。详细规格见 `dd10-ai-creation-extended-spec.md` | P0 | 新增 AI 创建 UI 流程、新增 LLM 调用链路、creation_source 自动标记 |
| DD-11 | 业务输出 Schema：4 内置模板 + output_type/structured_result + 版本快照。详细字段定义见 `business-output-templates-and-status-rules.md` | P0 | 新增 EAV 字段（output_type/output_schema）、4 模板默认结构、consume API 输出结构 |
| DD-12 | 业务输出配置体验：面向业务语言的配置界面 + 模板选择 + AI 推荐 output_type | P0 | 新增 UI 配置页、AI 推荐逻辑 |
| DD-13 | 资产市场 AI 推荐入口：业务意图→已发布角色匹配 + 推荐理由 + 运营信号 + 场景入口 + 资产卡片。推荐链路为四阶段引擎（准入过滤→候选召回→LLM judge→阈值过滤），推荐结果分 4 类：matched/no_match/out_of_scope/service_error。推荐池准入：角色须同时具备 output_type + business_domain + applicable_scenarios + bio 才能进入 AI 推荐。详细设计见 handoff `dd13-recommend-rereview-submission-2026-05-27.md` 和 `dd13-recommend-pool-eligibility-2026-05-27.md` | P1 | 新增推荐 API、四阶段推荐引擎、4 类结果区分、推荐池准入、前端场景卡片/AI 推荐区/推荐结果态/空态/返回列表 |
| DD-14 | 决策产品集成验收：决策产品真实集成 + 双方证据闭合。**不降级** | P0 | 跨项目协调、集成适配层、双方验收 |
| DD-15 | Dify 消费证明：开放 Agent 平台消费 published 角色代表证明 + 验收证据。技术评估见 `dify-integration-tech-evaluation.md` | P1 | Dify 集成代码、消费方身份记录、跨平台调用 |
| DD-16 | 统一消费结果状态：6 状态 + boundary_status 复合结构 + 命中规则 + 消费方处理方式。详细规则见 `business-output-templates-and-status-rules.md`。**不降级为 4 状态** | P0 | LLM 调用链路改造（状态判定逻辑）、consume API 响应结构 |

## 3. 数据与状态变化

### 3.1 必需新增字段（DD-01）

| 字段 | 位置 | 类型 | 说明 |
|---|---|---|---|
| category | RoleAsset | String(32) | 资产分类（行业专家/职能助手/制度顾问/项目管理/自定义） |
| owner | RoleAsset | String(64) | 资产所有者 |
| maintainer | RoleAsset | String(64) | 维护人 |
| business_domain | RoleAsset | String(64) | 适用业务域 |
| visibility | RoleAsset | String(16) | 可见范围（内部/部门/公开），默认内部 |
| applicable_scenarios | RoleVersionField (EAV) | JSON | 适用场景描述（角色内容属性，AI 创建时生成，人确认后保存，进入版本快照）。详见 `dd10-ai-creation-extended-spec.md` |
| creation_source | RoleAsset | String(16) | 创建来源标记（枚举：manual/ai_assisted），AI 草案保存时自动标记为 ai_assisted。不进版本快照（资产级属性） |

#### 字段详细说明

| 字段 | 枚举值 | 默认值 | 填写位置 | 展示位置 | 篩选支持 | 是否进入版本快照 | 权限语义 |
|---|---|---|---|---|---|---|---|
| category | 行业专家、职能助手、制度顾问、项目管理、自定义 | 自定义 | 创建/编辑页（下拉选择） | 详情页、列表页（标签） | 列表页 category 篩选 | **否** — category 是资产级属性，不属于角色版本内容 | 仅展示与筛选属性，**不暗含 RBAC 或多租户权限能力** |
| owner | 自由文本（人员姓名或标识） | 空（创建时必填） | 创建/编辑页（文本输入） | 详情页、列表页 | 列表页 owner 篩选 | **否** — owner 是资产级属性，不属于角色版本内容 | 仅展示与筛选属性，**不暗含 RBAC 或多租户权限能力** |
| maintainer | 自由文本（人员姓名或标识） | 空（编辑时可选） | 创建/编辑页（文本输入） | 详情页 | 不支持列表页篩选 | **否** — maintainer 是资产级属性，不属于角色版本内容 | 仅展示与筛选属性，**不暗含 RBAC 或多租户权限能力** |
| business_domain | 自由文本（业务域名称） | 空（创建时可选） | 创建/编辑页（文本输入） | 详情页、列表页（标签） | 列表页 business_domain 篩选 | **否** — business_domain 是资产级属性，不属于角色版本内容 | 仅展示与筛选属性，**不暗含 RBAC 或多租户权限能力** |
| visibility | 内部、部门、公开 | 内部 | 创建/编辑页（下拉选择） | 详情页、列表页 | 列表页 visibility 篩选 | **否** — visibility 是资产级属性，不属于角色版本内容 | 仅展示与筛选属性，**不暗含 RBAC 或多租户权限能力**。v0.4 不基于 visibility 实现任何访问控制逻辑 |

字段归属说明：

1. 上述 5 个字段均为 **RoleAsset 级属性**（资产级），不属于 RoleVersion 级属性（版本级）。
2. **不进入版本快照**：角色版本变更时，这 5 个字段不随版本内容保存，而是在 RoleAsset 表上直接更新。
3. **仅展示与筛选属性**：这些字段用于角色资产的分类、归属标识和列表筛选，**不暗含 RBAC、多租户或访问控制能力**。v0.4 不基于 visibility 字段实现任何访问控制逻辑。
4. 如果上位治理要求将这些字段纳入公共对象或赋予权限语义，必须先上提裁决，不直接在 v0.4 中实现。

### 3.2 必需新增字段（DD-02）

| 字段 | 位置 | 类型 | 说明 |
|---|---|---|---|
| knowledge_boundary | RoleCreate / RoleUpdate / RoleDetail | String | L3 知识边界声明，当前全链路缺失（schema/API/UI/前端类型均无此字段），需补全链路 |
| capability_boundary | 已存在于 RoleCreate / RoleUpdate / RoleDetail | String | L4 能力边界声明，已有 schema/API/UI/详情页基础入口，v0.4 做资产化展示和语义强化，不新增字段 |

### 3.3 必需新增概念（DD-03）

#### 使用台 (Usage Desk)

| 概念 | 说明 |
|---|---|
| 使用台 (Usage Desk) | published 角色的正式使用入口，区分于测试台 |

使用台与测试台的区分：

| 维度 | 测试台 | 使用台 |
|---|---|---|
| 目的 | 验证角色质量，决定是否发布 | 正式使用已发布角色获取专业建议 |
| 可用条件 | 角色处于 test 状态 | 角色处于 published 状态 |
| 记录类型 | test_runs | usage_records |
| 评分 | 人工评分 (1-5 星) | 使用反馈 (可选，v0.4 不实现评分) |
| 对发布的影响 | 测试评分影响发布门禁 | 使用记录不影响发布门禁 |
| 谁使用 | 角色管理者 / 测试人员 | 角色使用者 (一线员工 / 管理层) |
| UI 入口 | 角色详情页"测试"按钮 | 角色详情页"使用"按钮（仅 published 角色显示） |

#### usage_records

| 概念 | 说明 |
|---|---|
| usage_records | 使用记录，与 test_runs 区分。v0.4 升级为包含 caller_type/caller_id/status/boundary_status/structured_result/output_type/sources |

usage_records 数据模型（与 consume API 输出对齐，详见 `consume-api-design.md §5`）：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | String(36) (PK) | 使用记录唯一标识，UUID，与 RoleAsset.id 口径一致 |
| role_asset_id | String(36) (FK → RoleAsset.id) | 关联角色资产 |
| role_version_id | String(36) (FK → RoleVersion.id) | **冻结**：消费时快照当前 published 版本 UUID |
| user_id / caller_id | String(128) | 调用方标识 |
| caller_type | Enum | 调用方类型：human / agent_platform / decision_product / system |
| query | String(2048) | 消费者输入的查询内容 |
| context | String(4096), optional | 业务上下文 |
| answer | String(8192) | 角色回复的自然语言内容 |
| structured_result | String (JSON) | 按角色业务 Schema 生成的结构化结果 |
| output_type | String | 实际使用的输出类型 |
| status | Enum (6) | 消费结果状态 |
| status_reason | String | 状态原因说明 |
| boundary_status | String (JSON) | boundary_status 复合结构 JSON |
| sources | String (JSON array) | 知识来源/引用来源 |
| knowledge_snapshot | String (JSON, optional) | 知识版本快照摘要（v0.4 不强制填写） |
| created_at | DateTime | 消费时间 |

版本冻结规则：

1. **usage_records 必须冻结 role_version_id**：使用记录关联的是角色发布时的具体版本，而非角色资产整体。角色后续更新产生新版本时，历史 usage_records 的 role_version_id 不变。
2. **v0.4 不记录 LLM 输出元数据和失败记录**：usage_records 只记录查询和回复文本。LLM token 用量、模型参数、调用失败等暂不纳入，后续版本评估扩展。
3. **v0.4 不实现使用反馈评分**：使用台不设评分功能。后续版本可评估使用满意度反馈。

验收边界：

1. 使用台 UI 仅对 published 角色显示入口，其他状态角色不显示。
2. 使用记录与测试记录在 UI 和数据层面完全区分：不同页面、不同数据表、不同 API。
3. usage_records 的 role_version_id 冻结后不可变更。
4. 如果使用台需要新增读写 API（POST /role-assets/{id}/usage, GET /role-assets/{id}/usage-records），必须先回写 dossier 再实现。

### 3.4 必需新增字段（DD-05）

| 字段 | 位置 | 类型 | 说明 |
|---|---|---|---|
| capability_level | RoleCreate / RoleUpdate / RoleDetail | String(4) | A1/A2/A3 能力层级标注，默认 A1 |

#### capability_level 归属与链路收口

归属层级：**版本级属性**（不属于 RoleAsset 资产级）。

理由：能力层级是角色版本的内容属性——同一角色在不同版本可能处于不同能力层级（如 v1 标注 A1 问答建议，v2 升级为 A2 生成产物）。因此 capability_level 应随版本内容保存和追溯，而非在 RoleAsset 表上独立更新。

全链路设计：

| 链路段 | 当前状态 | v0.4 需补 | 说明 |
|---|---|---|---|
| Schema 写入口 | 不存在 | RoleCreate + RoleUpdate 补 capability_level: str | None = None | 创建/编辑时可填写 |
| Schema 读入口 | 不存在 | RoleDetail 补 capability_level: str | None | 详情页展示需回读 |
| 对外版本响应 | RoleVersionPublicResponse 不包含此字段 | **v0.4 不纳入 RoleVersionPublicResponse** | 消费侧 API 不暴露内部能力层级标注，后续版本视裁决决定 |
| 持久化 | LAYER_MAP 和 _save_fields 不包含此字段 | LAYER_MAP 补 "capability_level": Layer.L4_CAPABILITY；_save_fields 补 capability_level | 进入现有 EAV 存储链路，与 capability_boundary 同属 L4 |
| 版本快照 | **进入版本快照** | _save_fields 包含此字段后自动进入版本快照 | 作为版本级属性，随 RoleVersionField EAV 存储，版本发布时一并冻结 |
| 前端类型 | 不存在 | api.ts RoleDetail interface 补 capability_level | 详情页回读需类型定义 |
| UI 写入口 | 不存在 | RoleEdit.tsx 创建/编辑页补 capability_level 下拉选择 | A1 问答建议 / A2 生成产物 / A3 执行动作 |
| UI 读入口 | 不存在 | RoleDetail.tsx 详情页补 capability_level 展示 | 展示能力层级标注和语义说明 |

枚举与默认值：

| 枚举值 | 含义 | 默认行为 |
|---|---|---|
| A1 | 问答建议：基于知识回答、分析、总结、提出建议 | 默认值：未填写时默认 A1 |
| A2 | 生成产物：生成报告、方案、会议纪要等（v0.4 只定义模型，不实现） | 可选填写 |
| A3 | 执行动作：调用工具或系统完成任务（v0.4 不实现） | 可选填写，但 UI 标注"v0.4 不实现 A3 执行机制" |

不纳入对外版本响应的理由：capability_level 是角色产品内部治理标注，用于角色管理者声明角色的能力边界。消费方（决策产品、外部系统）当前不需要此信息。如果后续上位治理要求消费方感知角色能力层级，需先通过公共契约裁决，v0.4 不主动扩展对外接口。

### 3.4a 必需新增字段与概念（DD-13）

| 字段/概念 | 位置 | 类型 | 说明 |
|---|---|---|---|
| recommend_pool_eligible | RoleListItem (响应字段) | Boolean | 是否满足 AI 推荐池准入条件。准入条件：output_type + business_domain + applicable_scenarios(>=1) + bio(>=5字符)。不满足的角色仍在市场列表可见，但不参与 AI 推荐 |
| result_type | RecommendResponse (响应字段) | Enum | 推荐结果类型：matched（匹配成功）/no_match（业务范围内无覆盖，记录 OpsSignal）/out_of_scope（超出企业业务场景范围，不记录 OpsSignal）/service_error（推荐服务故障，不记录 OpsSignal） |
| match_score | RecommendItem (响应字段) | Float | LLM judge 给出的匹配评分（0-1），低于 0.5 阈值的角色不进入推荐结果 |
| service_error_message | RecommendResponse (响应字段) | String | service_error 时向用户展示的故障信息 |

推荐链路设计（DD-13 四阶段引擎）：

1. **Phase 1 准入过滤**：published 角色须满足 4 项准入条件才进入 AI 推荐候选池
2. **Phase 2 非 LLM 候选召回**：关键词映射 + business_domain/applicable_scenarios/tags 多维召回，按得分降序取前 10，保守优先
3. **Phase 3 单次 LLM judge/rerank**：一次 LLM call 同时完成意图分析（is_out_of_scope）+ 每个候选角色的 match/score/reason 判断
4. **Phase 4 阈值过滤 + 保守拒绝**：score < 0.5 拒绝；is_out_of_scope 整批拒绝；LLM 失败保守拒绝（service_error，不放宽推荐）

阈值 0.5 选择理由：score 中点，匹配度不足一半不应推荐。正向样例 0.85>0.5 成立，反向样例 0.15<0.5 成立。

### 3.4b AI 链路模型可配置（DD-13/DD-10 补充）

AI 推荐（DD-13）和 AI 创建草案（DD-10）使用的 LLM 模型通过独立环境变量配置，不再硬编码。

| 配置项 | 环境变量 | 默认值 | 用途 |
|---|---|---|---|
| AI 推荐模型 | AI_RECOMMEND_MODEL | deepseek-v4-pro | 推荐链路 LLM judge/rerank |
| AI 推荐温度 | AI_RECOMMEND_TEMPERATURE | 0.3 | 推荐链路 LLM temperature |
| AI 推荐最大 token | AI_RECOMMEND_MAX_TOKENS | 4096 | 推荐链路 LLM max_tokens |
| AI 创建模型 | AI_CREATE_MODEL | deepseek-v4-pro | 创建草案链路 LLM |
| AI 创建温度 | AI_CREATE_TEMPERATURE | 0.7 | 创建草案链路 LLM temperature |
| AI 创建最大 token | AI_CREATE_MAX_TOKENS | 4096 | 创建草案链路 LLM max_tokens |

默认值与原硬编码值一致。角色测试/consume 路径使用 model_binding 机制（每角色独立配置），与上述 AI 链路配置无关。详见 handoff `ai-model-config-implementation-2026-05-28.md`。

### 3.4c 知识平台健康检查（补充）

知识平台健康检查不再使用独立的 `KNOWLEDGE_HEALTH_URL` 环境变量（已移除），改为基于 `KNOWLEDGE_API_BASE` + `/api/v1/version` 端点检查（与 `get_version()` 共用同一端点）。虚拟资产产品暴露 `/health/knowledge-platform` 端点供外部检查。

### 3.5 不变的部分

- 4 状态机 (draft/test/published/archived) 保持不变
- KnowledgeRef + ValidatedKnowledgeVersion 保持不变
- TestRunRecord 保持不变（测试记录不变，但测试台 UI 升级）
- RoleVersion 不可覆写机制保持不变
- 消费侧只读 API (GET /role-assets, GET /role-versions/{id}) 不改变
- **新增统一消费 API (POST /role-assets/{role_id}/consume)** — 规划方裁决批准回写，详见 `consume-api-design.md`

### 3.6 新增进入版本快照的字段（DD-11/DD-10/DD-05）

详见 `version-snapshot-update-and-migration.md §2`：

| field_name | layer | 说明 |
|---|---|---|
| applicable_scenarios | L1_IDENTITY | 角色适用场景描述（AI 创建时生成） |
| output_type | L5_CONFIG | 业务输出类型枚举（发布前必填） |
| output_schema | L5_CONFIG | 业务输出 Schema 定义（按 output_type 模板默认结构） |
| capability_level | L4_CAPABILITY | 能力层级 A1/A2/A3（默认 A1） |

### 3.7 v0.3 既有角色数据迁移策略

详见 `version-snapshot-update-and-migration.md §4`：

1. 已 published 版本快照不追溯修改
2. capability_level 批量设为 A1
3. creation_source 批量设为 manual
4. output_type/output_schema/applicable_scenarios 不批量回填
5. 已 published 角色下次发布新版本前必须补填 output_type/output_schema

## 4. UI 路径变化

| 路径 | 变化类型 | 说明 |
|---|---|---|
| /roles/:id/use | 新增 | 使用台页面，仅 published 角色可进入 |
| /roles/:id | 变更 | 详情页补资产治理属性展示、边界声明展示、中文枚举映射 |
| /roles/:id/edit | 变更 | 创建/编辑页补资产治理属性字段、边界声明字段、capability_level |
| /roles/:id/versions | 新增 | 版本详情列表页 |
| / | 变更 | 列表页补分类筛选、所有者筛选、中文枚举 |

## 5. 风险与边界

1. **统一消费 API 公共契约边界** — consume API 是角色产品内部候选接口，不等同于冻结跨项目公共契约。如果决策产品要稳定依赖此 API 的输入/输出/状态字段，必须上提公共契约裁决。
2. **资产治理属性** — 分类、可见范围等字段当前作为角色产品内部概念，如果上位治理要求纳入公共对象，必须先上提裁决。
3. **A3 执行** — v0.4 不实现 A3，如果后续涉及工具权限或跨系统调用，必须先上提裁决。
4. **DD-14 决策产品集成** — 不降级；双方证据必须闭合；如发现公共契约、读写边界或版本规则问题，必须上提治理裁决。
5. **DD-16 不降级** — 6 状态固定，不降级为 4 状态；保守判定策略允许但不移除交付语义。
6. **不得把 mock/stub/fixture 描述为真实集成证据。**
7. **不得把知识平台当前 Accepted 范围表述为长期冻结公共契约版本。**
8. **不得自行把已确认的产品本质降级为较弱交付。**
9. **UI/UX 硬约束** — 进入实现前必须完成 UI/UX 原型、用户任务流、场景走查、验收点、Human 检查清单和设计冻结记录。设计冻结后不得自行改变关键交互。

## 6. 待裁决项

| 裁决项 | 说明 | 建议 |
|---|---|---|
| 统一消费 API 是否成为跨项目公共契约 | 决策产品和 Dify 要稳定依赖 consume API 的字段、状态和输出结构 | 先作为角色产品内部候选接口，后续视裁决扩展 |
| 业务输出 Schema 是否纳入公共对象 | 如果上位治理要求 business output schema 成为跨项目标准 | 先允许角色产品内部定义 4 模板，后续视裁决扩展 |
| boundary_status/status 字段是否进入公共契约 | 决策产品可能要求这些字段有稳定定义 | 先作为角色产品内部字段，后续视消费方依赖程度裁决 |
| "角色资产"是否纳入公共对象 | 如果上位治理要求角色资产成为跨项目公共对象 | 先作为角色产品内部概念，后续视裁决扩展 |
