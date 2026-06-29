# v0.4.0 文档结构治理索引

> 版本：v0.4.0 | 日期：2026-05-27 | Formal Status：Self-Tested
> 用途：v0.4 唯一入口索引——防止实现方误读旧口径、绕过设计冻结或用 v0.3 证据证明 v0.4

---

## 当前状态

| 维度 | 状态 |
|---|---|
| Formal Status | Self-Tested（复审退回后三轮修复 + DD-13 AI 推荐 MVP 已补齐交付（四阶段引擎） + 79 项自动化测试真实覆盖 + 真实运行态主链路验证闭合 + 质量工具链 5 条全过 + 交付证据已降实 + D-4A/D-6A/D-11A/D-11B/D-12A/D-12B/D-13A 已修复；H01-H07 和 UI/UX 10 项需人工冒烟；不得据此升级为 User-Acceptance-Candidate 或 Accepted） |
| Design Freeze Status | **Effective**（规划方终审于 2026-05-26 确认生效） |
| 是否允许代码实现 | **是**。按 README 中 Current Source of Truth 列出的真源文件推进 |
| 当前真源 | 本索引 + 下方 Current Source of Truth 列出的文件 |
| 冻结边界 | 详见下方冻结边界与执行要求 |

## 文档分类规则

| 类别 | 定义 | 读取权限 |
|---|---|---|
| **Current Source of Truth** | 当前有效的设计定义、产品范围、验收标准和数据规则。实现方必须以此为准 | 实现方必须读，且必须以此为唯一口径 |
| **Active Review Material** | 当前仍在审核流程中的材料（审核意见、转发说明、待裁决项）。不直接指导实现，但可能改变真源 | 实现方不得以此指导实现；规划方/审核方以此推进审核流程 |
| **Superseded** | 曾经是真源但已被后续版本替代的文件。内容不再有效，不得引用 | 实现方不得引用；仅作为"为什么改成现在这样"的历史解释 |
| **Historical Reference** | 研究阶段产出、讨论记录、早期复审意见。记录了决策过程但不定义当前口径 | 实现方不得以此定义功能或口径；仅作为上下文理解辅助 |
| **Handoff Only** | 跨项目/跨角色交接材料。不定义 v0.4 内部口径，仅记录外部协作或审核转发 | 实现方不得以此替代真源；仅作为外部协调参考 |

---

## Current Source of Truth（实现方必须以此为准）

以下文件构成 v0.4 当前有效真源。如文件之间存在表述差异，以本索引标注的优先级为准；如仍有冲突，上提规划方裁决。

### 1. 产品范围与定义（最高优先级）

| 文件 | 内容 | 优先级 |
|---|---|---|
| `scope.md` | 定位、Scope In/Out、场景推导、验收标准、停止条件、设计蓝图与实现批次 | P0 — 范围定义的唯一真源 |
| `design-delta.md` | 15 项设计增量、数据与状态变化、UI 路径变化、风险边界、待裁决项 | P0 — 设计变化的唯一真源 |
| `traceability.md` | US-06~US-21 追溯矩阵、consume API 对 DD 项支撑关系、追溯使用规则 | P0 — 追溯关系的唯一真源 |

### 2. 核心设计文档

| 文件 | 内容 | 说明 |
|---|---|---|
| `consume-api-design.md` | 统一消费 API：路径、输入输出、版本选择、6 状态、boundary_status、错误处理、legacy 分流、公共契约边界 | DD-04/09/16 的核心实现依据 |
| `business-output-templates-and-status-rules.md` | 4 类模板字段定义、boundary_status 复合结构枚举、6 状态联动规则、保守判定策略 | DD-11/16 的核心实现依据 |
| `version-snapshot-update-and-migration.md` | 版本快照新增 4 字段、LAYER_MAP 更新、发布前校验、v0.3 数据迁移策略、legacy 角色分流 | 数据模型和迁移的唯一真源 |
| `dd10-ai-creation-extended-spec.md` | AI 创建范围（含 output_type 推荐 + applicable_scenarios + output_schema 默认结构）、用户可编辑范围、保存逻辑、降级路径 | DD-10 的核心实现依据 |
| `test-desk-upgrade-design.md` | 测试台升级：test-consume 内部接口、test_validation_record、结构化输出验证、6 状态展示、boundary 命中分析 | DD-03 测试台部分的实现依据 |
| `dify-integration-tech-evaluation.md` | Dify 接入方式对比、推荐 HTTP API Tool、代表场景技术链路、认证方案、验收证据格式 | DD-15 的技术选型依据 |
| `task-flows-acceptance-and-design-freeze.md` | 7 个核心用户任务流、UI/UX 验收点、Human 检查清单（10 项）、设计冻结记录、偏差管理规则 | 规划方硬约束 3.5/3.6 的验收依据 |
| `ui-ux-wireframes.md` | 5 个核心场景低保真交互线框图、v0.4 vs v0.4.x 交互分界标注 | 规划方硬约束 3.5 的交付物 |

