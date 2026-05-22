# 角色产品 → 决策产品 集成方案（反馈稿 v0.2）

> 版本：v0.3 | 日期：2026-05-14
> 发起方：角色产品（Virtual Actor）
> 接收方：决策产品（Complex_Decision）
> 性质：角色产品对决策产品集成草案的可实现方案反馈，对应协作流程 Phase 2
>
> 更新说明（v0.2 → v0.3）：
> - 纳入上位项目正式裁决结论（2026-05-14）
> - 公共字段正式冻结为最小集（必需 4 项 + 可选 6 项）
> - 质量信号字段降为双边局部扩展，不进公共字段集
> - RolePublishRecord 不进公共对象集合
> - validated_knowledge_versions 按最小追溯结构收口
> - API 直连明确为本轮局部实现方式

---

## 一、回应 §4.1 — 角色资产内部生命周期

### 1.1 四状态够用

决策草案问：`draft/test/published/archived` 是否足够，是否需要 `deprecated` / `superseded`。

**结论：四状态够用，不新增状态。**

| 状态 | 含义 | 决策产品可见性 |
|------|------|-------------|
| `draft` | 起草中，未完成 | ❌ 不可见 |
| `test` | 测试中，已保存可运行版本 | ⚠️ 仅查看，不可消费 |
| `published` | 已发布，可供调用 | ✅ 可见，可消费 |
| `archived` | 已归档，不再使用 | ⚠️ 仅查看，不可消费 |

理由：
- `deprecated` 可通过发布新版本来表达，角色升级版本即可
- `superseded` 由角色产品内部判断，不对外暴露

### 1.2 发布记录与质量信号

- 每次发布（publish）生成一个 `RolePublishRecord`，记录：发布人、发布时间、发布时的 role_version_id、变更说明
- 每次测试（test）生成一个 `TestRunRecord`，记录：测试时间、测试输入、测试输出、人工评分（可选）
- 两者各自独立，通过 `role_id` 关联

> **⚠️ RolePublishRecord 地位（上位裁决）**：`RolePublishRecord` **不进入组合公共对象集合**，不作为决策产品的默认依赖对象。决策产品如需感知发布信息，通过 `GET /role-assets/{role_id}/published-version` 接口间接获取。

#### 质量信号字段（双边局部扩展，非公共字段）

角色产品内部允许无测试记录时也可发布，以下字段作为**双边局部扩展字段**保留，供决策产品按需读取。**不进组合公共字段集，不承担公共契约地位。**

| 信号字段 | 说明 | 地位 |
|---------|------|------|
| `has_test_record` | 该角色是否存在测试记录 | 双边局部扩展 |
| `latest_test_rating` | 最近一次测试的人工评分（1-5），无记录时为 null | 双边局部扩展 |
| `latest_tested_at` | 最近一次测试时间，无记录时为 null | 双边局部扩展 |
| `test_run_count` | 累计测试次数 | 双边局部扩展 |
| `publish_confirmed_by` | 发布确认人（人工/系统） | 双边局部扩展 |

#### 知识绑定规则说明

「发布前角色至少绑定 1 条知识」是**角色产品内部质量策略**，不是跨产品公共前提。

- 角色产品内部保留该规则，以保证角色心智层有知识支撑
- 决策产品消费 `published` 角色时，不检查知识绑定数量
- 若决策产品有额外质量要求，可通过 `has_knowledge_refs` 字段自行过滤

---

## 二、回应 §4.2 — 角色测试与发布实现

### 2.1 测试记录最小字段

```json
{
  "test_run_id": "uuid",
  "role_id": "uuid",
  "role_version_id": "uuid",
  "test_input": "string",
  "test_output": "string",
  "knowledge_retrieved": [
    {
      "knowledge_id": "string",
      "chunk": "string",
      "relevance_score": 0.95
    }
  ],
  "human_rating": 1-5,
  "tested_at": "ISO8601"
}
```

### 2.2 发布前校验项

