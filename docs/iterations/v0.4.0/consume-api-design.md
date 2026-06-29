# v0.4.0 统一消费 API 设计文档

> 版本：v0.4.0 | 日期：2026-05-26 | Formal Status：Draft
> 类型：角色产品本地候选接口 / 集成验证接口
> 公共契约边界：不等同于冻结跨项目公共契约；决策产品要稳定依赖输入输出字段/状态/版本规则时，必须上提公共契约裁决

## 1. 定位与边界

统一消费 API 是 v0.4 MVP 主链路 `AI 创建 -> 资产治理 -> 测试发布 -> 统一消费 -> 运营证据` 中"统一消费"环节的必要能力。

三类消费形态共用此 API：

1. 资产目录试用：人类发现并试用已发布角色
2. Dify 代表验证：开放 Agent 平台消费已发布角色
3. 决策产品集成：产品组合内受治理消费方消费已发布角色

此 API 是角色产品内部候选接口，用于本轮集成验证。在上位治理确认前，不得表述为长期冻结跨项目公共契约。

## 2. API 路径与方法

### 2.1 消费入口

```
POST /role-assets/{role_id}/consume
```

路径参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| role_id | String(36) UUID | 角色资产 ID，必填 |

### 2.2 消费查询（使用记录查询）

```
GET /role-assets/{role_id}/consume-records
```

路径参数同上。查询参数支持分页和筛选。

## 3. 输入模型

### 3.1 消费请求输入

