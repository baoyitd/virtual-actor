# v0.4.0 设计冻结终审提交说明

> 日期：2026-05-26
> 对象：规划方 / 终审方
> 状态：提交终审，请求确认设计冻结
> Formal Status：Draft
> Design Freeze Status：待终审确认后生效为 Effective

## 1. 提交内容

工作方已完成以下全部前置工作，请求规划方/终审方确认设计冻结：

### 1.1 P0 材料产出与审核

| 阶段 | 结论 | 对应文件 |
|---|---|---|
| P0 材料首次提交 | 有阻塞（2 P0 + 6 P1） | `p0-materials-review-2026-05-26.md` |
| 二次复审 | 有阻塞（4 P0 + 2 P1） | `p0-materials-rereview-2026-05-26.md` |
| 修正后提交 | P0 阻塞已清，1 个 P1 清理项 | `p0-rereview-fix-forward-2026-05-26.md` |
| 三次复审 | P0 阻塞已清，P1 清理项已修复 | `p0-materials-third-review-2026-05-26.md` |
| P1 修复验证 | test-desk 线框图字段名已修正，lint:md 0 errors，iteration-guard passed | `test-desk-upgrade-design.md` §4.1 |

**审核方结论**：P0 阻塞已清，可以进入文档结构治理和规划方终审；但仍不得直接进入代码实现。

### 1.2 文档结构治理

| 产物 | 说明 | 对应文件 |
|---|---|---|
| v0.4 唯一入口索引 | 5 类文档分类（Current Source of Truth / Active Review Material / Superseded / Historical Reference / Handoff Only）、旧口径黑名单、下一步流程 | `README.md` |
| Formal Status 修正 | Design Freeze Status 与 Formal Status 分离：冻结后 Formal Status 仍保持 Draft，实现和自测完成后升级为 Self-Tested | `README.md` 当前状态表 |

**复核方结论**：文档结构治理整体通过，Design Freeze Status 表述修正后可提交规划方终审。

### 1.3 真源文件清单

以下 14 个文件构成 v0.4 当前有效真源：

| # | 文件 | 内容 | 优先级 |
|---|---|---|---|
| 1 | `scope.md` | 定位、Scope In/Out（15 项交付项）、场景推导、验收标准、停止条件 | P0 — 范围定义唯一真源 |
| 2 | `design-delta.md` | 15 项设计增量、数据与状态变化、UI 路径变化、风险边界、待裁决项 | P0 — 设计变化唯一真源 |
| 3 | `traceability.md` | US-06~US-21 追溯矩阵、consume API 支撑关系、追溯规则 | P0 — 追溯关系唯一真源 |
| 4 | `consume-api-design.md` | 统一消费 API：路径、输入输出、版本选择、6 状态、boundary_status、错误处理、legacy 分流、公共契约边界 | DD-04/09/16 实现依据 |
| 5 | `business-output-templates-and-status-rules.md` | 4 类模板字段定义、boundary_status 复合结构、6 状态联动规则、保守判定策略 | DD-11/16 实现依据 |
| 6 | `version-snapshot-update-and-migration.md` | 版本快照新增 4 字段、LAYER_MAP 更新、发布前校验、v0.3 数据迁移、legacy 分流 | 数据模型和迁移唯一真源 |
| 7 | `dd10-ai-creation-extended-spec.md` | AI 创建范围（含 output_type 推荐 + applicable_scenarios + output_schema）、保存逻辑、降级路径 | DD-10 实现依据 |
| 8 | `test-desk-upgrade-design.md` | test-consume 内部接口、test_validation_record、结构化输出验证、6 状态展示、boundary 命中分析 | DD-03 测试台实现依据 |
| 9 | `dify-integration-tech-evaluation.md` | Dify 接入方式对比、推荐 HTTP API Tool、验收证据格式 | DD-15 技术选型依据 |
| 10 | `task-flows-acceptance-and-design-freeze.md` | 7 个任务流、UI/UX 验收点、Human 检查清单、设计冻结记录、偏差管理规则 | 硬约束 3.5/3.6 验收依据 |
| 11 | `ui-ux-wireframes.md` | 5 个核心场景低保真线框图、v0.4/v0.4.x 交互分界标注 | 硬约束 3.5 交付物 |
| 12 | `delivery/test-plan-v0.4.md` | 15 项交付项测试覆盖、质量门禁、核心用户路径、legacy 验证、错误分离验证 | 测试计划唯一真源 |
| 13 | `delivery/test-cases-v0.4.md` | US-06~US-21 详细测试用例、DD-14 里程碑与通过条件、6 状态命中路径 | 测试用例唯一真源 |
| 14 | `implementation-notes.md` | 偏差记录模板（实现阶段填写） | 偏差管理使用 |

