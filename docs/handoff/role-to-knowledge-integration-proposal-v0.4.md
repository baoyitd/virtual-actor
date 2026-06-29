# 角色产品 → 知识平台 集成方案（v0.4 — Knowledge Workbench 公共契约接口）

> 版本：v0.4 | 日期：2026-06-17
> 发起方：角色产品（Virtual Actor）
> 接收方：知识平台（Knowledge Workbench）
> 状态：**公共契约裁决已通过，Knowledge Workbench 接口已交付，Open WebUI 适配器待就绪**
>
> 更新说明（v0.3 → v0.4）：
>
> - 公共契约裁决通过：接口对接点从 Open WebUI 变更为 Knowledge Workbench 公共契约接口
> - Open WebUI 退为 Knowledge Workbench 内部执行适配层
> - 接口从4项扩展为 Knowledge Workbench 协议层接口集（packages/manifest/route/retrieve/status）
> - retrieve 支持简化模式（含 Q0 越界拒答）和显式模式
> - 检索结果携带 tier/doc_role/evidence_type 结构化元数据
> - v0.3（Open WebUI 端点）保留为历史基线，不再作为当前有效接口契约

---

## 一、v0.4 接口总览

| 接口 | 端点 | 方法 | 满足场景 | 状态 |
|------|------|------|---------|------|
| 知识包列表 | `/api/packages` | GET | 浏览可挂载知识包 | 已交付 |
| 结构化元数据 | `/api/packages/{package_id}/manifest` | GET | 浏览知识对象详情 + 说明卡 tier 分布 | 已交付 |
| 问题路由 | `/api/packages/{package_id}/route` | POST | 按需调用（非强依赖） | 已交付 |
| 分层检索 | `/api/packages/{package_id}/retrieve` | POST | 角色消费知识检索 | 已交付（检索引擎待升级） |
| 版本标识 + 健康检查 | `/api/packages/{package_id}/status` | GET | 发布快照 + 消费前检查 | 已交付 |

---

## 二、接口契约（v0.4）

### 接口 1：知识包列表

| 属性 | v0.4 契约 |
|------|----------|
| **用途** | 角色创建/编辑时浏览可挂载的知识包 |
| **调用** | `GET /api/packages` |
| **返回** | package_id, name, source_root, document_count, tier_summary, version_id, built_at |

### 接口 2：结构化元数据

| 属性 | v0.4 契约 |
|------|----------|
| **用途** | 浏览知识对象详情（含权威层级）；说明卡生成时获取 tier 分布 |
| **调用** | `GET /api/packages/{package_id}/manifest` |
| **返回** | package_id, source_root, version_id, built_at, documents[] |
| **每条文档** | doc_id, relative_path, tier(P1/P2/P3), doc_role, evidence_type, canonical_default, use_for[], not_for[], title, obsidian_url |

### 接口 3：问题路由（按需）

| 属性 | v0.4 契约 |
|------|----------|
| **用途** | 获取问题分流结果（Q0-Q6），消费方按需调用 |
| **调用** | `POST /api/packages/{package_id}/route` |
| **输入** | `{"question": "..."}` |
| **返回** | question_type, allowed_tiers[], rationale, boundary_mode |

### 接口 4：分层检索

| 属性 | v0.4 契约 |
|------|----------|
| **用途** | 角色消费时检索相关片段，返回含 tier 标注的分层命中 |
| **调用** | `POST /api/packages/{package_id}/retrieve` |
| **简化模式** | 不传 allowed_tiers，内部自动路由+检索；Q0 越界时返回拒答 payload |
| **显式模式** | 传入 allowed_tiers，直接按指定层级检索 |
| **正常返回** | route{} + hits[]（每条含 tier/doc_role/evidence_type/score/source_reference） |
| **越界拒答** | route{} + refused:true + refusal_reason + hits:[] |
| **证据不足** | route{} + refused:false + hits:[] |

### 接口 5：版本标识 + 健康检查