```json
{
  "role_version_id": "string(36) UUID, optional",
  "query": "string(2048), required",
  "context": "string(4096), optional",
  "output_type": "string, optional",
  "caller_type": "enum, optional but recommended",
  "caller_id": "string(128), optional but recommended"
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| role_id | String(36) | 必填（路径参数） | 角色资产 ID |
| role_version_id | String(36) | 可选 | 指定已发布角色版本 UUID；不填时使用当前 published 版本 |
| query | String(2048) | 必填 | 用户问题或业务请求 |
| context | String(4096) | 可选 | 业务上下文信息 |
| output_type | String | 可选 | 指定输出类型（decision_advice/risk_analysis/policy_explanation/review_findings）；不填时使用角色版本配置的默认 output_type |
| caller_type | Enum | 可选但建议记录 | 调用方类型：human / agent_platform / decision_product / system |
| caller_id | String(128) | 可选但建议记录 | 调用方标识（如 Dify workflow ID、决策产品场景 ID、用户 ID） |

### 3.2 版本选择规则

| 场景 | 规则 | 输出行为 |
|---|---|---|
| 只传 role_id | 系统使用该角色当前 published 版本 | 输出中必须明确实际使用的 role_version_id |
| 同时传 role_id + role_version_id | 系统校验版本归属和状态，严格使用指定版本 | 使用指定版本 |
| role_version_id 不属于该 role_id | 拒绝调用 | 返回 HTTP 400，`{ "detail": "指定的版本不属于该角色" }`；不返回固定治理外壳，不生成 usage_record |
| 指定版本已归档或不可消费 | 拒绝调用 | 返回 HTTP 400，`{ "detail": "指定版本不可消费（已归档）" }`；不返回固定治理外壳，不生成 usage_record，不自动 fallback |

## 4. 输出模型

### 4.1 固定治理外壳

每次消费输出必须包含以下固定字段：

```json
{
  "answer": "string, 自然语言回答",
  "role_id": "string(36) UUID",
  "role_version_id": "string(36) UUID, 本次消费绑定的角色版本",
  "usage_record_id": "string(36) UUID, 本次使用记录 ID",
  "created_at": "datetime, ISO 8601",
  "sources": "array, 知识来源/引用来源",
  "boundary_status": {
    "knowledge_boundary": "enum",
    "capability_boundary": "enum"
  },
  "output_type": "string, 本次实际使用的输出类型",
  "structured_result": "object, 按角色业务 Schema 生成的结构化结果",
  "status": "enum, 6 状态之一",
  "status_reason": "string, 状态原因说明"
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| answer | String | 给人阅读的自然语言回答 |
| role_id | String(36) UUID | 角色资产 ID |
| role_version_id | String(36) UUID | 本次消费实际使用的角色版本 |
| usage_record_id | String(36) UUID | 本次使用记录 ID |
| created_at | DateTime ISO 8601 | 调用时间 |
| sources | Array | 知识来源/引用来源列表 |
| boundary_status | Object | 复合结构：knowledge_boundary + capability_boundary 各维度的枚举值 |
| output_type | String | 本次实际使用的输出类型 |
| structured_result | Object | 按角色业务 Schema 生成的结构化结果 |
| status | Enum (6) | 消费结果状态 |
| status_reason | String | 状态原因说明 |

### 4.2 boundary_status 复合结构

boundary_status 是 knowledge_boundary 和 capability_boundary 各维度的组合对象。每个维度的枚举值：

| 枚举值 | 中文名 | 含义 |
|---|---|---|
| within_boundary | 边界内 | 请求在该维度边界内 |
| near_boundary | 接近边界 | 请求接近该维度边界但未越界 |
| out_of_scope | 越界 | 请求超出该维度边界 |
| not_applicable | 不适用 | 该维度边界判定不适用（如系统失败时） |

与 6 消费状态联动规则：

| 消费状态 | boundary_status 各维度可能值 |
|---|---|
| success | knowledge_boundary: within_boundary 或 near_boundary；capability_boundary: within_boundary 或 near_boundary |
| boundary_blocked | 至少一个维度: out_of_scope |
| insufficient_context | knowledge_boundary: within_boundary（请求属于范围但输入不足）；capability_boundary: within_boundary |
| insufficient_knowledge | knowledge_boundary: near_boundary 或 within_boundary（请求属于范围但知识不足）；capability_boundary: within_boundary |
| system_failed | 各维度: not_applicable |
| undefined | 各维度: not_applicable |

### 4.3 消费结果状态（6 状态固定）

| 状态 | 中文名 | 命中规则 | 消费方处理 | 运营含义 |
|---|---|---|---|---|
| success | 成功 | 角色在知识边界和能力边界内完成回答或结构化输出 | 可展示、可继续流程、可进入正式记录 | 正常使用 |
| insufficient_context | 上下文不足 | 用户请求属于角色范围，但输入信息不足以给出可靠结果 | 提示补充信息，或由上游 Agent 继续收集上下文 | 输入质量问题，不归因于角色质量 |
| insufficient_knowledge | 知识不足 | 请求属于角色能力范围，但绑定知识或当前知识版本无法支撑可靠回答 | 不应作为正式结论，可提示补充知识或换角色 | 知识缺口、知识过期或绑定不足 |
| boundary_blocked | 边界阻断 | 请求超出角色知识边界、能力边界或能力层级（如 A1 角色被要求执行动作） | 停止使用该角色结果，转人工、换角色或进入更高能力流程 | 边界治理生效，不应简单视为失败 |
| system_failed | 系统失败 | LLM、知识平台、数据库、网络、超时等系统性异常导致无法完成调用 | 可重试或提示系统错误 | 系统稳定性问题，不归因于角色质量 |
| undefined | 未定义 | 无法稳定归类到上述状态，或规则不足以判断 | 慎展示，标记为需人工复核 | 状态规则缺口，需产品和运营复盘 |

保守判定策略：

1. insufficient_context 和 insufficient_knowledge 采用保守判定——当 LLM 判断置信度不够时，优先降入 undefined 而不是硬判。
2. 每次消费必须返回 status 和 status_reason。
3. 非 success 不应被消费方当作正常业务结论继续流转。
4. undefined 是兜底和复盘信号，不应长期大量使用。

## 5. 使用记录数据模型

每次消费调用生成一条 usage_record，与 consume API 输入输出对齐。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | String(36) UUID (PK) | 使用记录唯一标识，与 RoleAsset.id 口径一致 |
| role_asset_id | String(36) UUID (FK → RoleAsset.id) | 关联角色资产 |
| role_version_id | String(36) UUID (FK → RoleVersion.id) | **冻结**：消费时快照当前 published 版本 UUID |
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

1. usage_record 的 role_version_id 冻结后不可变更。
2. 角色后续更新产生新版本时，历史 usage_record 的 role_version_id 不变。
3. v0.4 不记录 LLM 输出元数据和失败记录（只记录 query/answer/status）。

## 6. 与既有数据模型的关系

### 6.1 与 usage_records（原 DD-03）的关系

原 DD-03 定义的使用台使用记录和统一消费 API 的消费记录是同一概念——usage_records 表既存储使用台的人类使用记录，也存储 Dify/决策产品的外部消费记录。caller_type 字段区分来源。

### 6.2 与 test_runs 的区分

| 维度 | test_runs（测试记录） | usage_records（使用/消费记录） |
|---|---|---|
| 目的 | 验证角色质量 | 正式使用角色获取专业建议 |
| 可用条件 | 角色处于 test 状态 | 角色处于 published 状态 |
| 评分 | 1-5 星 | v0.4 不实现评分 |
| 调用方类型 | human（测试人员） | human / agent_platform / decision_product / system |
| 输出格式 | 自然语言（v0.3） | 固定治理外壳 + structured_result + status（v0.4） |

### 6.3 consume API 与使用台 UI 的关系

使用台页面（/roles/:id/use）是人类消费方（caller_type: human）的 UI 入口，底层调用同一个 consume API。

Dify 和决策产品通过 HTTP API 直接调用 consume API（caller_type: agent_platform / decision_product）。

## 7. 错误处理

| HTTP 状态码 | 场景 | 返回内容 |
|---|---|---|
| 200 | 消费调用成功完成（包括已处理的下游失败：LLM 超时/不可达但系统仍能返回 system_failed 治理外壳） | 完整固定治理外壳 |
| 400 | role_version_id 不属于 role_id、指定版本不可消费（已归档） | `{ "detail": "具体错误原因" }` |
| 403 | 角色不可消费（draft/test 状态） | `{ "detail": "角色处于 draft/test 状态，不可通过消费 API 消费" }` |
| 404 | role_id 不存在 | `{ "detail": "角色资产不存在" }` |
| 500 | 未捕获服务异常（框架级崩溃、数据库连接断开等系统无法生成治理外壳的情况） | `{ "detail": "服务异常" }` |

注意：

1. HTTP 200 响应中 status 字段可以是任何 6 状态值（包括 boundary_blocked、system_failed 等），因为消费调用本身已被系统处理并返回了完整的治理外壳。这是"已处理的下游失败"：即使 LLM 调用超时或知识平台不可达，系统仍能生成包含 status=system_failed 的完整治理外壳，此时生成 usage_record 并计入 6 状态统计。
2. HTTP 400/403/404 是调用方输入错误或权限/状态错误，不属于 6 状态的业务语义范围——这些错误不返回固定治理外壳，不生成 usage_record，不计入运营看板的 6 状态统计。
3. 只有 HTTP 200 的消费结果才进入 6 状态统计和 usage_record。HTTP 200 + status=system_failed 属于"已处理的下游失败"，计入 6 状态统计。
4. HTTP 500 是未捕获的服务异常——系统无法生成固定治理外壳，不生成 usage_record，不计入 6 状态统计。这类错误应在运营看板中作为"服务可用性异常"单独统计，与 6 状态统计分开。

### 7.1 v0.3 legacy 角色消费分流规则

v0.3 已 published 但缺少 output_type/output_schema 的角色（legacy 角色），按消费方类型分流：

| 消费方 | legacy 角色处理 |
|---|---|
| 使用台 (caller_type: human) | 允许消费；output_type 为 null，structured_result 为空对象 {}；answer 中标注"该版本未配置结构化输出（需升级）"；status 可为 success（自然语言回答成功） |
| Dify (caller_type: agent_platform) | 拒绝消费；返回 HTTP 400，提示"该角色版本不满足 v0.4 消费标准（缺少业务输出配置），请使用已配置输出类型的版本" |
| 决策产品 (caller_type: decision_product) | 拒绝消费；同 Dify 规则——返回 HTTP 400 |
| 缺失 capability_level | 使用台按 A1 处理；Dify/决策产品同上拒绝 |

legacy 角色不得进入资产市场正式消费链路、Dify 消费和决策产品消费。详细策略见 `version-snapshot-update-and-migration.md §4.3~4.4`。

## 8. 公共契约边界说明

1. 此 API 是角色产品内部候选接口，用于 v0.4 集成验证。
2. 路径、输入输出 schema、状态枚举、版本选择规则均为 v0.4 设计定义，不等同于冻结跨项目公共契约。
3. 如果决策产品要求稳定依赖此 API 的输入字段、输出字段、status 枚举、boundary_status 结构或版本选择规则，必须上提公共契约裁决。
4. portfolio-sync.md 后续应明确 Interface Delta 为候选或待裁决状态，不得写成 Accepted public contract。
5. Dify 集成验证仅证明"开放 Agent 平台可以消费已发布角色资产"，不外推为所有开放平台均已支持。

## 9. 与 DD 项的支撑关系

| DD 项 | consume API 支撑点 |
|---|---|
| DD-03 | 使用台 UI 底层调用 consume API（caller_type: human） |
| DD-11 | structured_result 和 output_type 由 consume API 输出 |
| DD-14 | 决策产品通过 consume API 消费角色（caller_type: decision_product） |
| DD-15 | Dify 通过 consume API 消费角色（caller_type: agent_platform） |
| DD-16 | 6 状态由 consume API 返回 |

## 10. 后续扩展方向（v0.4 不实现）

1. 消费侧 API 版本化（/v1/ 前缀）
2. 批量消费接口
3. 消费回调机制
4. 流式输出（SSE/WebSocket）
5. 消费权限校验（基于 visibility 字段，需公共契约裁决）
6. MCP/A2A 协议适配
