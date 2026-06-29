# v0.4.0 P0 材料审核方复审意见

> 日期：2026-05-26
> 对象：`docs/handoff/p0-materials-review-forward-2026-05-26.md` 及其列出的 P0 材料
> 结论：有阻塞项，修订后再进入规划方终审和设计冻结

## 1. 总体结论

工作方已按最新规划回应补齐了多数 P0 材料，方向基本符合“企业数字角色资产运营平台”的产品共识。

但当前材料仍存在阻塞问题，不能直接进入设计冻结或代码实现：

1. 测试计划和测试用例仍是旧范围，未覆盖当前 16 项设计蓝图。
2. 统一消费 API 与测试台升级设计存在角色状态语义冲突。
3. v0.3 legacy published 角色的 fallback 规则与“可发布、可消费角色必须配置业务输出结构”的产品原则存在张力。
4. Dify 技术评估需要更新对当前 Dify 能力的事实依据，不能基于未引用事实冻结方案。

## 2. 阻塞发现

### P0-1 测试计划和测试用例未回写到最新范围

文件：

- `delivery/test-plan-v0.4.md`
- `delivery/test-cases-v0.4.md`

问题：

当前测试计划仍写明只覆盖 `US-06`、`US-07`、`US-08`、`US-09`、`US-10`、`US-12`、`US-13`，且仍把 `DD-04` 表述为“消费侧 API 设计说明文档”。测试用例中 `US-09` 仍要求“无新增或修改的 API 路径”。

这与最新版 `scope.md`、`design-delta.md`、`traceability.md` 已回写的 16 项设计蓝图直接冲突，也与规划方要求“测试计划和测试用例回写”不一致。

影响：

1. `DD-09` 至 `DD-16` 缺少正式测试覆盖。
2. 统一消费 API、Dify、决策产品、6 状态、UI/UX 硬约束均无法进入可验收状态。
3. 如果按当前测试计划进入实现，会复现 v0.3 的“交付后由终审方发现基础问题”的风险。

处理要求：

1. 回写 `delivery/test-plan-v0.4.md`，覆盖 `US-06` 至 `US-21`。
2. 回写 `delivery/test-cases-v0.4.md`，新增统一消费 API、6 状态、业务输出模板、资产市场、AI 创建、使用台/测试台、Dify、决策产品、运营看板、UI/UX 人工冒烟用例。
3. 删除旧口径“DD-04 不改变接口 / 无新增 API 路径”。

### P0-2 consume API 与测试台状态语义冲突

文件：

- `docs/iterations/v0.4.0/consume-api-design.md`
- `docs/iterations/v0.4.0/test-desk-upgrade-design.md`
- `docs/iterations/v0.4.0/design-delta.md`

问题：

`consume-api-design.md` 将 consume API 定位为三类已发布角色消费入口，并在错误处理中写明 draft/test 状态角色不可消费。`test-desk-upgrade-design.md` 又要求测试台作为 consume API 的第一个内部消费方，使用 `role_version_id` 指向 test 版本进行消费。

这导致同一个 API 的状态规则互相矛盾：

1. 对外消费语义要求只消费 published 版本。
2. 测试发布链路要求 test 版本也能走 consume API 做结构化输出、状态和边界验证。

影响：

1. “测试发布 -> 统一消费”主链路无法设计闭合。
2. 后端实现时会在 `test` 版本是否可被 consume API 消费上自行裁决，产生实现漂移。
3. usage_records 与 test_runs 边界会被打乱。

处理要求：

工作方必须在设计阶段明确以下二选一或提出等价方案：

1. consume API 增加内部测试模式，只允许测试台消费 test 版本，并明确不生成正式 usage_record 或生成带 `record_type=test_validation` 的记录。
2. 测试台继续走 test_runs 专用测试接口，但复用同一套结构化输出、6 状态、boundary_status 校验逻辑，不把 test 版本纳入正式 consume API。

无论采用哪种方案，都必须同步更新 consume API、测试台、usage_records/test_runs、测试计划和追溯矩阵。

## 3. 高风险修订项

### P1-1 legacy published 角色 fallback 规则需重新收口

文件：

- `docs/iterations/v0.4.0/version-snapshot-update-and-migration.md`
- `docs/iterations/v0.4.0/consume-api-design.md`
- `docs/iterations/v0.4.0/ui-ux-wireframes.md`

