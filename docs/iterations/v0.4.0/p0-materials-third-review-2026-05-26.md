# v0.4.0 P0 材料三次复审意见

> 日期：2026-05-26
> 对象：工作方针对 `p0-materials-rereview-2026-05-26.md` 的修正
> 结论：P0 阻塞已清；仍有 1 个设计冻结前 P1 清理项；暂不进入代码实现

## 1. 总体结论

工作方已按二次复审意见完成关键收口。本轮复审结论：

1. 上次列出的 4 个 P0 阻塞均已实质修复。
2. 上次列出的 2 个 P1 高风险项已基本修复。
3. 当前不再存在阻止进入“文档结构治理 + 规划方终审”的 P0 问题。
4. 仍有 1 个字段名残留需要在设计冻结前修正。
5. 在规划方/终审方确认设计冻结前，仍不得进入代码实现。

## 2. 逐项复审结论

### P0-R1 DD-14 决策产品集成降级表述

结论：已修复。

核对结果：

1. `scope.md` 已明确：真实集成证据闭合前不得声明 `DD-14` 通过，也不得声明 `v0.4` 完整通过。
2. `test-plan-v0.4.md` 已明确：如决策产品配合窗口未就绪，应记录为外部阻塞，不得声明 `DD-14` 通过或 `v0.4` 完整通过。
3. `test-cases-v0.4.md` 已将 `I01~I02` 改为“角色产品侧集成准备里程碑（本地 readiness 证据）”，并明确 `I03~I05` 才是 `DD-14` 通过条件。

当前口径符合规划方要求：决策产品真实集成可以作为后置闭合事项，但不能被角色产品侧 readiness 替代。

### P0-R2 test-consume 与 usage_record/test_validation_record 边界冲突

结论：实质修复，剩余 1 个线框图字段名残留。

核对结果：

1. `test-desk-upgrade-design.md` 已明确 `test-consume` 不生成正式 `usage_record`，只生成 `test_validation_record`。
2. 测试台响应已明确使用 `validation_record_id`，避免污染 `usage_record_id` 语义。
3. `test-cases-v0.4.md` 的 A62/A64 已同步说明 `test_validation_record` 不写入 `usage_records`，不出现在 `consume-records` 查询中。

剩余清理项：

`test-desk-upgrade-design.md` 的 ASCII 线框图中仍有一处：

```text
role_version_id / usage_record_id
```

应改为：

```text
role_version_id / validation_record_id
```

该问题属于 P1 清理项，不影响 P0 方向判断，但必须在设计冻结前修正，避免前端实现按错误字段名展示。

### P0-R3 HTTP 错误与 system_failed 语义冲突

结论：已修复。

核对结果：

1. `consume-api-design.md` 已删除 `400` 场景中的 `status: system_failed` 表述。
2. 文档已明确：
   - HTTP 400/403/404：调用方输入、权限或状态错误，不返回固定治理外壳，不生成 `usage_record`，不计入 6 状态统计。
   - HTTP 200 + `status=system_failed`：已处理的下游失败，返回固定治理外壳，生成 `usage_record`，计入 6 状态统计。
   - HTTP 500：未捕获服务异常，不返回固定治理外壳，不生成 `usage_record`，不计入 6 状态统计。
3. `test-plan-v0.4.md`、`test-cases-v0.4.md`、`business-output-templates-and-status-rules.md` 已同步该口径。

该修复解决了运营统计、消费方处理和状态语义混用问题。

### P0-R4 场景编号和覆盖数量不一致

结论：已修复。

核对结果：

1. `scope.md`、`traceability.md`、`test-plan-v0.4.md`、`test-cases-v0.4.md` 已统一为：
   - `US-17 = DD-12 业务输出配置`
   - `US-18 = DD-13 资产市场 AI 推荐`
   - `US-19 = DD-14 决策产品集成`
   - `US-20 = DD-15 Dify 消费证明`
   - `US-21 = DD-16 6 状态`
2. “16 项设计蓝图”已改为“15 项交付项”，并明确 `US-11/DD-06` 角色模板库已移出本轮范围。

编号错位风险已解除。

## 3. P1 复审结论

### P1-R1 legacy 分流规则未回写 consume API 主设计

结论：已修复。

`consume-api-design.md` 已新增 `7.1 v0.3 legacy 角色消费分流规则`，明确：

1. `caller_type=human` 可降级消费。
2. `caller_type=agent_platform` 和 `caller_type=decision_product` 必须拒绝。
3. legacy 角色不得进入资产市场正式消费链路、Dify 消费和决策产品消费。

### P1-R2 Dify 官方依据 URL 需修正

结论：已基本修复。

核对结果：

1. 已移除旧的 `https://docs.dify.ai/guides/tools` 和 `https://docs.dify.ai/guides/tools/mcp` 路径。
2. 已改为当前可访问的 Dify 官方文档路径，并标注访问日期。
3. 本地 HTTP 复核结果：`http-request`、`workspace/tools`、`workspace/plugins`、`publish-mcp` 四个页面均返回 HTTP 200。
4. “v0.4 优先 HTTP，MCP 后续评估”的结论保持不变，且不再依赖“Dify MCP 不成熟”这类不稳妥表述。

该项不再阻塞。

## 4. 当前剩余问题

### P1-F1 测试台线框图字段名残留

涉及文件：

- `docs/iterations/v0.4.0/test-desk-upgrade-design.md`

问题：

ASCII 线框图仍展示：

```text
role_version_id / usage_record_id
```

但本文档其他章节和测试用例已明确测试台应展示：

```text
role_version_id / validation_record_id
```

处理要求：

设计冻结前将该线框图字段改为 `validation_record_id`。

## 5. 审核结论

当前结论：**P0 阻塞已清，可以进入文档结构治理和规划方终审；但仍不得直接进入代码实现。**

进入下一步前需完成：

1. 修复 `test-desk-upgrade-design.md` 中线框图字段名残留。
2. 按既定要求推进文档结构治理：区分 v0.4 当前真源、历史研究、已废弃旧口径、交付证据和 handoff 材料。
3. 文档结构治理完成后，再提交规划方/终审方确认是否进入设计冻结。
4. 设计冻结确认后，才允许进入代码实现。

## 6. 给终审方的简要口径

本轮工作方修复有效。上次阻塞的核心问题已经清掉：决策产品集成未再被 readiness 替代，测试台和正式消费记录边界已拆开，HTTP 错误和 6 状态语义已分离，US 编号已统一。

当前只剩一个测试台线框图字段名残留，需要在设计冻结前改掉。建议允许工作方进入“文档结构治理 + 规划方终审”阶段，但不要直接进入代码实现。