### 3. 测试与验收

| 文件 | 内容 | 说明 |
|---|---|---|
| `delivery/test-plan-v0.4.md` | 15 项交付项测试覆盖、质量门禁、核心用户路径、legacy 验证路径、consume API 错误分离验证 | 测试计划的唯一真源 |
| `delivery/test-cases-v0.4.md` | US-06~US-21 详细测试用例、DD-14 里程碑与通过条件、6 状态基本命中路径 | 测试用例的唯一真源 |
| `acceptance-review-framework.md` | 工程门槛 / 产品验收 / 价值证明三层审核框架，定义审核结论和 Formal Status 的判定方式 | 规划方 / AI 审核方 / 终审方的统一验收标尺 |

### 4. 实现管理

| 文件 | 内容 | 说明 |
|---|---|---|
| `implementation-notes.md` | 偏差记录与关键落地说明（D-1A~D-13A 共 14 条偏差 + 关键落地说明 11 项） | 设计冻结后偏差管理使用 |

---

## Active Review Material（不直接指导实现）

| 文件 | 内容 | 状态 | 备注 |
|---|---|---|---|
| `p0-materials-third-review-2026-05-26.md` | 三次复审结论：P0 阻塞已清，1 个 P1 清理项已修复，可进入文档结构治理和规划方终审 | **当前最新审核结论** | 规划方终审前必须参考此结论 |
| `mvp-requirements-consensus-2026-05-26.md` | MVP 需求共识稿（正文+附录） | 待终审确认 | 共识稿已被真源文件消化；终审确认后升级为真源或标记 Superseded |
| `planning-response-to-worker-feedback-2026-05-26.md` | 规划方对工作方反馈的裁决回应 | 已消化为真源 | 裁决口径已写入 scope.md/design-delta.md/traceability.md；终审确认后标记 Superseded |

---

## Superseded（已被替代，不得引用）

以下文件曾经是真源，但已被后续版本替代。**实现方不得引用这些文件定义功能或口径**。

| 文件 | 原用途 | 被替代原因 | 替代文件 |
|---|---|---|---|
| `proposal-user-feedback.md` | 方向 B 提案（终审反馈整合修订版） | 提案内容已被 mvp-requirements-consensus 消化，再被 scope.md/design-delta.md 等真源文件替代 | `scope.md`、`design-delta.md` |
| `p0-materials-review-2026-05-26.md` | 首次复审意见（2 P0 + 6 P1） | 首次复审问题已在二次复审前修复；二次复审发现新问题，三次复审确认全部清掉 | `p0-materials-third-review-2026-05-26.md` |
| `p0-materials-rereview-2026-05-26.md` | 二次复审意见（4 P0 + 2 P1） | 二次复审问题已在三次复审前修复；三次复审确认 P0 全清 | `p0-materials-third-review-2026-05-26.md` |
| `v0.4.0-planning-review-forward-2026-05-25.md` | 规划复审转发说明 | 结论为"规划通过，可进入实现"——这是规划方首次复审的旧结论，已被后续三轮 P0 材料审核推翻并重新裁决 | `p0-materials-third-review-2026-05-26.md` + `scope.md` |

---

## Historical Reference（决策过程记录，不定义当前口径）

