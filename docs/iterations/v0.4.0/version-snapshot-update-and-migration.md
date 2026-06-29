# v0.4.0 角色版本快照数据结构更新与数据迁移策略

> 版本：v0.4.0 | 日期：2026-05-26 | Formal Status：Draft
> 类型：数据模型设计 / 数据迁移策略
> 前置依赖：consume-api-design.md、business-output-templates-and-status-rules.md

---

## 1. 当前版本快照结构（v0.3）

### 1.1 RoleVersion 元数据

| 字段 | 类型 | 说明 |
|---|---|---|
| id | String(36), PK | role_version_id (UUID) |
| role_id | String(36), FK | 所属角色 |
| version_number | Integer | 自增版本号 |
| status | String(16) | draft / test / published / archived |
| published_at | DateTime, nullable | 发布时间 |
| published_by | String(64), nullable | 发布人 |
| is_deprecated | Boolean, default=False | 不建议使用标记 |
| change_note | Text, nullable | 变更说明 |
| created_at | DateTime | 创建时间 |

### 1.2 RoleVersionField（EAV 快照）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | String(36), PK | |
| version_id | String(36), FK | 关联 RoleVersion.id |
| layer | String(4) | L1/L2/L3/L4/L5 |
| field_name | String(64) | 字段名 |
| field_value | JSON | 字段值 |

### 1.3 当前已进入快照的字段

| field_name | layer | 必填 |
|---|---|---|
| name | L1_IDENTITY | 必填 |
| bio | L1_IDENTITY | 必填 |
| tags | L1_IDENTITY | 必填 |
| identity_background | L2_MIND | 可选 |
| point_of_view | L2_MIND | 可选 |
| decision_style | L2_MIND | 可选 |
| responsibility_boundary | L2_MIND | 可选 |
| speaking_style | L2_MIND | 可选 |
| knowledge_boundary | L3_KNOWLEDGE | 可选 |
| collaboration_mode | L4_CAPABILITY | 可选 |
| capability_boundary | L4_CAPABILITY | 可选 |
| model_binding | L5_CONFIG | 必填 |
| memory_strategy | L5_CONFIG | 可选 |

---

## 2. v0.4 新增进入版本快照的字段

### 2.1 新增字段清单

| field_name | layer | 必填 | 说明 | 与 DD 项对应 |
|---|---|---|---|---|
| applicable_scenarios | L1_IDENTITY | 可选（AI 创建时生成，人确认） | 角色适用场景描述；AI 推荐匹配的前置字段 | DD-10, DD-13 |
| output_type | L5_CONFIG | v0.4 必填（发布前） | 业务输出类型枚举：decision_advice / risk_analysis / policy_explanation / review_findings | DD-11, DD-12 |
| output_schema | L5_CONFIG | v0.4 必填（发布前） | 业务输出 Schema 定义，JSON 格式；按 output_type 对应模板的默认结构 | DD-11, DD-12 |
| capability_level | L4_CAPABILITY | 必填 | 能力层级枚举：A1 / A2 / A3 | DD-05 |

### 2.2 字段说明

#### applicable_scenarios

- 类型：JSON（结构化文本或自由文本）
- 默认值：AI 创建时自动生成；手动创建时为 null
- 进入版本快照理由：不同版本可能适用不同场景（如角色从 A1 升级到 A2 后适用场景扩展）
- 消费方使用：资产市场 AI 推荐（DD-13）基于此字段匹配；资产卡片展示此字段

#### output_type

- 类型：String，枚举值
- 默认值：AI 创建时根据角色意图推荐；手动创建时为 null，发布前必须填写
- 进入版本快照理由：消费时必须知道角色输出什么类型的结构化结果，且不同版本可能使用不同输出类型
- 消费方使用：consume API 输出的 `output_type` 取自版本快照中的此字段

#### output_schema

- 类型：JSON
- 默认值：按 output_type 对应模板的默认字段结构自动填充
- 进入版本快照理由：消费时必须知道 structured_result 的结构，且已发布角色的 Schema 不可直接覆写
- v0.4 初始值：按选择的模板自动生成模板的默认字段定义
- v0.4.x 扩展：支持自定义字段追加

