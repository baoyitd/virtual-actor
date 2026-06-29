# v0.4.0 P0 材料二次复审修正提交 — 审核方复审转发说明

> 日期：2026-05-26
> 对象：AI 审核方
> 状态：修正完成，提交三次复审
> 前置复审文件：`docs/iterations/v0.4.0/p0-materials-rereview-2026-05-26.md`

## 1. 背景

审核方二次复审（`p0-materials-rereview-2026-05-26.md`）提出 4 个 P0 阻塞项和 2 个 P1 高风险项，结论为"仍有阻塞，暂不进入设计冻结和代码实现"。

工作方已完成全部修正。本文件逐项说明修正内容和涉及文件，供审核方三次复审。

## 2. P0 阻塞项修正

### P0-R1 DD-14 决策产品集成降级表述 → 已修正

审核方指出：`scope.md` 将 DD-14 v0.4 必交写为"角色产品侧消费能力 + 证据链就绪"、测试计划允许"终审方确认配合窗口延后则角色产品侧就绪即可"、测试用例将 I03~I05 移入 v0.4.x——与规划方"真实集成不得从 MVP 验收移出"的口径矛盾。

修正内容：

1. **scope.md DD-14 v0.4 必交**：改为"真实集成双方证据闭合；若外部配合延期则记录为外部阻塞，不得自动降级为'角色产品侧就绪'"。v0.4.x 增强列改为"无——DD-14 通过条件不可降级"。
2. **scope.md 验收标准**：新增"DD-14 真实集成双方证据闭合；真实集成证据闭合前不得声明 DD-14 通过，也不得声明 v0.4 完整通过"。
3. **scope.md 非目标与禁止动作**：新增"不得把 DD-14 从 MVP 最终验收中移出（可延后闭合但不得移出范围）"。
4. **scope.md 停止条件**：新增"DD-14 决策产品集成不得从 MVP 验收移出（可延后闭合但不得移出范围）"。
5. **traceability.md**：新增规则 5"DD-14 决策产品集成不得从 MVP 验收移出，可延后闭合但不得移出范围"。
6. **test-plan-v0.4.md 决策产品集成验证**：改为"双方证据闭合。若决策产品团队配合窗口未就绪，记录为外部阻塞，不得声明 DD-14 通过或 v0.4 完整通过"。
7. **test-plan-v0.4.md 停止条件**：新增"DD-14 决策产品集成不得从 MVP 验收移出（可延后闭合但不得移出范围）"。

涉及文件：`scope.md`、`traceability.md`、`delivery/test-plan-v0.4.md`

### P0-R2 test-consume 与 usage_record/test_validation_record 内部冲突 → 已修正

审核方指出：`test-desk-upgrade-design.md` 前文写 test-consume 不生成正式 usage_record、生成 test_validation_record，但 P0 功能清单又写"每次测试台消费自动生成一条 usage_record"、固定治理外壳检查要求 usage_record_id 非空。

修正内容：

1. **test-desk-upgrade-design.md §2.1**：已明确"test-consume 不生成正式 usage_record，生成 test_validation_record（与 test_runs 共存但字段对齐 consume API 输出结构）"。P0 功能清单中删除"每次测试台消费自动生成一条 usage_record"的矛盾表述。
2. **test-desk-upgrade-design.md 固定治理外壳检查**：将 usage_record_id 改为 validation_record_id，明确测试台响应字段使用 `validation_record_id`（而非 `usage_record_id`），避免语义污染。
3. **consume-api-design.md §6.2**：明确 test_runs 与 usage_records 的区分，测试台走 `test-consume` 内部接口，不把 test 版本纳入正式 consume API。

涉及文件：`test-desk-upgrade-design.md`、`consume-api-design.md`

### P0-R3 HTTP 错误与 system_failed 语义仍不一致 → 已修正

审核方指出：`consume-api-design.md` 仍把 role_version_id 不属于 role_id 等输入错误写成 400 同时带 system_failed；400/403/404 与固定治理外壳关系不清；500/system_failed 与 usage_record 关系矛盾。

修正内容：

1. **consume-api-design.md §7 错误处理**：完全重写，明确三层分离：
   - HTTP 200 + 6 状态（含 system_failed 已处理下游失败）→ 返回固定治理外壳 → 生成 usage_record → 计入 6 状态统计
   - HTTP 400/403/404（调用方输入/权限/状态错误）→ `{ detail }` → 不返回固定治理外壳 → 不生成 usage_record → 不计入 6 状态统计
   - HTTP 500（未捕获服务异常）→ `{ detail }` → 不承诺固定治理外壳 → 不生成 usage_record → 不计入 6 状态统计，作为"服务可用性异常"单独统计
2. **删除 400 场景中的 `status: system_failed` 表述**：role_version_id 不属于 role_id、版本不可消费、角色不可消费等均为 400/403/404，只返回 `{ detail }`，不返回固定治理外壳。
3. **test-plan-v0.4.md**：新增"consume API 错误与业务状态分离验证路径"，覆盖 4 种场景（200+6状态/200+system_failed/400~404/500）。

涉及文件：`consume-api-design.md`、`delivery/test-plan-v0.4.md`

### P0-R4 场景编号和覆盖数量仍不一致 → 已修正

审核方指出：`scope.md` 核心场景链仍用旧编号（US-17=资产市场 AI 推荐、US-18=决策产品…），与 traceability.md 和测试文档不一致。多处写"16 项设计蓝图"，但 DD-06/US-11 已移出，实际为 15 项。

