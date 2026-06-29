# v0.4.0 P0 材料二次复审意见

> 日期：2026-05-26
> 对象：工作方针对 `p0-materials-review-2026-05-26.md` 的 5 项 P0 修复
> 结论：仍有 P0 阻塞，不能进入设计冻结和代码实现

## 1. 总体结论

工作方已完成实质性回写，5 项原始阻塞中有 2 项基本收口：

1. `delivery/test-plan-v0.4.md` 和 `delivery/test-cases-v0.4.md` 已从旧范围重写到当前增量范围，原“DD-04 不改变接口 / 无新增 API 路径”的旧口径已删除。
2. legacy published 角色按 `human`、`agent_platform`、`decision_product` 分流的原则已在迁移策略和测试用例中形成。

但复审发现仍存在会直接导致实现漂移或验收口径错误的阻塞问题。本轮不能进入设计冻结，也不能进入代码实现。

## 2. P0 阻塞项

### P0-R1 DD-14 决策产品集成仍存在降级表述

涉及文件：

- `docs/iterations/v0.4.0/scope.md`
- `delivery/test-plan-v0.4.md`
- `delivery/test-cases-v0.4.md`

问题：

当前文档一方面写明 `DD-14` 不得从 MVP 验收移出，另一方面又写出如下口径：

1. `scope.md` 将 `DD-14` 的 `v0.4 必交` 写为“角色产品侧消费能力 + 证据链就绪”，把“决策产品真实集成验收”放入 `v0.4.x 增强`。
2. `delivery/test-plan-v0.4.md` 写明“如终审方确认配合窗口延后，则角色产品侧消费能力和证据链就绪即可”。
3. `delivery/test-cases-v0.4.md` 写明 `I01~I02` 可作为 `v0.4` 验收最低证明，`I03~I05` 在 `v0.4.x` 完成。

这与规划方已确认的口径不一致：决策产品真实集成可以作为后置里程碑或子批次执行，但在真实集成证据闭合前，不得声明 `DD-14` 通过，也不得声明 `v0.4` 完整通过。

影响：

1. 会把“角色产品侧准备完成”误写成“决策产品集成验收完成”。
2. 会导致工作方在没有决策产品真实场景证据时请求最终验收。
3. 会削弱 `v0.4` 作为“企业数字角色资产运营平台 MVP”的产品组合证明力。

处理要求：

1. 允许保留 `I01~I02`，但只能命名为“角色产品侧集成准备里程碑”或“本地 readiness 证据”，不得写为 `v0.4` 最低验收证明。
2. `I03~I05` 必须继续作为 `DD-14` 通过条件；若决策产品窗口未就绪，应记录为外部阻塞，不得自动降级。
3. `scope.md` 中 `DD-14` 的 `v0.4 必交` 应改为“真实集成双方证据闭合；若外部配合延期则不得声明 DD-14 通过”，而不是把真实集成放到增强项。

### P0-R2 test-consume 与 usage_record/test_validation_record 仍有内部冲突

涉及文件：

- `docs/iterations/v0.4.0/test-desk-upgrade-design.md`
- `delivery/test-cases-v0.4.md`
- `docs/iterations/v0.4.0/consume-api-design.md`

问题：

工作方已引入 `POST /role-assets/{role_id}/test-consume`，方向正确。但 `test-desk-upgrade-design.md` 内部仍存在冲突：

1. 前文写明 `test-consume` 不生成正式 `usage_record`，生成 `test_validation_record`。
2. 区分表中也写明测试台 `caller_type` 不生成正式 `usage_record`。
3. 但 P0 功能清单又写“每次测试台消费自动生成一条 usage_record”。
4. 固定治理外壳完整性检查仍要求 `usage_record_id` 非空，未说明测试台返回的是 `usage_record_id`、`test_validation_record_id`，还是统一的 `record_id`。

这会让实现阶段自行裁决数据模型和响应字段，重新引入 v0.3 暴露过的“设计未收口导致实现漂移”风险。

