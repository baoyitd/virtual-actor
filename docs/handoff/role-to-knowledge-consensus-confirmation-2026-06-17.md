# 角色产品 → 知识平台 接口方案共识确认

> 版本：v1.0 | 日期：2026-06-17
> 发起方：角色产品（Virtual Actor）
> 接收方：知识平台（Knowledge Workbench）
> 目的：确认双方在3项待共识事项上达成一致，形成共识基线，作为上提裁决的依据
> 前置文档链：`role-to-knowledge-interface-need-and-gap-assessment-2026-06-17.md`（角色产品需求与缺口评估）→ `handoff-knowledge-to-role-interface-proposal.zh-CN.md`（v2，知识平台方案）→ `role-to-knowledge-interface-proposal-confirmation-2026-06-17.md`（角色产品确认与回应）→ `handoff-knowledge-to-role-consensus-response.zh-CN.md`（知识平台共识回应）

---

## 一、共识声明

经过四轮文档交换，角色产品与知识平台在以下三项事项上达成共识：

1. 接口归属变更：角色产品今后对接 Knowledge Workbench 公共契约接口，不再直接对接 Open WebUI
2. 接口拆分与能力：Knowledge Workbench 提供 packages/manifest/route/retrieve/status 接口，角色产品自行合成回答
3. 三项技术细节共识（见第二节）

双方共同确认：以上共识作为上提组合层裁决的依据，裁决落地前双方不做超出各自治理边界的代码改动。

---

## 二、三项共识事项

### 共识1：retrieve 简化模式（含越界拒答条件）

| 维度 | 共识内容 |
|------|---------|
| 接口 | `POST /api/packages/{package_id}/retrieve` |
| 显式模式 | 先调 route 获取 allowed_tiers，再调 retrieve 传入 allowed_tiers |
| 简化模式 | 直接调 retrieve，不传 allowed_tiers。Knowledge Workbench 内部先执行路由（Q0-Q6），按路由结果执行检索 |
| 越界处理 | 简化模式内部执行完整路由规则，包括 Q0 越界拒答。路由判为 Q0 时直接返回拒答 payload，不执行检索 |
| 角色产品消费主路径 | 默认使用简化模式，一次调用完成路由+检索；route 接口按需使用 |

**双方确认**：简化模式不做越界豁免，路由的边界保障职能不被削弱。

### 共识2：回答契约结构（结论可见知识支撑层级）

| 维度 | 共识内容 |
|------|---------|
| 角色产品不遵循五段式格式 | 角色回答结构由 L4 output_schema 定义（4种结构化模板），不被外部格式约束 |
| 结论可见知识支撑层级 | 核心结论字段（recommendation/key_factors/risks 等）本身需可见其知识支撑层级，而非仅在 references 区标注 tier |
| 实现方式 | 由角色产品自行决定（如 evidence_tier 标注、evidence_weight 字段等），知识平台不规定格式 |
| 角色产品承诺 | 携带 tier 标注、source 回链（knowledge_object_id）、边界声明（boundary_status） |
| 实现约束 | 触及 v0.5 已冻结的 L4 output_schema，实现需走设计变更流程（写回 dossier → 裁决落地 → 纳入迭代范围） |

**双方确认**：消费方在结论本身即可见可信度权重，不需要去 references 里翻找。

### 共识3：裁决与接口建设并行推进

| 维度 | 共识内容 |
|------|---------|
| 并行原则 | 裁决解决契约归属问题，接口建设解决能力问题，两者不互相阻塞 |
| 节奏 | (1) Knowledge Workbench 先完成公共契约接口开发与内部测试；(2) 双方共同提交裁决；(3) 裁决落地后角色产品切换对接点，并行联调 |
| 角色产品约束 | 裁决落地前角色产品不改代码，不承担联调义务 |
| 知识平台约束 | 接口开发属于知识平台侧工作，角色产品不承担开发义务 |

**双方确认**：并行期间双方各自推进不阻塞对方，切换时机以裁决落地为触发点。

---

## 三、共识接口总表

| 接口 | 方法 | 满足场景 | 角色产品调用方式 | 状态 |
|------|------|---------|-----------------|------|
| `/api/packages` | GET | 场景1：知识库列表 | 角色创建/编辑时浏览可挂载的知识包 | 知识平台新增中 |
| `/api/packages/{package_id}/manifest` | GET | 场景1 & 5：结构化元数据 | 角色创建/编辑时浏览详情；说明卡生成时获取 tier 分布 | 改造中 |
| `/api/packages/{package_id}/route` | POST | 场景2：问题路由 | 角色消费时按需调用（非强依赖） | 新增中 |
| `/api/packages/{package_id}/retrieve` | POST | 场景2：带 tier 的检索 | 简化模式（默认）或显式模式（按需） | 新增中 |
| `/api/packages/{package_id}/status` | GET | 场景3 & 4：版本标识 + 健康检查 | 角色发布时快照 version_id；消费前健康检查 | 改造中 |
| `/api/ask` | POST | 角色产品不使用 | 角色产品自行合成回答 | 知识平台内部自用 |

---

## 四、角色产品侧影响评估

本次共识落地后，角色产品需要进行的代码改动（均在裁决落地后执行）：

| 改动项 | 说明 | 依赖 |
|--------|------|------|
| `knowledge_platform.py` 接口切换 | 从 Open WebUI 端点切换到 Knowledge Workbench 端点 | 裁决落地 + Knowledge Workbench 接口就绪 |
| `consume_service.py` 检索调用调整 | retrieve 返回结构变化（新增 tier/doc_role/evidence_type） | 同上 |
| `output_schema_service.py` 结论层知识支撑层级 | 核心结论字段增加 evidence_tier 标注 | 同上 + 设计变更写回 dossier |
| 说明卡生成逻辑 | 利用 manifest 的 tier 分布生成结构化知识范围描述 | 同上 |

---

## 五、下一步

1. 本文档作为共识基线，双方各自留存
2. 双方共同提交组合层裁决（接口归属变更）
3. Knowledge Workbench 并行推进接口开发
4. 裁决落地后角色产品启动代码切换（写回 dossier → 实现 → 联调）