## 2. 关键口径确认（供终审方核对）

终审方需确认以下口径是否与规划方裁决一致：

| 口径 | 当前真源表述 | 规划方裁决依据 |
|---|---|---|
| 定位 | "企业数字角色资产运营平台" | `planning-response-to-worker-feedback-2026-05-26.md` §1 |
| MVP 主链路 | AI 创建 → 资产治理 → 测试发布 → 统一消费 → 运营证据 | 同上 |
| DD-04 | 统一消费 API 设计与实现（原"纯文档"已升级） | 同上 §2.2 |
| DD-10 | AI 协作创建（含 output_type 推荐 + applicable_scenarios 生成） | 同上 §3.1 |
| DD-14 | 决策产品真实集成 + 双方证据闭合；不得从 MVP 验收移出；真实集成证据闭合前不得声明 DD-14 通过或 v0.4 完整通过 | 同上 §2.1 |
| DD-16 | 6 状态固定，不降级为 4 状态；保守判定策略允许但不移除交付语义 | 同上 §3.2 |
| 公共契约边界 | consume API 是角色产品内部候选接口，不等同于冻结跨项目公共契约 | 同上 §2.2 |
| UI/UX 硬约束 | 进入实现前必须完成线框图、任务流、验收点、Human 检查清单、设计冻结记录 | 同上 §3.5~3.6 |
| Formal Status | 设计冻结后仍保持 Draft；实现和自测完成后升级为 Self-Tested | 复核方修正要求 |

## 3. 旧口径黑名单（已移除，不得引用）

| 旧口径 | 移除原因 |
|---|---|
| "消费侧 API 不改变" | 规划方裁决批准回写：新增统一消费 API |
| "AI 辅助填充不纳入" | 方向 B 升级为 AI 协作创建全流程 |
| "决策产品集成需另行立项" | 规划方裁决不降级：DD-14 不得从 MVP 验收移出 |
| "DD-04 只产出设计说明文档" | 已升级为统一消费 API 设计与实现 |
| "DD-09 只是质量看板 MVP" | 已升级为运营看板 MVP |
| "16 项设计蓝图" | 实际为 15 项交付项（US-11/DD-06 已移出） |
| "DD-16 可降级为 4 状态" | 规划方裁决不降级 |
| "DD-14 角色产品侧就绪即可" | 三次复审确认：真实集成证据闭合前不得声明通过 |

## 4. 待终审方协调项

| 项 | 说明 | 状态 |
|---|---|---|
| P0-13 决策产品协同确认 | 决策产品团队配合时间窗口、双方对接负责人、最小真实决策场景和双方证据格式 | 需终审方协调；DD-14 真实集成证据闭合前不得声明 v0.4 完整通过 |

## 5. 设计冻结请求

工作方请求规划方/终审方确认以下事项：

1. **确认 v0.4 当前真源文件清单**（14 个文件，见 §1.3）为设计冻结范围。
2. **确认 Design Freeze Status 生效为 Effective**——设计冻结生效后，工作方不得自行改变 scope.md/design-delta.md/traceability.md 及核心设计文档中已定义的范围、数据结构、验收标准或停止条件。偏差需提交偏差说明并经规划方/终审方确认。
3. **确认 Formal Status 保持 Draft**——设计冻结不升级 Formal Status；实现和自测完成后按证据升级为 Self-Tested。
4. **确认允许进入代码实现**——Design Freeze Status = Effective 后，工作方可按真源文件定义的范围和验收标准开始代码实现。

## 6. 终审决策选项

1. **批准设计冻结**：Design Freeze Status = Effective，Formal Status 保持 Draft，允许工作方进入代码实现
2. **修改后批准**：对真源文件或口径提出调整，处理后重新终审
3. **驳回**：需要重新研究或调整方向

## 7. 验证结果

| 门禁 | 结果 |
|---|---|
| lint:md | 0 errors |
| iteration-guard | passed |
| P0 阻塞 | 全清（三次复审确认） |
| P1 清理项 | 已修复（线框图字段名修正） |
| 文档结构治理 | 通过（README.md 作为唯一入口索引） |