修正内容：

1. **scope.md 核心场景链**：完全重写为 US-06~US-21（15 项交付项），编号与 traceability.md 和测试文档一致。DD-06/US-11 角色模板库显式标注"已移出本轮范围"。
2. **scope.md Scope In 表**：从 7 项扩展到 15 项（不含 DD-06），每项标注优先级、v0.4 必交、v0.4.x 增强。
3. **scope.md 验收标准**：改为"15 项交付项（不含已移出的 DD-06/US-11 角色模板库）"。
4. **traceability.md**：新增 US-06~US-21 全量追溯行，编号与 scope.md 和测试文档一致。
5. **test-plan-v0.4.md**：开头显式标注"15 项交付项：US-06~US-10, US-12~US-21；US-11/DD-06 角色模板库已移出本轮范围"。

涉及文件：`scope.md`、`traceability.md`、`delivery/test-plan-v0.4.md`

## 3. P1 高风险项修正

### P1-R1 legacy 分流规则未回写到 consume API 主设计文档 → 已修正

审核方指出：legacy 角色分流规则已在迁移策略和测试文档中收口，但 consume-api-design.md 主设计文档没有写入。

修正内容：

1. **consume-api-design.md §7.1 新增 v0.3 legacy 角色消费分流规则**：按 caller_type 分流：
   - 使用台 (human)：允许消费，output_type 为 null，structured_result 为空，answer 标注"需升级"
   - Dify (agent_platform)：拒绝消费，返回 HTTP 400
   - 决策产品 (decision_product)：拒绝消费，返回 HTTP 400
2. 明确写入"legacy 角色不得进入资产市场正式消费链路、Dify 消费和决策产品消费"。

涉及文件：`consume-api-design.md`

### P1-R2 Dify 官方依据仍需修正为当前可访问地址 → 已修正

审核方指出：文档继续引用 `https://docs.dify.ai/guides/tools`（本地复核 404）；HTTP Request 页面跳转到新地址。

修正内容：

1. **dify-integration-tech-evaluation.md §1**：更新所有 Dify 官方文档 URL 为当前可访问地址：
   - HTTP Request 节点：`https://docs.dify.ai/en/use-dify/nodes/http-request`
   - Tools 章节：`https://docs.dify.ai/en/use-dify/workspace/tools`
   - Plugins 章节：`https://docs.dify.ai/en/use-dify/workspace/plugins`
   - MCP Server：`https://docs.dify.ai/en/use-dify/publish/publish-mcp`
2. 对 OpenAPI、Plugin、MCP 的能力判断分别给出对应官方依据，不交叉引用。
3. MCP 部分改为更稳妥表述："v0.4 为降低集成变量，优先采用 HTTP Request/HTTP Tool；MCP 能力作为后续增强候选，不作为本轮最低证明路径"。
4. 所有引用标注访问日期 2026-05-26。

涉及文件：`dify-integration-tech-evaluation.md`

## 4. 同步回写的 dossier 文件

除上述针对性修正外，以下 dossier 文件已同步回写至当前产品共识和规划方裁决口径：

| 文件 | 回写内容 |
|---|---|
| `scope.md` | 定位升级为"企业数字角色资产运营平台"；Scope 从 7 项扩展到 15 项（含 v0.4 必交/v0.4.x 增强分界）；移除旧约束；新增场景 SC-05~10；更新验收标准和停止条件 |
| `design-delta.md` | DD-04 升级为统一消费 API 设计与实现；新增 DD-09~16；新增 applicable_scenarios/creation_source/output_type/output_schema/capability_level 字段定义；usage_records 模型升级；新增版本快照字段和迁移策略；更新风险边界和待裁决项 |
| `traceability.md` | 新增 US-06~US-21 追溯行；新增 consume API 对 DD 项支撑关系表；更新追溯使用规则（DD-14 不移出、DD-16 不降级） |

## 5. 审核方复审要点提示

本次修正聚焦于二次复审提出的 4 个 P0 + 2 个 P1，未新增功能范围。审核方需重点关注：

1. **DD-14 不降级口径的一致性**：scope.md、traceability.md、test-plan 中"不得自动降级""不得声明通过""外部阻塞"的表述是否互相一致，是否与规划方裁决口径一致。
2. **test-consume / test_validation_record 与 consume API / usage_record 的边界**：两条路径是否完全分离、无交叉污染；固定治理外壳检查中 validation_record_id 是否语义清晰。
3. **HTTP 错误与 6 状态的分离**：400/403/404 → 不返回外壳不生成 usage_record；200+system_failed → 返回外壳生成 usage_record；500 → 不返回外壳不生成 usage_record；三层是否完全自洽。
4. **US 编号一致性**：scope.md、traceability.md、test-plan、test-cases 的编号是否完全一致；是否显式标注"15 项交付项、US-11/DD-06 已移出"。
5. **legacy 分流规则回写完整性**：consume-api-design.md 是否与 version-snapshot-update-and-migration.md 分流口径一致。
6. **Dify 官方依据**：URL 是否可访问、是否标注访问日期、是否与结论对应。

## 6. 下一步

审核方三次复审通过后 → 规划方终审确认 → 设计冻结生效 → 进入代码实现。

如审核方发现仍有阻塞或矛盾，请提出复审意见，工作方将再次修订。