| 属性 | v0.4 契约 |
|------|----------|
| **用途** | 角色发布时快照 version_id；消费前确认知识平台可达 |
| **调用** | `GET /api/packages/{package_id}/status` |
| **返回** | package_id, source_root, version_id, built_at, document_count, tier_counts |
| **version_id 规则** | git commit hash 优先，manifest SHA 回退；不可变 |

---

## 三、v0.3 → v0.4 端点变更

| v0.3（Open WebUI） | v0.4（Knowledge Workbench） | 用途 |
|---|---|---|
| `GET /api/v1/knowledge/` | `GET /api/packages` | 知识库列表 |
| `GET /api/v1/knowledge/{kb_id}/files` | `GET /api/packages/{package_id}/manifest` | 知识对象清单 |
| `POST /api/v1/retrieval/query/collection` | `POST /api/packages/{package_id}/retrieve` | RAG 检索 |
| `GET /api/v1/version` | `GET /api/packages/{package_id}/status` | 版本标识 + 健康检查 |
| — | `POST /api/packages/{package_id}/route` | 问题路由（新增） |

---

## 四、不变项

以下内容从 v0.3 继承，不因接口对接点变更而改变：

| 标识 | 格式 | 来源 |
|------|------|------|
| `knowledge_object_id` | 文件路径型（相对 vault 根） | Lead 裁决（2026-05-14） |
| `knowledge_version_id` | Git commit hash | Lead 裁决（2026-05-14） |
| `knowledge_refs` 格式 | knowledge_object_id + knowledge_version_id + title + type | Lead 裁决最小结构 |
| `validated_knowledge_versions` 格式 | knowledge_object_id + knowledge_version_id | Lead 裁决最小追溯结构 |

角色产品自身数据模型（role_assets/role_versions/knowledge_refs 等表结构）不变。

---

## 五、当前状态与阻塞

| 事项 | 状态 |
|------|------|
| 公共契约裁决 | ✅ 通过 |
| Knowledge Workbench 接口交付 | ✅ 已交付，22/22 测试通过 |
| Open WebUI 适配器 | ❌ 未实现——当前 retrieve 使用确定性评分器，检索质量不足 |
| 角色产品代码切换 | 阻塞——等待 Open WebUI 适配器就绪 |
| 角色产品 dossier 回写 | ✅ 已完成（v0.5.1） |

---

## 六、回答契约结构

角色产品不遵循知识平台的五段式回答契约（formal_position/supporting_explanation/background_context/citations/boundary_notice），角色回答结构由 L4 output_schema 定义。

角色产品承诺：

- 携带 tier 标注（每条引用标注权威层级）
- source 回链（knowledge_object_id 可回链到知识平台 manifest）
- 边界声明（boundary_status 机制）

evidence_tier 标注（核心结论字段可见知识支撑层级）为后续迭代项，不在首次切换范围。

---

## 七、附录：前置文档链

| 文档 | 说明 |
|------|------|
| `role-to-knowledge-interface-need-and-gap-assessment-2026-06-17.md` | 角色产品需求与缺口评估 |
| `handoff-knowledge-to-role-interface-proposal.zh-CN.md`（v2） | 知识平台接口方案 |
| `role-to-knowledge-interface-proposal-confirmation-2026-06-17.md` | 角色产品确认与回应 |
| `handoff-knowledge-to-role-consensus-response.zh-CN.md` | 知识平台共识回应 |
| `role-to-knowledge-consensus-confirmation-2026-06-17.md` | 双边共识确认 |
| `adjudication-knowledge-interface-ownership-change-2026-06-17.md` | 裁决文档 |
| `handoff-knowledge-adjudication-supplement.zh-CN.md` | 知识平台执行计划补充 |
| `design-freeze-public-contract-interfaces.zh-CN.md` | Knowledge Workbench 接口契约冻结定义 |
| `change-delivery-public-contract-2026-06-17.zh-CN.md` | Knowledge Workbench 交付说明 |
| `role-to-knowledge-execution-risk-feedback-2026-06-17.md` | 角色产品风险反馈（Open WebUI 适配器未就绪） |