角色发布前强制校验：
1. L1 身份必填（role_name、bio 不可为空）
2. L2 心智必填（至少 point_of_view 不可为空）
3. L5 配置必填（model_binding 不可为空）
4. L3 知识绑定 ≥ 1 条（角色产品内部质量规则，非跨产品公共前提）
5. 最近一次测试记录评分 ≥ 3 分（可选，若无测试记录则允许发布）

### 2.3 发布入口与版本生成

- 发布入口：角色测试页中的「发布」按钮
- 版本生成规则：每次发布自动生成新版本（role_version_id），不可覆写已发布版本
- 版本号：内部使用 UUID，不对外暴露序号

---

## 三、回应 §4.3 — 模型绑定与知识绑定内部数据结构

### 3.1 model_binding 最小字段

```json
{
  "model_provider": "openai | anthropic | ollama | 自定义",
  "model_name": "gpt-4o | claude-3-5-sonnet | 本地模型名",
  "temperature": 0.7,
  "max_tokens": 4096,
  "fallback_enabled": false
}
```

其中 `model_provider` 和 `model_name` 为必填，其余可选。

### 3.2 knowledge_refs 与 validated_knowledge_versions 内部组织

```json
{
  "knowledge_refs": [
    {
      "knowledge_id": "ai/rag-architecture",
      "title": "RAG 架构设计",
      "type": "design",
      "bound_at_version": "abc1234",
      "bound_at_timestamp": "2026-05-14T10:00:00Z",
      "knowledge_source": "knowledge-platform"
    }
  ],
  "validated_knowledge_versions": [
    {
      "knowledge_object_id": "ai/rag-architecture",
      "knowledge_version_id": "abc1234"
    }
  ]
}
```

> **⚠️ validated_knowledge_versions 结构（上位裁决）**：若保留，只冻结最小追溯结构：
> - `knowledge_object_id`：知识对象标识，真源归知识平台 owner
> - `knowledge_version_id`：知识版本标识，真源归知识平台 owner
>
> 不额外携带 commit_hash、timestamp、platform_version 等字段，待知识平台协议确认后扩展。

### 3.3 字段可见性（v0.3 正式冻结）

> **上位裁决结论**：角色公共字段只冻结最小公共消费字段集。

| 字段 | 公共地位 | 对决策产品可见 | 说明 |
|------|---------|-------------|------|
| `role_id` | **必需** | ✅ | 角色唯一标识 |
| `role_version_id` | **必需** | ✅ | 版本唯一标识 |
| `summary` | **必需** | ✅ | 角色摘要，决策产品角色选择页必需 |
| `model_binding` | **必需** | ✅（只读） | 模型绑定，决策产品调用必需 |
| `knowledge_refs` | **可选** | ✅（摘要） | 仅展示绑定知识列表，不含 chunk |
| `identity_background` | **可选** | ✅ | 角色来源说明 |
| `point_of_view` | **可选** | ✅ | 核心视角 |
| `decision_style` | **可选** | ✅ | 决策风格 |
| `responsibility_boundary` | **可选** | ✅ | 职责边界 |
| `validated_knowledge_versions` | **可选** | ✅ | 最小追溯结构（见 §3.2 说明） |
| `has_test_record` 等 5 个质量信号字段 | 双边局部扩展 | ✅（局部） | 不进公共字段集，仅当前双边可用 |
| `RolePublishRecord` | 不进公共对象集 | ❌ | 决策产品不默认依赖，通过 published-version 接口间接获取 |
| 内部测试记录 / 草稿内容 | 内部数据 | ❌ | 角色产品内部数据，不对外暴露 |

---

## 四、公共字段正式冻结（v0.3 — 上位裁决）

> 以下字段集为上位正式裁决结果，替代 v0.2 中的候选字段方向。

### 4.1 必需字段（4 项）

| 字段名 | 说明 |
|--------|------|
| `role_id` | 角色唯一标识 |
| `role_version_id` | 版本唯一标识 |
| `summary` | 角色摘要，决策产品角色选择页必需 |
| `model_binding` | 模型绑定，决策产品调用必需 |

### 4.2 可选字段（6 项）

