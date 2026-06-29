# 角色产品 · 组合层同步

> 子项目：角色产品 / virtual-actor
> 版本：v0.5.1
> 日期：2026-06-26
> Formal Status：Accepted
> 本轮复核：2026-06-26

## Current Status

当前对外交付基线为 `v0.5.1`，其 `Formal Status = Accepted`，与 `delivery/release-notes.md`、`delivery/known-issues.md`、`delivery/test-results.md` 保持一致。

v0.5.1 已完成 Knowledge Workbench 公共契约切换（`/api/public/*`）、retrieve 范围过滤落地（`knowledge_object_ids`）、知识绑定全链路修复、外供包交互重设计，44 项自动化测试通过（0 warnings），端到端联调验证通过，H01-H05 人工手动冒烟全部通过并获用户正式签收。

当前已知问题仅剩 M04（鉴权为基础账号，非企业级 RBAC，属 Known Limitation），无 Blocker。

历史版本状态如下：

| 版本 | 当前定位 | 状态 |
| --- | --- | --- |
| `v0.5.1` | 当前对外交付基线 | `Accepted` |
| `v0.5.0` | 前序迭代，已被 v0.5.1 承接 | `Self-Tested`（历史中间态） |
| `v0.4.0` | 已完成自测的历史中间态 | `Self-Tested`，未升级 |
| `v0.3.0-commercial-trial` | 早期商业试用基线 | `Accepted`（已被 v0.5.1 替换为当前基线） |

当前边界：

1. `portfolio-sync.md` 顶层同步当前对外交付基线 `v0.5.1`，已通过组合层裁决的接口增量标注为已裁决。
2. 知识平台当前 `Accepted` 仅覆盖已验收的交付范围，不外推为长期冻结公共契约版本。
3. v0.4/v0.5 活跃线引入的新增能力（统一 consume API、外供包、结构化输出语义等）在 v0.5.1 已实现并通过验收；知识平台相关接口增量已通过组合层裁决，角色产品自身接口增量（consume API、外供包等）如需外部稳定依赖仍需单独上提。
4. 决策产品集成已正式暂缓至独立后续计划（见 v0.5.1 release-notes），不在当前版本验收范围内。

## Interface Delta

状态：`Partially Adjudicated`

以下接口增量已在 v0.5.1 实现、验证并通过验收：

**已通过组合层裁决（知识平台相关）：**

5. **知识平台接口归属变更**（2026-06-18 裁决通过）：角色产品对知识平台的接口对接点从 Open WebUI 切换为 Knowledge Workbench 公共契约接口（`/api/public/*`）；Open WebUI 退为知识平台内部执行适配层。v0.5.1 已完成代码切换。裁决文档：`role-knowledge-interface-adjudication-2026-06-18.md`
6. **retrieve/route 端点结构调整 + knowledge_object_ids 参数**（2026-06-23 裁决通过）：retrieve 和 route 从 package 路径下移出为独立端点；retrieve 新增 knowledge_object_ids 参数支持文档级范围过滤。v0.5.1 已完成代码适配。裁决文档：`role-knowledge-retrieve-scope-adjudication-2026-06-23.md`
7. **retrieve 执行机制共识确认**（2026-06-29 双边共识，已闭合）：retrieve 为混合检索（open_webui 向量检索为主 + deterministic 确定性评分补充 + fallback），基于 06-18 裁决 §4 owner 自主决策事项授权，无需上提组合层裁决。共识文档：`role-to-knowledge-retrieve-mechanism-consensus-confirmed-2026-06-29.md`

**角色产品自身接口增量（尚未上提裁决）：**

1. 统一 `consume API`（`POST /role-assets/{role_id}/consume`）
2. `Tool package / Skill package` 外供形态
3. `structured_result / status / boundary_status / usage_record` 的扩展消费语义
4. `L3` 数据能力与说明卡生命周期相关的新字段和读取约束

以上角色产品自身接口增量如外部项目需稳定依赖，须单独上提公共契约裁决。

这些内容当前表述为：

- 已实现并通过 v0.5.1 验收的接口能力
- 不等同于已冻结的跨项目公共契约
- 若外部项目需要稳定依赖，必须单独完成公共契约裁决

## Required Decisions / Next Actions

| 事项 | 处理 |
| --- | --- |
| 知识平台接口归属变更裁决 | ✅ 已通过（2026-06-18 裁决），v0.5.1 已完成代码切换 |
| retrieve/route 端点结构调整裁决 | ✅ 已通过（2026-06-23 裁决），v0.5.1 已完成代码适配 |
| retrieve 执行机制共识确认 | ✅ 已闭合（2026-06-29），基于 06-18 裁决 §4 owner 自主决策事项授权，无需上提组合层裁决 |
| 知识平台中文包名 404 | ✅ 已修复（知识平台 06-24 修复，角色产品 06-29 实测确认） |
| 角色产品自身接口裁决 | 统一 consume API、外供包等如需跨项目依赖，需单独上提公共契约裁决 |
| 决策产品集成 | 已暂缓至独立后续计划，启动时需另开 dossier |
| evidence_tier 标注 | 后续迭代项，需走设计变更流程（L4 output_schema 已冻结） |

停止条件：

- 若后续实现需要改动公共契约、跨项目依赖边界、版本规则或已裁决字段，必须先停止并上提。

## Acceptance Result

| 版本 | 结论 |
| --- | --- |
| `v0.5.1` | 当前 `Accepted` 基线。已完成 Knowledge Workbench 公共契约切换、retrieve 范围过滤、知识绑定全链路修复、外供包交互重设计；44 passed 0 warnings；端到端联调通过（consume 全链路 + Skill 包下载 + 外部调用）；H01-H05 人工手动冒烟全部通过并获用户正式签收。M01/M02/M05 已于 2026-06-26 收口 |
| `v0.5.0` | `Self-Tested` 历史中间态，已被 v0.5.1 承接 |
| `v0.4.0` | `Self-Tested` 历史中间态，因外部阻塞与人工验证未闭合，未进入最终对外交付基线 |
| `v0.3.0-commercial-trial` | 早期 `Accepted` 基线，已被 v0.5.1 替换 |