#### capability_level

- 类型：String，枚举：A1 / A2 / A3
- 默认值：A1（最安全的默认层级）
- 进入版本快照理由：消费时 boundary_blocked 判定需要比对请求与角色能力层级

### 2.3 LAYER_MAP 更新

v0.3 的 LAYER_MAP 需新增 4 个字段映射：

```python
# 原有映射保持不变，新增：
"applicable_scenarios": "L1_IDENTITY",
"output_type":          "L5_CONFIG",
"output_schema":        "L5_CONFIG",
"capability_level":     "L4_CAPABILITY",
```

### 2.4 发布前校验规则

v0.4 新增发布前校验：角色从 draft/test 进入 published 状态前，以下字段必须已填写：

1. output_type：必须为 4 个合法枚举值之一
2. output_schema：必须非空且为合法 JSON（至少包含模板默认字段）
3. capability_level：必须为 A1 / A2 / A3 之一
4. applicable_scenarios：可选，但资产市场 AI 推荐和业务发现视图依赖此字段；未填写时资产卡片标注"适用场景待补充"

---

## 3. RoleAsset 表新增字段（资产级属性，不进版本快照）

| 字段 | 类型 | 说明 | 是否进版本快照 |
|---|---|---|---|
| creation_source | String(16), Enum: manual / ai_assisted | 角色创建来源标记 | 不进——这是资产级属性，不属于版本内容 |
| category | String(32) | 分类（治理属性） | 不进——v0.3 已有，治理属性 |
| owner | String(64) | 所有者（治理属性） | 不进——v0.3 已有，治理属性 |
| maintainer | String(64) | 维护人（治理属性） | 不进——v0.3 已有，治理属性 |
| business_domain | String(32) | 业务域（治理属性） | 不进——v0.3 已有，治理属性 |
| visibility | String(16), Enum: internal / restricted / public | 可见范围（治理属性） | 不进——v0.3 已有，治理属性 |

creation_source 是新增字段，需要加入 RoleAsset 表（ALTER TABLE）。

---

## 4. v0.3 既有角色数据迁移策略

### 4.1 迁移原则

1. 迁移不得破坏 v0.3 已有角色的数据完整性。
2. 已 published 的角色版本不可修改快照内容。
3. 新增字段对已有角色提供合理默认值，不强制回填。
4. 迁移后系统必须仍能正常运行 v0.3 的所有功能。

### 4.2 各新增字段迁移策略

| 字段 | 既有数据 | 默认值 | 回填策略 | 是否强制 |
|---|---|---|---|---|
| capability_level | v0.3 角色无此字段 | A1 | 批量设置所有已有角色的当前 published 版本 capability_level 为 A1；draft/test 版本同样设 A1 | 不强制——A1 是最安全默认值 |
| applicable_scenarios | v0.3 角色无此字段 | null | 不批量回填；已有角色需要在编辑时补填或由运营方手动补填 | 不强制——资产市场展示时标注"适用场景待补充" |
| output_type | v0.3 角色无此字段 | null | 不批量回填；已有角色需要在编辑时选择输出类型 | **发布前强制**——已有 published 角色在下次编辑进入新版本发布前必须补填；当前已 published 版本不追溯 |
| output_schema | v0.3 角色无此字段 | null | 不批量回填；与 output_type 联动 | **发布前强制**——同 output_type |
| creation_source | v0.3 角色全部为手动创建 | manual | 批量标记所有已有角色 creation_source = manual | 不强制——manual 是合理默认值 |

### 4.3 关键决策：已有 published 角色的处理

**核心原则**：v0.3 已 published 的角色版本快照不追溯修改。

这意味着：

1. 已 published 版本的 RoleVersionField 中不补 capability_level / output_type / output_schema / applicable_scenarios。
2. 已 published 版本消费时（通过 consume API），如果版本快照中缺少 output_type，系统按 fallback 规则处理（见 4.4）。
3. 已 published 角色如需进入 v0.4 的资产市场、Dify 消费或决策产品消费，必须先创建新版本并补齐新增字段后再发布。
4. v0.4 资产市场业务发现视图默认只展示 v0.4 标准的 published 角色（具备 output_type 和 capability_level 的版本）；v0.3 标准的已 published 角色标注"需升级"。