| 字段名 | 说明 |
|--------|------|
| `knowledge_refs` | 仅展示绑定知识列表，不含 chunk 内容 |
| `identity_background` | 角色来源说明 |
| `point_of_view` | 核心视角 |
| `decision_style` | 决策风格 |
| `responsibility_boundary` | 职责边界 |
| `validated_knowledge_versions` | 最小追溯结构（见 §3.2） |

### 4.3 双边局部扩展字段（不进公共字段集）

| 字段名 | 说明 |
|--------|------|
| `has_test_record` | 是否存在测试记录 |
| `latest_test_rating` | 最近一次测试评分 |
| `latest_tested_at` | 最近一次测试时间 |
| `test_run_count` | 累计测试次数 |
| `publish_confirmed_by` | 发布确认人 |

### 4.4 不进公共字段集的内部对象

| 对象 | 决策产品访问方式 |
|------|---------------|
| `RolePublishRecord` | 不直接暴露。通过 `GET /role-assets/{role_id}/published-version` 间接获取 |

---

## 五、回应 §8 — 公共接口范围与实现方案

### 5.1 决策产品候选 API 的实现确认

| 决策产品候选 API | 角色产品实现状态 | 说明 |
|---------------|--------------|------|
| `GET /role-assets?status=published` | ✅ 可实现 | 返回已发布角色列表，含摘要字段 |
| `GET /role-assets/{role_id}/published-version` | ✅ 可实现 | 返回当前最新发布版本的 role_version_id |
| `GET /role-versions/{role_version_id}` | ✅ 可实现 | 返回指定版本的完整公开字段 |
| 角色摘要/模型绑定/知识摘要/知识版本信息 | ✅ 可实现 | 均在 GET 返回字段中 |

### 5.2 扩展接口建议（v0.2 更新）

除 §8 候选范围外，角色产品原建议增加以下接口。**决策产品反馈后调整为：**

| 接口 | 状态 | 说明 |
|------|------|------|
| `GET /role-assets`（全状态） | ❌ 不接受 | 决策产品默认只消费 published 角色，非 published 角色通过跨产品跳转 |
| `GET /role-versions?role_id={id}&status={status}` | ⚠️ 增强项 | 暂不纳入阻断接口范围，可作为后续增强接口 |
| `POST /role-assets/{role_id}/test` | ❌ 不接受 | 角色测试属于角色产品内部生命周期，决策产品只读取测试结果信号 |

### 5.3 调用拓扑（v0.3 更新）

> **上位裁决**：当前允许本轮局部实现采用 API 直连，但**不写成组合默认模式**。

本轮实现：决策产品通过 API 直连读取角色产品。

- 两个产品独立部署，API 直连更灵活
- 决策产品按需拉取角色信息，无需维护镜像同步
- 版本冻结通过 `role_version_id` 实现，不需要实时同步

> 此为当前双边局部实现方式，不作为组合默认集成模式。后续若需升级为组合默认模式，须重新上提裁决。

---

## 六、回应 §5.3 — 版本冻结规则建议

| 规则 | 角色产品建议 | 说明 |
|------|-----------|------|
| 决策产品是否只能读取已发布版本 | ✅ 是 | draft/test 版本不对决策产品暴露 |
| 历史 run 是否必须冻结到具体 role_version_id | ✅ 是 | 每次 run 记录当时的 role_version_id，保证回放一致性 |
| 历史 run 是否允许自动升级到新版本 | ❌ 否 | 自动化升级会破坏历史 run 可追溯性 |
| 角色产品是否允许覆写已发布版本 | ❌ 否 | 已发布版本不可修改，只能发布新版本 |

---

## 七、角色产品 → 决策产品完整接口契约（v0.3 草案）

> 上位正式裁决后版本。标记说明：
> - **必需**：组合公共必需字段
> - **可选**：组合公共可选字段
> - **局部**：双边局部扩展字段（不进公共字段集）