以下文件记录了 v0.4 的决策过程——研究、讨论、反馈、早期复审。**实现方不得以此定义功能范围、数据结构或验收标准**。

| 文件 | 原用途 | 不引用原因 |
|---|---|---|
| `research-brief.md` | v0.3 能力复盘 + 研究框架 | 研究假设和初始问题已由 research-conclusion 收口；研究产出已被 scope.md/design-delta.md 消化 |
| `research-conclusion.md` | 研究结论（竞品分析、场景建模、定位建议） | 研究结论推导出了 v0.4 方向，但具体范围定义已由 scope.md 替代 |
| `planning-review-2026-05-25.md` | 规划方首次复审记录 | 复审结论"有差距，补齐后再进入实现"已被后续裁决和 P0 材料审核替代 |
| `proposal-strategic-review-2026-05-26.md` | 提案战略复审（方向 B 修改后批准） | 战略复审的调整建议已被 mvp-requirements-consensus 和真源文件消化 |
| `product-positioning-discussion-log-2026-05-26.md` | 产品定位讨论记录 | 讨论结论已被 mvp-requirements-consensus 消化；定位已写入 scope.md |
| `worker-feedback-2026-05-26.md` | 工作方对共识稿的反馈 | 反馈已被规划方裁决回应消化，裁决口径已写入真源文件 |
| `document-structure-governance-request-2026-05-26.md` | 文档结构治理要求 | 本 README.md 即为该要求的交付物 |

---

## Handoff Only（跨项目/跨角色交接，不替代真源）

| 文件 | 用途 | 不引用原因 |
|---|---|---|
| `docs/handoff/p0-materials-review-forward-2026-05-26.md` | P0 材料首次提交的审核转发说明 | 转发说明的结论已被后续复审推翻 |
| `docs/handoff/p0-rereview-fix-forward-2026-05-26.md` | 二次复审修正提交的审核转发说明 | 转发说明的结论已被三次复审替代 |
| `docs/handoff/proposal-forward-2026-05-26.md` | 方向 B 提案终审转发说明 | 提案已被真源文件替代 |
| `docs/handoff/ui-ux-redesign-handoff-2026-05-29.md` | UI/UX 整体重构工作包交接说明 | 面向新工作方的交接材料，不定义 v0.4 真源 |
| `docs/handoff/ui-ux-redesign-submission-gate-2026-05-29.md` | UI/UX 重构提交清单与审核门槛 | 审核和提交流程辅助材料，不替代 v0.4 真源 |
| `docs/handoff/ui-ux-current-ui-reference-2026-05-29.md` | 当前 UI 现状参考包 | 仅用于辅助理解当前运行态页面，不作为新设计基线 |
| `docs/handoff/next-llm-iteration-handoff.md` | LLM 会话接手说明 | v0.3 时期产物，v0.4 状态已大幅变化 |
| `docs/handoff/interface-1-field-confirmation.md` | 知识平台接口字段扩展确认 | 跨项目协作记录，不定义 v0.4 内部口径 |
| `docs/handoff/knowledge-platform-integration-status.md` | 知识平台当前状态同步 | 跨项目状态同步，v0.4 consume API 已重新定义集成方式 |
| `docs/handoff/quality-gate-proposal-feedback.md` | 质量闸门建议支持意见 | 跨项目协作记录 |
| `docs/handoff/role-product-real-integration-blockers-to-knowledge-platform-2026-05-21.md` | 集成阻塞项通知 | v0.3 时期产物 |
| `docs/handoff/role-product-release-clarification-request-to-knowledge-platform.md` | 发布澄清请求 | v0.3 时期产物 |
| `docs/handoff/role-to-decision-integration-proposal.md` | 决策产品集成草案 | v0.3 时期产物；v0.4 DD-14 已重新定义集成边界 |
| `docs/handoff/role-to-knowledge-integration-proposal.md` | 知识平台集成草案 | v0.3 时期产物 |
| `delivery/dossier-review-v0.4.html` | v0.4 dossier HTML 静态页面 | 交付展示格式，不含新口径 |
| `docs/设计/角色产品设计纲要.md` | v0.1 设计纲要（Phase 2） | v0.1 时期产物，已被 v0.3/v0.4 完整替代 |