**关键收口：legacy 角色与 v0.4 可消费标准的关系**

1. legacy published 角色（缺少 output_type）**不得进入资产市场、Dify 消费和决策产品消费的正式链路**。
2. legacy published 角色只能在使用台（caller_type: human）被消费——使用台是内部过渡入口，允许 fallback 输出。
3. 使用台对 legacy 角色的消费结果必须明确标注降级状态："该版本未配置结构化输出（需升级）"。
4. fallback 输出的 status 仍可为 success（自然语言回答成功），但 answer 中必须包含升级提示。
5. Dify 和决策产品通过 consume API 消费 legacy 角色时，consume API 返回 HTTP 400，提示"该角色版本不满足 v0.4 消费标准（缺少业务输出配置），请使用已配置输出类型的版本"。不返回 fallback success + 空 structured_result。
6. 资产市场展示 legacy 角色时标注"需升级"，不提供试用和消费入口按钮，只提供"升级版本"引导。

### 4.4 消费 API 对 v0.3 版本的 fallback 规则

consume API 对 legacy 版本的 fallback 仅限使用台（caller_type: human）场景。Dify/决策产品消费 legacy 版本时直接拒绝。

| 消费方 | 缺少 output_type 的处理 |
|---|---|
| 使用台 (human) | 允许消费；structured_result 为空对象 `{}`；answer 仍为自然语言回答；answer 中标注"该版本未配置结构化输出（需升级）"；status 可为 success（自然语言回答成功） |
| Dify (agent_platform) | 拒绝消费；返回 HTTP 400，提示"该角色版本不满足 v0.4 消费标准（缺少业务输出配置），请使用已配置输出类型的版本" |
| 决策产品 (decision_product) | 同上——拒绝消费；返回 HTTP 400 |
| 缺失 capability_level | 使用台场景按 A1 处理；Dify/决策产品同上拒绝 |

使用台 fallback 输出示例：

```json
{
  "status": "success",
  "status_reason": "角色在边界内完成自然语言回答（该版本未配置结构化输出）",
  "answer": "...自然语言回答...",
  "structured_result": {},
  "output_type": null,
  "role_id": "uuid-legacy",
  "role_version_id": "uuid-v-legacy",
  "usage_record_id": "uuid-u-legacy",
  "created_at": "2026-05-26T10:00:00Z",
  "sources": [],
  "boundary_status": {
    "knowledge_boundary": "within_boundary",
    "capability_boundary": "within_boundary"
  }
}
```

### 4.5 数据库迁移脚本要点

Alembic 迁移需要执行：

1. ALTER TABLE role_assets ADD COLUMN creation_source VARCHAR(16) DEFAULT 'manual'
2. 不修改 role_versions 表结构（新增字段通过 EAV 行插入）
3. 不修改 role_version_fields 表结构
4. 为所有已有角色的当前 draft/test/published 版本新增 EAV 行：capability_level = 'A1'
5. 已 published 版本的 capability_level EAV 行标记 is_deprecated=False（可消费）
6. 其他新增字段（output_type, output_schema, applicable_scenarios）不批量回填

---

## 5. 与 DD 项的支撑关系

| DD 项 | 本文档支撑点 |
|---|---|
| DD-05 | capability_level 进入版本快照 + 默认 A1 |
| DD-10 | applicable_scenarios + output_type 进入版本快照 + AI 创建默认值 |
| DD-11 | output_type + output_schema 进入版本快照 + 发布前强制校验 |
| DD-12 | output_schema 模板默认值策略 |
| DD-13 | applicable_scenarios 为 AI 推荐前置字段 |
| DD-16 | capability_level 为 boundary_blocked 判定依据 |
| DD-03 | 使用台需展示新增字段 + fallback 规则 |
| DD-14 | 决策产品消费需要 output_type = decision_advice |
| DD-15 | Dify 消费需要 output_type 和 structured_result |