```yaml
# ============================================================
# 最小阻断集（已正式确认）
# ============================================================

# 1. 角色列表
GET /role-assets
Query: status=published  （决策产品默认使用此过滤）
Response: [
  {
    # 必需
    role_id, role_name, bio, tags,
    role_version_id,
    summary,
    model_binding: { model_provider, model_name },
    # 可选
    identity_background?, point_of_view?, decision_style?, responsibility_boundary?,
    knowledge_refs?: [{ knowledge_id, title, type }],
    validated_knowledge_versions?: [{ knowledge_object_id, knowledge_version_id }],
    # 局部扩展（不进公共字段集，当前双边可用）
    has_test_record?, latest_test_rating?, latest_tested_at?, test_run_count?,
    publish_confirmed_by?,
    updated_at
  }
]

# 2. 当前发布版本
GET /role-assets/{role_id}/published-version
Response: {
  role_id,
  role_version_id,      # 必需
  published_at,
  published_by         # RolePublishRecord 间接暴露，非公共对象直接暴露
}

# 3. 指定版本详情
GET /role-versions/{role_version_id}
Response: {
  # 必需
  role_id, role_version_id, summary,
  model_binding: { model_provider, model_name },
  # 可选
  identity_background?, point_of_view?, decision_style?, responsibility_boundary?,
  speaking_style?,
  knowledge_refs?: [{ knowledge_id, title, type, bound_at_version }],
  validated_knowledge_versions?: [{ knowledge_object_id, knowledge_version_id }],
  # 局部扩展（不进公共字段集）
  has_test_record?, latest_test_rating?, latest_tested_at?, test_run_count?,
  publish_confirmed_by?
}

# ============================================================
# 增强接口（非阻断，后续按需接入）
# ============================================================

# 4. 角色级版本历史列表
GET /role-assets/{role_id}/versions
Query: status (optional)
Response: [
  { role_version_id, version_number, status, published_at }
]
```

---

## 八、v0.3 共识状态汇总（正式收口）

### 8.1 已正式收口项（上位裁决）

| 类别 | 结论 | 状态 |
|------|------|------|
| 公共字段冻结 | 必需 4 项（role_id、role_version_id、summary、model_binding）；可选 6 项（见 §4.2） | ✅ 正式收口 |
| 质量信号字段 | 5 个字段不进公共字段集，保留为双边局部扩展字段 | ✅ 正式收口 |
| RolePublishRecord | 不进入组合公共对象集合，决策产品不默认依赖 | ✅ 正式收口 |
| validated_knowledge_versions 结构 | 只冻结最小追溯结构：knowledge_object_id + knowledge_version_id；真源归知识平台 | ✅ 正式收口 |
| API 直连定位 | 本轮允许局部实现，不写成组合默认模式 | ✅ 正式收口 |
| 生命周期 | draft/test/published/archived 四状态，不新增 deprecated/superseded | ✅ |
| 发布消费规则 | 只能消费 published；历史 run 冻结 role_version_id；历史 run 不自动升级；已发布不可覆写 | ✅ |
| 最小阻断接口 | GET /role-assets（published）、GET .../published-version、GET /role-versions/{id} | ✅ |
| 版本冻结规则 | 4 条规则全部接受 | ✅ |

### 8.2 决策产品不接受项（本方案已处理）

| 项 | 决策产品立场 | 角色产品处理 |
|----|-----------|-----------|
| POST /role-assets/{role_id}/test | 不接受 | 从 API 契约中移除 |
| GET /role-assets 全状态默认读取 | 不接受 | 改为默认 status=published |

### 8.3 角色产品内部策略（不影响公共契约）

| 项 | 性质 |
|----|------|
| 发布前知识绑定 ≥ 1 条 | 角色产品内部质量策略，非跨产品公共前提 |
| 无测试记录也可发布 | 角色产品内部策略，质量信号字段作为局部扩展供决策产品参考 |
| 角色版本历史列表 | 增强接口，非本轮阻断项 |

### 8.4 后续依赖项

| 项 | 说明 |
|----|------|
| knowledge_object_id 格式 | 待知识平台协议确认后填入 validated_knowledge_versions |
| API 直连升级为组合默认 | 当前为局部实现，后续如需升级须重新上提 |
