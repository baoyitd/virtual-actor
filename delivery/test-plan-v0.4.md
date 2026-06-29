# v0.4.0 测试计划

版本: v0.4.0 | 日期: 2026-05-28 | 状态: Self-Tested | 验收对象: 企业数字角色资产运营平台增量

> 本文档覆盖 US-06 至 US-21（15 项交付项：US-06~US-10, US-12~US-21；US-11/DD-06 角色模板库已移出本轮范围）。复审通过后同步更新为正式版。

## 交付范围

v0.4 在 v0.3.0-commercial-trial Accepted 基线上增量交付：

1. 角色资产治理属性：category、owner、maintainer、business_domain、visibility、applicable_scenarios、creation_source（DD-01 / US-06）
2. 边界声明补齐与强化：knowledge_boundary 全链路补齐；capability_boundary 资产化展示和语义强化；capability_level A1/A2/A3 标注（DD-02 / US-07）
3. 使用台升级 + 测试台升级：使用台调用 consume API（caller_type: human）；测试台调用 test-consume 内部接口验证结构化输出、6 状态、boundary_status（DD-03 / US-08）
4. **统一消费 API**：POST /role-assets/{role_id}/consume，返回固定治理外壳 + structured_result + 6 状态 + boundary_status（DD-04 / US-09）
5. 执行能力模型定义：capability_level 进入版本快照（DD-05 / US-10）
6. 历史版本详情入口（DD-07 / US-12）
7. 详情页枚举中文映射（DD-08 / US-13）
8. 角色资产运营看板：5 维度最小形态（DD-09 / US-14）
9. AI 协作创建：含 output_type 推荐 + applicable_scenarios 生成 + output_schema 默认结构（DD-10 / US-15）
10. 业务输出 Schema：4 模板 + output_type/structured_result + 版本快照（DD-11 / US-16）
11. 业务输出配置体验：模板选择 UI + AI 推荐（DD-12 / US-17）
12. 资产市场 AI 推荐入口：业务意图→角色匹配 + 推荐理由 + 运营信号（DD-13 / US-18）
13. 决策产品集成验收：双方证据闭合（DD-14 / US-19）
14. Dify 消费证明：HTTP API Tool + 代表场景 + 验收证据（DD-15 / US-20）
15. 统一消费结果状态：6 状态 + boundary_status 联动规则（DD-16 / US-21）

## 不交付范围

1. A3 执行动作的实现。
2. RBAC / 多租户 / SaaS。
3. 基于 visibility 字段的访问控制逻辑。
4. 使用反馈评分。
5. 角色模板库。
6. 自定义字段配置 UI（v0.4.x 增强）。
7. 资产市场治理视图和接入视图（v0.4.x 增强）。
8. 消费侧 API 版本化（/v1/ 前缀）。
9. 流式输出（SSE/WebSocket）。
10. MCP/A2A 协议适配。

## 测试类型与覆盖策略

| 测试类型 | 覆盖范围 | 说明 |
|---|---|---|
| 自动化 API 测试 | US-06, US-07, US-08, US-09, US-10, US-16, US-21 | pytest 覆盖 schema/API 层面的新增字段、consume API、6 状态判定、structured_result 输出结构 |
| 程序化 UI 测试 | US-06, US-07, US-08, US-10, US-12, US-13, US-15, US-16, US-17, US-18 | 前端构建 + 页面级验证，覆盖 UI 展示和交互 |
| 人工手动冒烟 | US-06, US-07, US-08, US-09, US-15, US-16, US-17, US-18, US-21 | 高风险核心路径的人工验证 |
| Dify 消费证明 | US-20 | 在 Dify 平台配置 HTTP Tool，执行代表场景，形成双方验收证据 |
| 决策产品集成验证 | US-19 | 在决策产品真实场景中消费角色资产，双方证据闭合（需终审方协调决策产品团队配合） |
| UI/UX Human 检查 | 全部核心流程 | Human 使用习惯专项检查清单走查 |

## 质量门禁

| 门禁 | 通过标准 |
|---|---|
| 自动化 API | `venv/bin/pytest -q` 全部通过，覆盖资产治理属性、knowledge_boundary schema/API、consume API、6 状态判定、boundary_status 联动、structured_result 输出结构、capability_level、version migration |
| 前端构建 | `npm run build` 通过，新增页面和字段渲染正确 |
| 程序化 UI | 新增页面（使用台、测试台、运营看板、资产市场、AI 创建、业务输出配置）和字段展示可验证 |
| iteration guard | `python3 scripts/iteration-guard.py --repo-root . --mode release` 通过 |
| markdown lint | `npm run lint:md` 通过 |
| 人工冒烟 | 资产治理属性填写和展示、knowledge_boundary 全链路、使用台基本操作、测试台结构化输出验证、AI 创建流程、业务输出配置、资产市场 AI 推荐、6 状态展示、boundary_status 命中分析 |
| Dify 消费证明 | Dify HTTP Tool 配置成功、代表场景调用成功、双方 usage_record 与 Dify 调用日志对上、非 success 状态处理验证 |
| 决策产品集成 | 决策产品真实场景调用成功、双方证据闭合。若决策产品团队配合窗口未就绪，记录为外部阻塞，不得声明 DD-14 通过或 v0.4 完整通过 |
| UI/UX Human 检查 | 10 项 Human 使用习惯专项检查清单全部通过 |

