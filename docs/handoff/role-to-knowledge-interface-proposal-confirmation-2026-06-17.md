# 角色产品 → 知识平台 接口方案确认与回应

> 版本：v1.0 | 日期：2026-06-17
> 发起方：角色产品（Virtual Actor）
> 接收方：知识平台（Knowledge Workbench）
> 目的：针对知识平台接口方案逐项确认与回应，标注异议与优化建议，请知识平台确认后进入共识阶段
> 前置文档：`handoff-knowledge-to-role-interface-proposal.zh-CN.md`（v2，2026-06-17，知识平台发起）、`role-to-knowledge-interface-need-and-gap-assessment-2026-06-17.md`（2026-06-17，角色平台发起）

---

## 一、总体确认

知识平台方案的核心方向——角色产品对接 Knowledge Workbench 的公共契约接口，不再直接对接 Open WebUI，Open WebUI 退为 Knowledge Workbench 的内部执行适配层——角色产品认同此方向。

理由与知识平台一致：角色产品需要的是协议层输出（分层元数据、带 tier 的检索结果），不是 LLM runtime 或底层向量检索能力。当前直接调用 Open WebUI 端点是首期联调的历史实现选择，不是契约层面的绑定。接口层归位到 Knowledge Workbench 符合双方的项目目标。

---

## 二、逐项确认

### 2.1 现状确认 ✅

无异议。角色产品对对接现状的理解与知识平台的补充一致——Knowledge Workbench 当前是 alpha 阶段，角色产品调用 Open WebUI 是首期合理选择。

### 2.2 Open WebUI 定位 ✅

无异议。角色产品今后对接 Knowledge Workbench，不再直接调用 Open WebUI。

变更后的职责边界清晰：

```
角色产品 → Knowledge Workbench 公共契约接口：协议层输出（元数据、路由、检索）
角色产品 → 自身 LLM：回答合成
Knowledge Workbench 内部 → Open WebUI：执行适配层（向量检索）
```

此变更涉及公共契约变更（接口端点和语义都从 Open WebUI 转移到 Knowledge Workbench），需上提组合层裁决。

### 2.3 检索执行方案 ✅（附优化建议）

角色产品认同：Knowledge Workbench 作为唯一接口点，内部委托 Open WebUI 执行向量检索，施加 tier 过滤后返回。角色产品只对接 Knowledge Workbench，不直接接触 Open WebUI。

**优化建议：retrieve 接口支持两种调用模式**

从用户场景出发：角色消费是低延迟、高频次场景。方案中的工作流要求每次消费调两次接口（route + retrieve），增加了延迟。

建议 retrieve 接口支持两种模式：

| 模式 | 调用方式 | 适用场景 | 说明 |
|------|---------|---------|------|
| 显式模式 | 先调 route 获取 allowed_tiers，再调 retrieve 传入 allowed_tiers | 需要精确路由、消费方需要先看路由结果再决定是否检索 | 知识平台原方案 |
| 简化模式 | 直接调 retrieve，不传 allowed_tiers | 大多数角色消费场景（角色按绑定范围默认层级检索） | Knowledge Workbench 内部自动执行路由，按角色绑定知识范围检索 |

两种模式返回结果结构一致。简化模式下角色消费主路径只需一次 retrieve 调用，route 接口按需使用。

角色产品消费主路径默认使用简化模式，仅在需要精确路由时切换为显式模式。

请知识平台确认是否接受此优化。

### 2.4 核心缺口满足方案

#### 场景1 & 5：结构化元数据 ✅

无异议。`/api/packages` + `/api/packages/{package_id}/manifest` 作为角色产品获取知识库列表和结构化元数据的正式接口。多包路径参数设计预留扩展，角色产品接受。

#### 场景2：检索 + tier 信息 ✅（附上述优化建议）

接口拆分方案可接受。角色产品确认只需要 route + retrieve，不需要 ask。

route 接口角色产品按需对接，不强依赖——消费主路径用 retrieve 简化模式，仅在需要精确路由时使用 route。

#### 场景3：版本标识 ✅

无异议。`/api/packages/{package_id}/status` 加入 `version_id` 字段（git commit hash 或 manifest content SHA），作为角色发布时的知识版本快照。

#### 场景4：健康检查 ✅

无异议。`/api/packages/{package_id}/status` 可达即健康。当前无 auth，alpha 阶段角色产品可工作。后续 auth 方案需双方共同定义。

#### 场景2 次要缺口：路由分流 ✅

无异议。route 接口作为公共契约接口暴露，角色产品按需对接。

---

## 三、异议：回答契约结构

### 知识平台的提问

> 角色平台自行合成回答时，是否遵循知识平台的五段式回答契约（formal_position、supporting_explanation、background_context、citations、boundary_notice）？

