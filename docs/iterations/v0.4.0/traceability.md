# v0.4.0 追溯矩阵

> 目的：把场景、设计、实现、测试与交付串起来，避免"做了很多但说不清"
> 前置文档：`research-brief.md`、`research-conclusion.md`、`mvp-requirements-consensus-2026-05-26.md`、`planning-response-to-worker-feedback-2026-05-26.md`
> Dossier 回写依据：规划方裁决批准定位升级、新增统一消费 API、DD-10 扩展、DD-16 不降级

| 场景 ID | 设计项 | 主要实现 | 用例 / 场景链 | 结果证据 | 发布口径 |
|---|---|---|---|---|---|
| US-R01 | DD-R01 | research-brief.md v0.3 能力复盘 | 研究评审 | research-conclusion.md §1 | Draft，研究产出 |
| US-R02 | DD-R01 | research-brief.md + research-conclusion.md 竞品深度分析 | 研究评审 | research-conclusion.md §2 | Draft，研究产出 |
| US-R03 | DD-R02 | research-brief.md 集团企业场景建模 | 研究评审 | research-conclusion.md §3 | Draft，研究产出 |
| US-R04 | DD-R02/DD-R03/DD-R04 | research-conclusion.md 角色资产定位与使用方式 | 研究评审 | research-conclusion.md §4-6 | Draft，研究产出 |
| US-R05 | DD-R05 | research-conclusion.md v0.4 范围决策建议 | 规划方复审 | scope.md + design-delta.md + traceability.md 更新 | Draft，待规划方确认 |
| US-06 | DD-01 | 角色资产治理属性（含 applicable_scenarios + creation_source） | SC-01, SC-03, SC-07 | design-delta.md §3.1, dd10-ai-creation-extended-spec.md | 后端 API + UI 已实现；creation_source AI 标记已修复（D-4A）；79 tests passed |
| US-07 | DD-02 | 边界声明补齐与强化：knowledge_boundary 全链路 + capability_boundary + capability_level | SC-01, SC-03 | design-delta.md §3.2, §3.4 | 后端 API + UI 已实现；79 tests passed |
| US-08 | DD-03 | 使用台升级（含 caller_type/caller_id + 测试台结构化输出验证 + 6 状态展示） | SC-01, SC-02 | consume-api-design.md §5, test-desk-upgrade-design.md | 后端 consume API 已实现；使用台 UI 基本可用但 structured_result 展示未按模板字段（P1 偏差）；79 tests passed |
| US-09 | DD-04 | **统一消费 API**：POST /role-assets/{role_id}/consume | SC-04, SC-08, SC-09, SC-10 | consume-api-design.md | 后端 API 已实现（6 状态 + boundary_status + structured_result + 版本归属校验 + output_type 覆盖）；79 tests passed |
| US-10 | DD-05 | 执行能力模型定义（capability_level 进入版本快照） | SC-01, SC-03 | design-delta.md §3.4, version-snapshot-update-and-migration.md | 后端 EAV + 版本快照已实现；capability_level 缺失拒绝已修复（D-6A）；79 tests passed |
| US-12 | DD-07 | 历史版本详情入口 | SC-03 | design-delta.md §2 | UI 已实现 |
| US-13 | DD-08 | 详情页枚举中文映射 | SC-03 | design-delta.md §2 | UI 已实现 |
| US-14 | DD-09 | 角色资产运营看板（5 维度最小形态） | SC-06 | ui-ux-wireframes.md §5 | 后端 dashboard/stats API 已实现；UI 展示 5 卡片但创建运营缺少 AI 草案接受率/人工修改率/草稿沉睡，质量运营卡片缺失（P2 偏差）；79 tests passed |
| US-15 | DD-10 | AI 协作创建（含 output_type 推荐 + applicable_scenarios 生成） | SC-07 | dd10-ai-creation-extended-spec.md, ui-ux-wireframes.md §1 | 后端 AI draft API 已实现；前端 AI 草案回填表单但缺少确认弹窗/AI 字段标记/保存成功页（P1 偏差）；79 tests passed |
| US-16 | DD-11 | 业务输出 Schema（4 模板 + output_type/structured_result + 版本快照） | SC-07, SC-10 | business-output-templates-and-status-rules.md §1 | 后端 output_schema 服务 + 4 模板已实现；79 tests passed |
| US-17 | DD-12 | 业务输出配置体验（模板选择 + AI 推荐） | SC-07 | ui-ux-wireframes.md §2 | 后端 output-templates API + AI 推荐 output_type 已实现；前端为下拉框而非模板卡片 + JSON textarea 而非字段列表 + 无保存确认弹窗（P1 偏差） |
| US-18 | DD-13 | 资产市场 AI 推荐入口（四阶段引擎：准入过滤→候选召回→LLM judge→阈值过滤；4 类结果：matched/no_match/out_of_scope/service_error；推荐池准入；场景入口 + 推荐理由 + 运营信号） | SC-05 | ui-ux-wireframes.md §3 + dd13-recommend-rereview-submission-2026-05-27.md + dd13-recommend-pool-eligibility-2026-05-27.md | 已实现（79 tests passed），待浏览器验证证据补齐 |
| US-19 | DD-14 | 决策产品集成验收（双方证据闭合） | SC-08 | consume-api-design.md §6.1, mvp-requirements-consensus §7.8 | 后端 consume API 支持 caller_type=decision_product；双方证据闭合需终审方协调决策产品团队（外部阻塞） |
| US-20 | DD-15 | Dify 消费证明（HTTP API Tool + 代表场景 + 验收证据） | SC-09 | dify-integration-tech-evaluation.md | 后端 consume API 支持 caller_type=agent_platform；Dify 平台侧执行需外部配合（外部阻塞） |
| US-21 | DD-16 | 统一消费结果状态（6 状态 + boundary_status + 联动规则） | SC-10 | business-output-templates-and-status-rules.md §2-3 | 后端 6 状态 + boundary_status 已实现；前端使用台/测试台 structured_result 展示未按模板字段（P1 偏差） |

## 统一消费 API 对 DD 项的支撑关系

| DD 项 | consume API 支撑点 |
|---|---|
| DD-03 | 使用台 UI 底层调用 consume API（caller_type: human） |
| DD-11 | structured_result 和 output_type 由 consume API 输出 |
| DD-14 | 决策产品通过 consume API 消费角色（caller_type: decision_product） |
| DD-15 | Dify 通过 consume API 消费角色（caller_type: agent_platform） |
| DD-16 | 6 状态由 consume API 返回 |

## 追溯使用规则

1. 新增高风险场景时，必须先补追溯关系，再开始实现。
2. 修复 P1 问题时，必须补对应回归用例。
3. 如果发布说明写了某项能力"已支持"，但没有实现和证据映射，不得对外表述为已完成。
4. US-R01 至 US-R05 为研究阶段产出，不构成实现承诺。
5. DD-14 决策产品集成不得从 MVP 验收移出，可延后闭合但不得移出范围。
6. DD-16 不得降级为 4 状态验收。
