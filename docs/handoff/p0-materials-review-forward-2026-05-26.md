# v0.4.0 工作方 P0 材料产出提交 — 审核方复审转发说明

> 日期：2026-05-26
> 对象：AI 审核方
> 状态：提交复审，待审核方确认后进入规划方终审

## 1. 背景

规划方已产出最新裁决文档 `planning-response-to-worker-feedback-2026-05-26.md`，新增 3.5 UI/UX 原型产出和 3.6 设计期强化与实现防漂移两个硬约束。终审方同步确认：v0.4 不允许"文档/API 先行、UI 后补"，进入实现前必须完成用户任务流、低保真原型、场景走查材料、UI/UX 验收点、Human 使用习惯检查清单和设计冻结记录。

工作方按最新裁决口径完成了 14 项 P0 材料中的 11 项（不含终审方协调的决策产品协同确认和尚未正式产出的测试计划/测试用例），并回写了 dossier 三份文档。

## 2. 已产出材料清单

| # | 文件路径 | 内容 | 对应规划方裁决 |
|---|---|---|---|
| 1 | `consume-api-design.md` | 统一消费 API 完整设计：路径、输入输出 schema、6 状态、boundary_status、版本选择规则、错误处理、公共契约边界 | P0-1, DD-04 升级 |
| 2 | `business-output-templates-and-status-rules.md` | DD-11 四类模板完整字段定义 + boundary_status 复合结构枚举 + 6 状态与 boundary_status 联动规则 + 6 种状态输出示例 | P0-2, P0-3, P0-4, DD-11, DD-16 |
| 3 | `version-snapshot-update-and-migration.md` | 版本快照新增 4 字段（applicable_scenarios/output_type/output_schema/capability_level）+ LAYER_MAP 更新 + 发布前校验规则 + v0.3 数据迁移策略（已 published 版本不追溯、fallback 规则） | P0-5, P0-6 |
| 4 | `test-desk-upgrade-design.md` | 测试台升级为 consume API 内部消费方：structured_result 合规校验 + 6 状态展示 + boundary 命中分析 + 固定治理外壳完整性检查 + 页面信息架构 | P0-7, DD-03 |
| 5 | `dify-integration-tech-evaluation.md` | Dify 集成技术评估：3 种接入方式对比，推荐 HTTP API Tool（最低开发量、最高稳定性），代表场景技术链路，认证方案，验收证据格式 | P0-8, DD-15 |
| 6 | `dd10-ai-creation-extended-spec.md` | DD-10 扩展规格：AI 生成范围（含 output_type 推荐 + applicable_scenarios 生成 + output_schema 默认结构）、用户可编辑范围、联动逻辑、保存逻辑、默认值与失败回退、版本快照影响 | P0-9（规划方裁决 3.1），DD-10 |
| 7 | `ui-ux-wireframes.md` | 5 个核心场景低保真交互线框图：AI 创建主流程、业务输出配置、资产市场业务发现视图、使用台/消费结果展示、运营看板。每个场景标注入口、主路径、空状态、错误状态、加载状态、不可操作状态、确认弹窗和返回路径。附 v0.4 vs v0.4.x 交互分界标注 | P0-10（规划方裁决 3.5），DD-10/12/13/03/09 |
| 8 | `task-flows-acceptance-and-design-freeze.md` | 7 个核心用户任务流（含步骤表：用户动作、系统响应、成功条件、失败条件、返回/撤销）+ UI/UX 验收点（逐场景验收标准）+ Human 使用习惯专项检查清单（10 项）+ 设计冻结记录 + 实现偏差管理规则（偏差定义、处理流程、清单格式、交付前自测要求） | P0-11/12/13（规划方裁决 3.6），终审方硬约束 |
| 9 | `scope.md`（回写） | 定位升级为"企业数字角色资产运营平台"、Scope 从 7 项扩展到 16 项（含 v0.4 必交/v0.4.x 增强分界）、移除旧约束（消费侧 API 不改变、AI 填充不纳入、决策产品另行立项）、新增场景 SC-05~10、更新验收标准和停止条件 | 规划方裁决 2.2 |
| 10 | `design-delta.md`（回写） | DD-04 升级为统一消费 API 设计与实现、新增 DD-09~16 设计增量表、新增 applicable_scenarios/creation_source/output_type/output_schema/capability_level 字段定义、usage_records 模型升级（含 caller_type/caller_id/status/boundary_status/structured_result）、新增 3.6 版本快照字段和 3.7 数据迁移策略、更新风险边界和待裁决项 | 规划方裁决 2.2, 3.1~3.6 |
| 11 | `traceability.md`（回写） | 新增 US-14~21 追溯行（DD-09~16）、新增 consume API 对 DD 项支撑关系表、更新追溯使用规则（DD-14 不移出、DD-16 不降级） | 规划方裁决 2.2 |

