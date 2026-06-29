# 公共契约裁决上提：知识平台接口归属变更

> 版本：v1.0 | 日期：2026-06-17
> 发起方：角色产品（Virtual Actor）+ 知识平台（Knowledge Workbench）联合上提
> 接收方：组合层 / Lead 项目
> 目的：申请公共契约裁决——角色产品对知识平台的接口归属从 Open WebUI 变更为 Knowledge Workbench
> 性质：跨项目公共契约变更
> 共识基线：`role-to-knowledge-consensus-confirmation-2026-06-17.md`（双边共识确认）

---

## 一、裁决事项

**申请裁决**：角色产品对知识平台的接口对接点，从 Open WebUI（localhost:3000）变更为 Knowledge Workbench 公共契约接口。

### 变更内容

| 维度 | 变更前（当前） | 变更后（申请裁决） |
|------|--------------|------------------|
| 对接服务 | Open WebUI（localhost:3000） | Knowledge Workbench 公共契约接口 |
| 接口端点 | Open WebUI 内部 API（`/api/v1/knowledge/`、`/api/v1/retrieval/query/collection`、`/api/v1/version`） | Knowledge Workbench 协议层接口（`/api/packages/*`） |
| Open WebUI 定位 | 作为知识平台的直接对外接口 | 退为 Knowledge Workbench 内部执行适配层 |
| 接口语义 | 扁平检索（chunks + source + score） | 协议层输出（分层 tier + doc_role + evidence_type + 路由 + 越界拒答） |

---

## 二、裁决理由（从项目目标推导）

### 2.1 角色产品的项目目标

角色产品的核心价值是"帮助企业创建、管理、运营可被调用的数字角色资产，角色基于专属知识、按自身立场给出**可靠结论**"。

"可靠结论"的关键支撑：角色必须能区分知识的权威层级——引用 P1 制度级依据与 P3 参考级材料，在回答中的权重和表述应有差异。

### 2.2 当前架构的问题

当前角色产品直接调用 Open WebUI 的底层 API：

- `/api/v1/retrieval/query/collection` 返回扁平的检索 chunks（含 chunk 内容、source、score），**不含权威层级 tier**
- `/api/v1/knowledge/{kb_id}/files` 返回文件列表（含 id/title/type/tags），**不含 tier/doc_role/evidence_type/canonical**
- 角色无法在回答中区分引用的权威程度，"可靠结论"的用户价值被削弱

### 2.3 变更后的架构价值

Knowledge Workbench 作为协议层暴露公共契约接口：

- 检索结果携带 tier/doc_role/evidence_type，角色可在回答中区分制度级与参考级
- 路由能力（Q0-Q6）提供精确的问题分流和越界拒答，替代角色产品的硬编码关键词匹配
- manifest 提供结构化元数据，角色说明卡可生成"3篇P1+5篇P2+2篇P3"的结构化知识范围描述
- Open WebUI 退为 Knowledge Workbench 的内部执行适配层，职责边界清晰

### 2.4 双边共识

角色产品与知识平台已通过四轮文档交换达成共识（见共识基线文档），核心共识：

1. 角色产品对接 Knowledge Workbench，不再直接对接 Open WebUI
2. retrieve 接口支持简化模式（含越界拒答条件）
3. 角色产品不遵循知识平台五段式格式，但结论字段本身可见知识支撑层级
4. 裁决与接口建设并行推进

---

## 三、变更影响范围

### 3.1 角色产品侧影响

| 影响项 | 说明 | 性质 |
|--------|------|------|
| `knowledge_platform.py` | 接口端点从 Open WebUI 切换到 Knowledge Workbench | 代码改动，裁决落地后执行 |
| `consume_service.py` | 检索调用与返回结构适配 | 代码改动，裁决落地后执行 |
| `output_schema_service.py` | 核心结论字段增加 evidence_tier 标注 | 设计变更，需写回 dossier 后执行 |
| 说明卡生成逻辑 | 利用 manifest tier 分布生成结构化描述 | 代码改动，裁决落地后执行 |
| 原约定基线 | `role-to-knowledge-integration-proposal.md`（v0.3，2026-05-14）的4项接口契约需更新 | 文档更新 |

### 3.2 知识平台侧影响

| 影响项 | 说明 | 性质 |
|--------|------|------|
| Knowledge Workbench 接口开发 | packages/manifest/route/retrieve/status 接口开发与测试 | 知识平台侧工作，与裁决并行 |
| Open WebUI 定位变更 | 从对外接口退为内部执行适配层 | 架构调整 |

### 3.3 不受影响的部分

| 不受影响项 | 说明 |
|------------|------|
| 角色产品自身数据模型 | role_assets/role_versions/knowledge_refs 等表结构不变 |
| 角色产品消费 API | consume API 的外部接口不变（消费方无感知） |
| 角色产品发布/归档流程 | 不受接口归属变更影响 |
| knowledge_object_id 格式 | 文件路径型 ID 不变（已由 Lead 裁决） |
| knowledge_version_id 格式 | Git commit hash 不变（已由 Lead 裁决） |