处理要求：

1. 明确 `test-consume` 只生成 `test_validation_record`，不写入 `usage_records`，并删除测试台生成 `usage_record` 的表述；或明确采用统一记录表并用 `record_type` 区分，但需同步修改所有文档。
2. 明确测试台响应字段：如果沿用 consume API 固定外壳中的 `usage_record_id`，必须说明该字段在测试台语境中指向 `test_validation_record_id` 的兼容含义；更建议改为测试台响应使用 `validation_record_id` 或 `record_id`，避免语义污染。
3. 同步更新 `test-cases-v0.4.md` 的 A62/A64 和 UI 线框中的测试记录展示规则。

### P0-R3 HTTP 错误与 system_failed 语义仍不一致

涉及文件：

- `docs/iterations/v0.4.0/consume-api-design.md`
- `delivery/test-plan-v0.4.md`
- `delivery/test-cases-v0.4.md`
- `docs/iterations/v0.4.0/business-output-templates-and-status-rules.md`

问题：

当前修正已经把 HTTP 400/403/404 与 6 状态分离，但 `500/system_failed` 口径仍冲突：

1. `consume-api-design.md` 版本选择规则仍把 `role_version_id` 不属于 `role_id`、版本不可消费写成 `400` 同时带 `status: system_failed`。
2. `consume-api-design.md` 错误处理又写 `400/403/404` 只返回 `{ detail }`，不返回固定治理外壳。
3. `consume-api-design.md` 写“只有 HTTP 200 的消费结果才进入 6 状态统计和 usage_record”，同时又写 `HTTP 500` 返回 `system_failed`。
4. `delivery/test-plan-v0.4.md` 和 `delivery/test-cases-v0.4.md` 要求 `HTTP 500` 返回 `system_failed + 固定治理外壳`、生成 `usage_record`、计入 6 状态统计。
5. `business-output-templates-and-status-rules.md` 的 `system_failed` 示例是固定治理外壳，但没有说明它对应 HTTP 200 的“已处理下游失败”，还是 HTTP 500 的“服务内部异常”。

处理要求：

1. 明确区分“已处理的下游失败”和“未处理的服务异常”：
   - 已处理的 LLM/知识平台超时或不可达：建议返回 HTTP 200 + `status=system_failed` + 固定治理外壳 + `usage_record`。
   - 输入错误、权限/状态错误：HTTP 400/403/404 + `{ detail }`，不返回固定治理外壳，不生成 `usage_record`。
   - 未捕获服务异常：HTTP 500 + `{ detail }`，不承诺固定治理外壳，不计入 6 状态统计。
2. 删除 `400` 场景中的 `status: system_failed` 表述。
3. 将 A109 改成“已处理下游失败返回 HTTP 200 + system_failed”，或明确 HTTP 500 不生成 `usage_record`，二者只能选一种作为一致口径。

### P0-R4 场景编号和覆盖数量仍不一致

涉及文件：

- `docs/iterations/v0.4.0/scope.md`
- `docs/iterations/v0.4.0/traceability.md`
- `delivery/test-plan-v0.4.md`
- `delivery/test-cases-v0.4.md`

问题：

`traceability.md`、`test-plan-v0.4.md`、`test-cases-v0.4.md` 已采用：

```text
US-17 = DD-12 业务输出配置
US-18 = DD-13 资产市场 AI 推荐
US-19 = DD-14 决策产品集成
US-20 = DD-15 Dify 消费证明
US-21 = DD-16 6 状态
```

但 `scope.md` 的“核心场景链”仍写成：

```text
US-17 = 资产市场 AI 推荐
US-18 = 决策产品集成
US-19 = Dify 消费证明
US-20 = 6 状态
```

同时多处写“US-06 至 US-21（16 项设计蓝图）”。由于 `DD-06/US-11` 已移出本轮范围，当前实际是 15 个交付项：`US-06~US-10`、`US-12~US-21`。