---

## 已移除的旧口径（显式声明，防止误读）

以下旧口径已从真源中移除。**实现方不得在任何文件中引用这些旧口径**。

| 旧口径 | 移除原因 | 当前真源替代 |
|---|---|---|
| "消费侧 API 不改变" | 规划方裁决批准回写：新增统一消费 API | `scope.md` DD-04、"消费侧 API 不改变"旧约束已移除 |
| "AI 辅助填充不纳入" | 方向 B 升级为 AI 协作创建全流程 | `scope.md` DD-10 |
| "决策产品集成需另行立项" | 规划方裁决不降级：DD-14 不得从 MVP 验收移出 | `scope.md` DD-14 |
| "DD-04 只产出设计说明文档" | 已升级为统一消费 API 设计与实现 | `scope.md` DD-04、`consume-api-design.md` |
| "DD-09 只是质量看板 MVP" | 已升级为运营看板 MVP（含 AI 草案接受率、消费状态分布） | `scope.md` DD-09 |
| "16 项设计蓝图" | 实际为 15 项交付项（US-06~US-10, US-12~US-21；US-11/DD-06 已移出） | `scope.md` 验收标准 |
| "DD-16 可降级为 4 状态" | 规划方裁决不降级 | `scope.md` DD-16、`business-output-templates-and-status-rules.md` |
| "DD-14 角色产品侧就绪即可" | 三次复审确认：真实集成证据闭合前不得声明 DD-14 通过 | `scope.md` DD-14、`test-plan-v0.4.md` |

---

## 下一步流程

```text
规划方终审已通过（2026-05-26）→ Design Freeze Status = Effective
  ↓
当前：允许进入代码实现
  ↓
实现完成 → 自测 → Formal Status 升级为 Self-Tested（需按证据）
  ↓
终审方验收 → Formal Status 升级为 Accepted
```

## 冻结边界与执行要求（规划方终审确认）

以下边界与要求由规划方终审确认，实现阶段必须严格遵守：

1. **核心主链路固定**：`AI 创建 -> 资产治理 -> 测试发布 -> 统一消费 -> 运营证据`，不得在实现阶段弱化为"后台管理 + 局部 AI 辅助"。
2. **DD-14 不降级**：决策产品真实集成仍属于 v0.4 验收范围，只有真实集成且双方证据闭合后才能声明通过；不得降级为"角色产品侧就绪"。
3. **visibility 等治理字段不含权限控制**：仅作为治理标识与筛选属性，不得自行扩展为访问控制能力。
4. **资产市场 v0.4 交付范围**：business discovery MVP（业务发现、AI 推荐、直接试用、消费展示），不得削弱已冻结路径；治理视图和接入视图可放到 v0.4.x。
5. **consume API 不是冻结公共契约**：统一消费 API、status、boundary_status、structured_result 当前是角色产品本地候选接口/候选结构，如需形成跨项目稳定依赖必须先上提裁决。
6. **A3 不纳入本轮实现**。
7. **严禁 mock/stub/fixture 表述为 real integration**。
8. **偏差流程**：如需调整已冻结的信息架构、关键交互、流程顺序或验收语义，必须先回写 `implementation-notes.md` 并提交复核，未经确认不得自行变更。

## 实现阶段红线

以下行为在实现阶段绝对禁止：

1. 不得引用 Superseded、Historical Reference 或 Handoff Only 文件指导实现。
2. 不得用 v0.3 交付证据证明 v0.4 验收标准。
3. 不得自行改变真源文件中已定义的范围、数据结构、验收标准或停止条件。
4. 不得把 mock/stub/fixture 描述为真实集成证据。
5. 不得将 visibility 等治理字段扩展为访问控制能力。
6. 不得弱化核心主链路为"后台管理 + 局部 AI 辅助"。

## 偏差管理

实现阶段如需调整已冻结设计：

1. 回写 `implementation-notes.md`，包含：原设计、实际限制、替代方案、影响范围、验收影响。
2. 提交规划方/终审方复核。
3. 未经确认不得自行变更。