## 核心用户路径（v0.4 新增）

1. AI 创建角色 -> AI 推荐 output_type + 生成 applicable_scenarios -> 编辑草案 -> 保存为 draft（creation_source = ai_assisted）
2. 角色编辑 -> 配置业务输出（选择 output_type -> 确认 output_schema 模板字段）-> 进入版本快照
3. 角色测试 -> 测试台消费（test-consume）-> 验证 structured_result 合规性 + 6 状态展示 + boundary_status 命中分析
4. 角色发布 -> 使用台消费（consume API，caller_type: human）-> 查看固定治理外壳 + structured_result + status + boundary_status
5. 角色发布 -> Dify HTTP Tool 调用 consume API（caller_type: agent_platform）-> 双方验收证据闭合
6. 角色发布 -> 决策产品调用 consume API（caller_type: decision_product）-> 双方验收证据闭合
7. 资产市场 -> 输入业务意图 -> AI 推荐 -> 查看推荐理由 -> 试用角色
8. 运营看板 -> 查看资产总览 / AI 草案接受率 / 消费状态分布 / boundary_blocked 比率
9. 创建角色 -> 填写资产治理属性 -> 填写 knowledge_boundary -> 填写 capability_level -> 保存 -> 详情页展示
10. 查看历史版本 -> 版本列表 -> 版本内容差异
11. 列表页 -> 按 category/owner/visibility 篩选 -> 枚举显示中文

## v0.3 legacy 角色消费验证路径

1. legacy published 角色（缺少 output_type） -> 使用台消费 -> output_type = null, structured_result = {} -> answer 中标注"该版本未配置结构化输出（需升级）"
2. legacy published 角色 -> Dify/决策产品消费 -> consume API 返回 HTTP 400，提示"该角色版本不满足 v0.4 消费标准"
3. legacy published 角色 -> 资产市场展示 -> 标注"需升级"，不提供试用和消费入口按钮

## consume API 错误与业务状态分离验证路径

1. HTTP 400/403/404 调用方输入/权限/状态错误 -> 不返回固定治理外壳 -> 不生成 usage_record -> 不计入 6 状态统计
2. HTTP 200 + 6 状态（success/boundary_blocked/insufficient_context/insufficient_knowledge/system_failed/undefined） -> 返回固定治理外壳 -> 生成 usage_record -> 计入 6 状态统计
3. HTTP 200 + status=system_failed（已处理的下游失败：LLM 超时/不可达但系统仍能返回治理外壳） -> 返回固定治理外壳 -> 生成 usage_record -> 计入 6 状态统计
4. HTTP 500（未捕获服务异常：框架崩溃/数据库连接断开等系统无法生成治理外壳的情况） -> 不返回固定治理外壳 -> 不生成 usage_record -> 不计入 6 状态统计；作为"服务可用性异常"单独统计

## 停止条件

1. 实现偏离冻结设计（关键交互、信息架构、流程顺序、验收语义），必须提交偏差说明并经规划方/终审方确认。
2. 如果统一消费 API 触发公共契约裁决要求，必须停止相关实现并上提。
3. 如果 DD-14 决策产品集成过程中发现公共契约、读写边界或版本规则问题，必须上提治理裁决。
4. 如果执行能力定义涉及工具权限或跨系统调用设计，必须先上提裁决。
5. 不得把 v0.4 任何 mock/stub/fixture 描述为真实集成证据。
6. 人工手动冒烟和 UI/UX Human 检查未完成前，Formal Status 不得升级为 User-Acceptance-Candidate 或 Accepted。
7. consume API 的 6 状态不得降级为 4 状态验收。
8. DD-14 决策产品集成不得从 MVP 验收移出（可延后闭合但不得移出范围）。

## 测试用例文档

详细测试用例见 `delivery/test-cases-v0.4.md`。

## 与 DD 项的支撑关系

| DD 项 | 测试覆盖 |
|---|---|
| DD-01 | US-06 资产治理属性 API + UI + 冒烟 |
| DD-02 | US-07 边界声明 API + UI + 冒烟 |
| DD-03 | US-08 使用台/测试台 API + UI + 冒烟 |
| DD-04 | US-09 consume API 自动化 API 测试 |
| DD-05 | US-10 capability_level API + UI |
| DD-07 | US-12 版本详情 UI |
| DD-08 | US-13 中文映射 UI |
| DD-09 | US-14 运营看板 UI + 冒烟 |
| DD-10 | US-15 AI 创建 UI + 冒烟 |
| DD-11 | US-16 业务输出 Schema API + UI + 冒烟 |
| DD-12 | US-17 业务输出配置 UI + 冒烟 |
| DD-13 | US-18 资产市场 AI 推荐 UI + 冒烟 |
| DD-14 | US-19 决策产品集成验证 |
| DD-15 | US-20 Dify 消费证明 |
| DD-16 | US-21 6 状态 + boundary_status API + 冒烟 |