---

## 四、需要裁决确认的事项

| # | 裁决项 | 当前状态 | 申请裁决 |
|---|--------|---------|---------|
| 1 | 接口归属变更 | 角色产品直接调用 Open WebUI | 确认角色产品今后对接 Knowledge Workbench 公共契约接口，Open WebUI 退为知识平台内部执行适配层 |
| 2 | 接口契约更新 | 原约定4项接口（基于 Open WebUI 端点） | 确认更新为 Knowledge Workbench 的 packages/manifest/route/retrieve/status 接口集 |
| 3 | 裁决与建设并行节奏 | — | 确认 Knowledge Workbench 可先完成接口开发，裁决落地后角色产品切换对接点 |
| 4 | 结论层知识支撑层级 | 角色产品 L4 output_schema 已冻结 | 确认角色产品后续迭代纳入"核心结论字段 evidence_tier 标注"的设计变更 |

---

## 五、裁决落地后的双方执行计划

### 5.1 角色产品侧执行步骤（裁决落地后启动，不提前）

| 步骤 | 内容 |
|------|------|
| 1 | 写回 dossier：将接口变更写入活跃版本 design-delta.md / scope.md / traceability.md |
| 2 | 更新接口基线：`role-to-knowledge-integration-proposal.md` 更新为 Knowledge Workbench 接口版本 |
| 3 | 代码切换（首次切换范围）：`knowledge_platform.py` / `consume_service.py` / 说明卡逻辑 |
| 4 | 联调验证：与 Knowledge Workbench 接口联调，确认运行态闭环 |
| 5 | 质量门禁：pytest / frontend build / markdownlint / Vale / iteration-guard 全链路通过 |

### 5.2 知识平台侧执行步骤（与裁决并行启动）

| 步骤 | 内容 | 依赖 | 预计节奏 |
|------|------|------|---------|
| 1 | 设计冻结：公共契约接口的接口契约、数据结构、路由与检索拆分逻辑冻结 | 无 | 裁决提交后启动 |
| 2 | 接口开发：packages/manifest/route/retrieve/status 接口实现 | 步骤1 | 设计冻结后启动 |
| 3 | Open WebUI 适配层：retrieve 接口内部委托 Open WebUI 向量检索 + tier 过滤的实现与测试 | 步骤2 + Open WebUI 可达 | 接口骨架完成后启动 |
| 4 | 内部测试：pytest + 评测场景 + 简化模式越界拒答验证 | 步骤2 + 3 | 接口开发完成后 |
| 5 | 可联调通知：通知角色平台接口就绪，提供联调环境与接口文档 | 步骤4 + 裁决落地 | 内部测试通过且裁决落地后 |

知识平台侧步骤1-4不依赖裁决落地，可与裁决并行推进。步骤5以裁决落地为触发点。

### 5.3 首次切换范围与后续迭代范围

**首次切换范围（裁决落地后）**：

| 范围 | 内容 |
|------|------|
| 角色产品侧 | 接口对接点变更（从 Open WebUI 到 Knowledge Workbench），含 knowledge_platform.py / consume_service.py / 说明卡逻辑 |
| 知识平台侧 | 公共契约接口就绪，可联调 |
| 价值交付 | 检索结果含 tier/doc_role/evidence_type；路由与越界拒答；说明卡结构化知识范围描述 |

**后续迭代范围（evidence_tier，不阻断首次切换）**：

| 范围 | 内容 | 节奏 |
|------|------|------|
| 角色产品 L4 output_schema | 核心结论字段（recommendation/key_factors/risks 等）增加 evidence_tier 标注 | 写回 dossier → 裁决追踪 → 纳入迭代 → 二次联调 |

evidence_tier 标注作为共识承诺纳入裁决追踪项，但因角色产品 L4 output_schema 已冻结，需走设计变更流程，是后续迭代项，不阻断首次切换。

---

## 六、附件

| 附件 | 说明 |
|------|------|
| `role-to-knowledge-interface-need-and-gap-assessment-2026-06-17.md` | 角色产品接口需求与缺口评估 |
| `handoff-knowledge-to-role-interface-proposal.zh-CN.md`（v2） | 知识平台接口方案 |
| `role-to-knowledge-interface-proposal-confirmation-2026-06-17.md` | 角色产品确认与回应 |
| `handoff-knowledge-to-role-consensus-response.zh-CN.md` | 知识平台共识回应 |
| `role-to-knowledge-consensus-confirmation-2026-06-17.md` | 双边共识确认基线 |
| `handoff-knowledge-adjudication-supplement.zh-CN.md` | 知识平台侧执行计划补充与共识补签 |