问题：

迁移策略允许 v0.3 已 published 角色继续被 consume API 消费，并以 `output_type = null`、`structured_result = {}` 形式返回 `success`。但产品共识要求可发布、可消费角色在进入资产市场、Dify 或决策产品消费前必须配置业务输出类型和结构。

影响：

1. legacy 角色可能以“不完整消费资产”形式进入正式使用链路。
2. Dify 或决策产品可能拿到 `success` 但没有结构化结果，破坏统一消费输出语义。
3. 资产市场用户会看到 published 但不符合 v0.4 标准的角色，体验和治理口径不清。

处理要求：

1. 明确 legacy published 角色是否允许进入资产市场、Dify、决策产品和正式使用台。
2. 如允许使用，应明确降级标识、禁止 Dify/决策产品消费、或返回非 success 状态。
3. 如不允许使用，应要求先升级版本并补齐 `output_type/output_schema`。

### P1-2 API 错误与业务状态混用

文件：

- `docs/iterations/v0.4.0/consume-api-design.md`

问题：

`role_version_id` 不属于 `role_id`、角色不可消费、`role_id` 不存在等请求错误被标为 `status: system_failed`。但 `system_failed` 的产品语义是 LLM、知识平台、数据库、网络、超时等系统异常，不应覆盖调用方输入错误或权限/状态错误。

影响：

1. 运营看板会把调用方错误统计为系统稳定性问题。
2. Dify 和决策产品无法区分“系统坏了”与“请求不合法”。
3. 6 状态的业务语义被污染。

处理要求：

1. 明确 HTTP 层错误是否返回固定治理外壳。
2. 如果坚持 6 状态不新增，调用方输入错误不应计入消费业务状态，应作为 HTTP 错误处理。
3. 如果需要把调用方错误纳入消费结果，需重新评估是否需要 `invalid_request` 或 `permission_denied`，并按规划规则上提。

### P1-3 Dify 技术评估需补官方依据并更新 MCP 表述

文件：

- `docs/iterations/v0.4.0/dify-integration-tech-evaluation.md`

问题：

Dify 技术评估对 HTTP Tool、OpenAPI、自定义插件、MCP 支持情况做了当前能力判断，但未引用官方依据。当前 Dify 官方文档显示其 Workflow 可通过 HTTP Request 节点连接外部 API，也支持工具/插件/MCP 相关能力；其中 MCP 工具支持 HTTP transport。该事实会影响“v0.4 不考虑 MCP”的理由表述方式。

处理要求：

1. 补充 Dify 官方文档依据。
2. 将“Dify 对 MCP 支持不够成熟”改为更稳妥表述：`v0.4 为降低集成变量，优先采用 HTTP Request/HTTP Tool；MCP 能力作为后续增强候选，不作为本轮最低证明路径`。
3. 不改变本轮推荐 HTTP 方式的结论，但要避免用过时或无依据事实支撑决策。

## 4. 可接受项

以下材料方向基本可接受，修订上述阻塞项后可进入规划方终审：

1. 4 类业务输出模板字段定义整体完整，能支撑 `decision_advice`、`risk_analysis`、`policy_explanation`、`review_findings` 的 MVP。
2. `boundary_status` 复合结构和 6 状态联动规则已形成可实现基础。
3. UI/UX 线框图覆盖了规划方要求的 5 个核心场景，且包含入口、主路径、空状态、错误状态、加载状态和返回路径。
4. 用户任务流、Human 检查清单和设计冻结规则已覆盖 v0.3 交付暴露的主要过程风险。
5. `scope.md`、`design-delta.md`、`traceability.md` 已基本回写当前产品方向。

## 5. 审核结论

当前状态：有阻塞，不能进入规划方终审和设计冻结。

工作方需先完成：

1. 回写 `delivery/test-plan-v0.4.md` 和 `delivery/test-cases-v0.4.md`。
2. 修正 consume API 与测试台对 test/published 版本的状态语义冲突。
3. 收口 legacy published 角色 fallback 与 v0.4 可消费资产标准的关系。
4. 修正 API 错误与业务状态混用问题。
5. 更新 Dify 技术评估的官方依据和 MCP 表述。

修订完成后，重新提交审核方复审。