## 3. 关键裁决口径（已贯彻）

| 裁决项 | 口径 | 已贯彻方式 |
|---|---|---|
| DD-14 不降级 | 决策产品集成不得从 MVP 验收移出；可作为后置里程碑或 v0.4.x 子批次 | scope.md DD-14 标注"不降级"；traceability.md 规则 5；consume-api-design.md §6.1 |
| DD-16 不降级 | 6 状态固定，不接受降级为 4 状态；保守判定策略允许但不移除交付语义 | business-output-templates-and-status-rules.md 含 6 状态全量定义 + 保守判定策略 + 联动校验规则；scope.md 验收标准 7 |
| Dossier 回写 | 批准将"消费侧 API 不改变"修订为新增统一消费 API | scope.md 移除旧约束、新增 DD-04 升级；design-delta.md DD-04 升级为设计与实现；consume-api-design.md 公共契约边界 §8 |
| DD-10 扩展 | 批准 AI 创建时推荐 output_type 和 applicable_scenarios | dd10-ai-creation-extended-spec.md 含完整扩展规格 |
| UI/UX 硬约束 | 进入实现前必须完成线框图、任务流、验收点、Human 检查清单、设计冻结 | ui-ux-wireframes.md 5 场景；task-flows-acceptance-and-design-freeze.md 含全部硬约束要求 |

## 4. 审核方需重点关注

1. **consume API 与原 dossier 约束的一致性**：原 dossier 明确"消费侧 API 不改变"，现已回写升级。审核方需确认回写是否完整、是否遗漏旧约束残留。
2. **6 状态与 boundary_status 联动校验规则的可实现性**：联动规则在后端需要校验逻辑（如 success 时 boundary_status 不得为 out_of_scope），审核方需评估是否可能产生校验死锁或边界模糊场景。
3. **4 模板字段定义的业务完整性**：每个模板的必填字段是否覆盖了消费方（决策产品、Dify）的核心需求；RiskItem/ReferenceItem 等子结构是否足够。
4. **v0.3 数据迁移策略的安全性**：已 published 版本不追溯修改是否可能导致消费 API fallback 场景过多；fallback 输出（structured_result 为空）是否影响资产市场展示。
5. **UI/UX 线框图是否覆盖规划方 3.6 的全部硬约束**：每个场景是否标注了入口、主路径、空状态、错误状态、加载状态、不可操作状态、确认弹窗和返回路径；Human 检查清单是否覆盖 10 项。
6. **设计冻结范围是否清晰**：冻结项与非冻结项的边界是否明确；偏差管理流程是否可执行。
7. **公共契约边界措辞一致性**：所有文档中关于 consume API "内部候选接口、不等同于冻结跨项目公共契约"的表述是否一致。

## 5. 待终审方协调项

P0-13（决策产品协同确认）需要终审方协调：
1. 决策产品团队配合时间窗口
2. 双方对接技术负责人
3. 最小真实决策场景和双方证据格式

此项工作方无法自行完成，需终审方确认后才能推进 DD-14 真实集成验收。

## 6. 下一步

审核方复审通过后 → 规划方终审确认 → 设计冻结生效 → 进入代码实现。

审核方如发现材料缺口、规则矛盾或设计风险，请提出复审意见，工作方将修订后再提交。