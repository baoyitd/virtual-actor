# v0.5.1 实现偏差与关键落地说明

> 用途：记录"原预期 vs 实际实现 vs 为什么改"，避免实现和设计默默分叉

## 1. 偏差记录

| 项 | 内容 |
|---|---|
| 原预期 | Knowledge Workbench retrieve 内部委托 Open WebUI 向量检索，施加 tier 过滤后返回 |
| 实际状态 | Knowledge Workbench retrieve 已升级为混合检索（open_webui 向量检索为主 + deterministic 确定性评分补充 + fallback），Open WebUI 适配器已实现并运行 |
| 偏差原因 | 知识平台在设计冻结阶段自行决定两阶段方案（确定性评分器优先，Open WebUI 后续），未在共识过程中提出。06-23 知识平台完成 Open WebUI 适配器实现，实际已超越两阶段方案 |
| 用户影响 | 已消除——06-29 联调验证通过，语义匹配能力恢复，检索质量满足"可靠结论"目标 |
| 是否补测 | 已完成——06-29 重新联调验证检索质量通过（见 `delivery/test-results.md` 混合检索联调验证） |
| 处理状态 | 已闭合。知识平台 06-23 完成 Open WebUI 适配器实现，retrieve 为混合检索（open_webui 向量检索为主 + deterministic 确定性评分补充 + fallback）。角色产品 06-29 重新联调验证通过。06-29 双方完成 retrieve 执行机制共识确认（基于 06-18 裁决 §4 owner 自主决策事项授权，无需上提组合层裁决）。共识文档：`role-to-knowledge-retrieve-mechanism-consensus-confirmed-2026-06-29.md`。 |

## 2. 关键落地说明

1. **代码切换授权路径**：scope.md 停止条件 #1 原写"若 Open WebUI 适配器未就绪，不进行代码切换"。实际执行中，知识平台于 06-22~06-23 期间将公共契约接口（packages/manifest/status/retrieve/route）部署到运行环境（localhost:3099）并通知就绪。虽然当时 Open WebUI 向量检索适配器未实现（retrieve 使用确定性字符级评分器），但公共契约接口本身功能可用。角色产品据此启动代码切换，端到端联调验证通过（见 `delivery/test-results.md`）。知识平台 06-23 完成 Open WebUI 适配器实现，retrieve 升级为混合检索。角色产品 06-29 重新联调验证检索质量通过。06-29 双方完成 retrieve 执行机制共识确认（基于 06-18 裁决 §4 owner 自主决策事项授权，无需上提组合层裁决）。
2. **evidence_tier 不在本轮**：L4 output_schema（`output_schema_service.py` 4个结构化模板）已冻结，evidence_tier 标注需走设计变更流程，是后续迭代项。
3. **接口基线更新先行**：`role-to-knowledge-integration-proposal.md` 更新为 Knowledge Workbench 接口版本，不依赖检索引擎就绪。
4. **越界拒答处理**：retrieve 简化模式返回 `refused: true` 时，`consume_service.py` 需映射为角色的 `boundary_blocked` 状态。