### 角色产品的回应：不遵循，但携带 tier 标注和 source 回链

从项目目标推导：

角色产品的核心价值是"角色基于专属知识、按自身立场给出可靠结论"。角色的回答结构由角色自身决定——L4 输出层定义了 `output_mode`（自由文本 / 结构化）和 `output_schema`（4种结构化模板：decision_advice / risk_analysis / policy_explanation / review_findings），加上角色自身的立场、观点、决策风格。

知识平台的五段式契约是为了确保知识问答"读对、答对、引对、守边界"——这是**知识侧的保障**，不是角色侧的回答格式。

角色回答的"可靠性"来自两件事：

1. **输入侧可靠性**：检索到的知识是分层的、权威层级标注的 → 这是知识平台的职责，方案已覆盖
2. **输出侧可靠性**：角色回答体现自身立场，按 L4 定义格式输出 → 这是角色产品的职责

如果强制角色遵循知识平台的五段式结构，会产生冲突：

| 维度 | 角色结构化输出模板 | 知识平台五段式契约 |
|------|-------------------|-------------------|
| 设计意图 | 业务决策导向——帮助消费方做决策 | 知识溯源导向——确保回答有据可查 |
| 核心字段 | recommendation / key_factors / risks / references | formal_position / supporting_explanation / background_context / citations / boundary_notice |
| 格式定义者 | 角色产品的 L4 output_schema | 知识平台的回答契约 |

两者结构不同、意图不同。角色产品的结构化输出模板是角色资产的一部分，由角色定义者决定，不应被外部格式约束。

### 角色产品承诺

角色产品虽不遵循知识平台的五段式格式，但在回答中承诺携带以下信息，作为输入侧可靠性在输出侧的自然投射：

| 承诺项 | 说明 |
|--------|------|
| tier 标注 | 角色回答中引用的每条知识来源，标注其权威层级（P1 制度级 / P2 操作指南 / P3 参考资料） |
| source 回链 | 每条引用附带来源文档的 knowledge_object_id，可回链到知识平台 manifest |
| 边界声明 | 角色的 boundary_status 机制继续工作——当问题超出角色声明的知识边界时返回 boundary_blocked |

这三项不改变角色的回答结构，而是在角色自身的格式内嵌入知识溯源信息。消费方仍然知道"这条引用是 P1 制度级依据，可以回查原文"。

请知识平台确认是否接受此回应。

---

## 四、接口总表（角色产品确认版）

| 接口 | 方法 | 满足的场景 | 角色产品调用方式 | 状态 |
|------|------|-----------|-----------------|------|
| `/api/packages` | GET | 场景1：知识库列表 | 角色创建/编辑时浏览可挂载的知识包 | 新增 |
| `/api/packages/{package_id}/manifest` | GET | 场景1 & 5：结构化元数据 | 角色创建/编辑时浏览知识对象详情；说明卡生成时获取 tier/evidence_type 分布 | 改造 |
| `/api/packages/{package_id}/route` | POST | 场景2：问题路由 | 角色消费时按需调用（非强依赖） | 新增 |
| `/api/packages/{package_id}/retrieve` | POST | 场景2：带 tier 的检索 | 角色消费主路径：简化模式（不传 allowed_tiers，自动路由+检索）；按需：显式模式（先 route 再 retrieve） | 新增 |
| `/api/packages/{package_id}/status` | GET | 场景3 & 4：版本标识 + 健康检查 | 角色发布时快照 version_id；消费前健康检查 | 改造 |
| `/api/ask` | POST | 角色产品不使用 | 角色产品自行合成回答，不使用此接口 | 保留（知识平台内部自用） |

---

## 五、待共识事项

| # | 事项 | 角色产品立场 | 需知识平台回应 |
|---|------|-------------|--------------|
| 1 | retrieve 简化模式 | 建议支持，降低消费主路径延迟 | 是否接受？实现方式是什么（内部自动调 route 还是允许 retrieve 不传 allowed_tiers 时按默认层级检索）？ |
| 2 | 回答契约结构 | 角色不遵循五段式格式，但承诺携带 tier 标注、source 回链、边界声明 | 是否接受此回应？ |
| 3 | 公共契约裁决 | 接口从 Open WebUI 转移到 Knowledge Workbench 是公共契约变更 | 是否需要双方共同提交裁决？由谁发起？ |

---

## 六、说明

1. 本回应仅确认方案方向和标注异议，不自行决定接口改造的执行时机——改造须在裁决落地后进行。
2. 角色产品当前代码仍对接 Open WebUI 端点，在裁决落地和 Knowledge Workbench 接口正式就绪之前不做代码改动。
3. 角色产品的设计纲要原则（§1.1）不变：只认接口契约语义，不对知识平台内部实现做假设。