影响：

1. 终审方按 `scope.md` 验收时会与测试用例编号错位。
2. 工作方实现时可能漏掉 `DD-12/US-17` 或把 `DD-16` 错写成 `US-20`。
3. “16 项设计蓝图”会造成范围虚增或误以为 `US-11` 仍在范围内。

处理要求：

1. 统一编号为 `traceability.md` 和测试文档当前口径。
2. 把“16 项设计蓝图”改为“15 项交付项（US-06~US-10、US-12~US-21；US-11/DD-06 角色模板库已移出本轮范围）”。
3. 如坚持保留“16 项蓝图”表述，必须显式说明其中 1 项是已移出的 `DD-06/US-11`，不参与 v0.4 验收。

## 3. P1 高风险项

### P1-R1 legacy 分流规则未回写到 consume API 主设计文档

涉及文件：

- `docs/iterations/v0.4.0/consume-api-design.md`
- `docs/iterations/v0.4.0/version-snapshot-update-and-migration.md`
- `delivery/test-plan-v0.4.md`
- `delivery/test-cases-v0.4.md`

问题：

legacy published 角色分流规则已在迁移策略和测试文档中收口，但 `consume-api-design.md` 主设计文档没有写入：

1. `caller_type=human` 可 fallback。
2. `caller_type=agent_platform/decision_product` 必须拒绝。
3. legacy 角色不进入资产市场正式消费链路。

处理要求：

把 `version-snapshot-update-and-migration.md §4.4` 的规则摘要同步到 `consume-api-design.md`，否则 consume API 实现依据不完整。

### P1-R2 Dify 官方依据仍需修正为当前可访问地址

涉及文件：

- `docs/iterations/v0.4.0/dify-integration-tech-evaluation.md`

问题：

当前文档继续引用 `https://docs.dify.ai/guides/tools`，本地复核该地址返回 404；HTTP Request 页面会跳转到 `https://docs.dify.ai/en/use-dify/nodes/http-request`。MCP 引用地址也需要用当前可访问的官方页面替换，并记录访问日期。

处理要求：

1. 更新 Dify 官方文档 URL 为当前可访问地址。
2. 对 OpenAPI、Plugin、MCP 的能力判断分别给出对应官方依据，不要用 MCP 页面支撑 Plugin 开发框架。
3. 保留“v0.4 优先 HTTP，MCP 后续评估”的结论可以接受，但依据必须准确。

## 4. 可接受项

以下修复方向可以接受：

1. `DD-04` 已从纯文档升级为新增统一消费 API，且公共契约边界表述基本正确。
2. 6 状态没有再降级为 4 状态，测试用例已覆盖 `success`、`insufficient_context`、`insufficient_knowledge`、`boundary_blocked`、`system_failed`、`undefined`。
3. legacy 角色按消费方类型分流的产品原则正确。
4. Dify MVP 优先 HTTP Tool，而 MCP 作为后续候选的方向正确。
5. UI/UX Human 冒烟专项已经补入测试用例，方向符合 v0.4 强化设计期的要求。

## 5. 审核结论

当前结论：**仍有阻塞，暂不进入设计冻结和代码实现**。

工作方下一步只需聚焦修正上述 4 个 P0 和 2 个 P1，不要继续扩大功能范围。修复完成后，重新提交二次材料；审核方再判断是否可以进入“文档结构治理”和“规划方终审”。

## 6. 给终审方的简要口径

工作方本轮修复有进展，但还不能进入实现。关键问题不是功能方向，而是验收和实现边界仍有几处会导致误交付：

1. 决策产品真实集成不能被“角色产品侧准备就绪”替代。
2. 测试台 `test-consume` 不能混写正式 `usage_record`。
3. `system_failed`、HTTP 500 和 `usage_record` 的关系必须统一。
4. `scope`、`traceability`、测试计划的 US 编号必须一致。

建议要求工作方按上述问题做小范围修订，不要进入代码实现。
