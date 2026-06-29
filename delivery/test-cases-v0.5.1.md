# v0.5.1 测试用例

> 版本：v0.5.1 | 日期：2026-06-26
> 覆盖范围：DD-25~DD-41 对应的 US-31~US-44
> 用例 ID：TC-31~TC-44
> 测试结果：见 `delivery/test-results.md`

---

## TC-31：角色消费时知识检索获取分层结果

| 属性 | 内容 |
|------|------|
| 场景 | US-31 |
| 设计项 | DD-25, DD-26 |
| 前置条件 | 知识平台运行中（localhost:3099），角色已绑定知识文档 |
| 验证点 | (1) retrieve 返回结果含 tier/doc_role/evidence_type 字段；(2) 角色回答中可区分制度级与参考级引用；(3) consume status=success |
| 验证方式 | 端到端 consume + retrieve 全量/scoped |
| 结果 | PASS — `delivery/test-results.md`：retrieve 全量 5 chunks + scoped 1 chunk + koid 字段完整 |

## TC-32：角色发布时知识版本快照

| 属性 | 内容 |
|------|------|
| 场景 | US-32 |
| 设计项 | DD-28 |
| 前置条件 | 角色已绑定知识文档，处于可发布状态 |
| 验证点 | (1) 发布时从 `/api/public/packages/{id}/status` 获取 version_id；(2) version_id 为 git commit hash；(3) 发布后版本快照记录 validated_knowledge_versions |
| 验证方式 | 发布后查询 `GET /role-versions/{id}` 确认 validated_knowledge_versions |
| 结果 | PASS — version_id=`fafecb7e4b17519c06e7dd2e65ee8865619bf3ff`，快照记录通过 |

## TC-33：说明卡生成结构化知识范围描述

| 属性 | 内容 |
|------|------|
| 场景 | US-33 |
| 设计项 | DD-27 |
| 前置条件 | 角色已绑定知识文档，文档有 tier 标注 |
| 验证点 | (1) 说明卡展示「绑定N篇P1+M篇P2」结构化描述；(2) tier 分布来自 manifest |
| 验证方式 | 代码审查 `role_service.py:1018-1022` + `briefing_service.py` tier 分布生成逻辑 |
| 结果 | PASS — 代码审查确认生成「N篇P1、M篇P2」格式 |

## TC-34：知识平台健康检查

| 属性 | 内容 |
|------|------|
| 场景 | US-34 |
| 设计项 | DD-29 |
| 前置条件 | 知识平台运行中或不可达 |
| 验证点 | (1) `GET /api/public/packages` HTTP 200 即可达；(2) 健康代理 `GET /health/knowledge-platform` 返回 `reachable`/`unreachable`；(3) 知识平台不可达时浏览/绑定/测试阻断 |
| 验证方式 | 健康检查 + 知识平台不可达阻断测试（U05） |
| 结果 | PASS — `delivery/test-results.md`：健康代理 reachable + U05 阻断测试通过 |

## TC-35：03 测试页信息架构调整

| 属性 | 内容 |
|------|------|
| 场景 | US-35 |
| 设计项 | DD-31 |
| 前置条件 | 前端构建通过 |
| 验证点 | (1) baseline-strip 改为紧凑信息栏；(2) 返回按钮移到顶部 back-link 区域；(3) 测试查询 section 在页面第一个核心位置 |
| 验证方式 | 前端构建 + 代码审查 `RoleTest.tsx` |
| 结果 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd31-test-page.png`）：返回按钮在顶部、测试查询在第一个核心位置、角色信息紧凑化、5 步导航 |

## TC-36：04 治理页信息架构调整

| 属性 | 内容 |
|------|------|
| 场景 | US-36 |
| 设计项 | DD-32 |
| 前置条件 | 前端构建通过 |
| 验证点 | (1) metric-row 改为紧凑状态栏；(2) 版本级动作提前到治理表单之后；(3) 证据概况和准备度卡片降级 |
| 验证方式 | 前端构建 + 代码审查 `RoleGovernance.tsx` |
| 结果 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd32-34-39-governance-page.png`）：紧凑状态栏、治理主路径在核心位置、发布按钮在表单之后 |

## TC-37：06 外供页信息架构调整

| 属性 | 内容 |
|------|------|
| 场景 | US-37 |
| 设计项 | DD-33 |
| 前置条件 | 前端构建通过 |
| 验证点 | (1) RoleBriefingCard 移除改为紧凑状态栏；(2) overview-card 压缩；(3) 生成按钮提前到第一个核心 section |
| 验证方式 | 前端构建 + 代码审查 `RoleExports.tsx` |
| 结果 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd33-exports-page.png`）：RoleBriefingCard 移除改为紧凑状态栏、生成按钮在第一个核心 section、刷新按钮移到顶部 |

## TC-38：治理页表单交互变更 + 配置建表

| 属性 | 内容 |
|------|------|
| 场景 | US-38 |
| 设计项 | DD-34, DD-35 |
| 前置条件 | 数据库迁移完成 |
| 验证点 | (1) Owner/Maintainer 下拉用户列表；(2) 业务域下拉；(3) 企业角色多选（按业务域过滤）；(4) 标签 chip 组件；(5) business_domains 表 + enterprise_roles 表建表 + 12 域 30 角色种子数据；(6) 配置管理 API 可用 |
| 验证方式 | pytest + 代码审查 |
| 结果 | PASS — pytest 44 passed + 代码审查确认建表+迁移+种子数据+API |

## TC-39：消费回答两次调用机制

| 属性 | 内容 |
|------|------|
| 场景 | US-39 |
| 设计项 | DD-36 |
| 前置条件 | 角色配置为结构化输出模式 |
| 验证点 | (1) 第一次 LLM 以角色立场自由回答产出完整原文；(2) 第二次 LLM 从原文中按 output_type 模板提取结构化字段（temperature=0.1）；(3) 自由输出模式仍为单次调用 |
| 验证方式 | pytest + 代码审查 `consume_service.py:439-487` |
| 结果 | PASS — pytest 44 passed + 代码审查确认两次调用机制 |

## TC-40：说明卡 source hash 移除 business_domain 和 validation_summary

| 属性 | 内容 |
|------|------|
| 场景 | US-40 |
| 设计项 | DD-37, DD-38 |
| 前置条件 | 角色有治理元数据和测试记录 |
| 验证点 | (1) source_hash payload 不含 business_domain；(2) source_hash payload 不含 validation_summary；(3) 在 04 页保存治理项不导致 02 页说明卡变 stale；(4) 新测试不导致说明卡变 stale |
| 验证方式 | pytest + 代码审查 `briefing_service.py:78-108` |
| 结果 | PASS — pytest 44 passed + 代码审查确认 payload 不含这两个字段 |

## TC-41：04 治理页操作区重构

| 属性 | 内容 |
|------|------|
| 场景 | US-41 |
| 设计项 | DD-39 |
| 前置条件 | 前端构建通过 |
| 验证点 | (1) 保存+发布合并到同一操作区；(2) 发布成功后显示 banner + 引导下一步；(3) 已发布且无变更时发布按钮禁用；(4) 归档增加确认弹窗 |
| 验证方式 | 前端构建 + 代码审查 `RoleGovernance.tsx` |
| 结果 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd32-34-39-governance-page.png`）：保存+发布合并、发布按钮禁用、归档有"此操作不可逆"提示 |

## TC-42：发布前检查清单统一

| 属性 | 内容 |
|------|------|
| 场景 | US-42 |
| 设计项 | DD-39 |
| 前置条件 | 前端构建通过 |
| 验证点 | (1) 准备度卡片+证据概况合并为统一「发布前检查」清单；(2) 不再分两个重复 section |
| 验证方式 | 前端构建 + 代码审查 `RoleGovernance.tsx` |
| 结果 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd32-34-39-governance-page.png`）：统一"发布前检查"清单 10 项检查项 |

## TC-43：合并 05+06 为统一外供页

| 属性 | 内容 |
|------|------|
| 场景 | US-43 |
| 设计项 | DD-40 |
| 前置条件 | 前端构建通过 |
| 验证点 | (1) 05 页面取消，UsageDesk.tsx 已删除；(2) 消费功能合并到 06（RoleExports.tsx）；(3) 模拟调用支持全部 caller_type；(4) RoleStageNav 从 6 步改为 5 步；(5) `/use` 重定向到 `/exports` |
| 验证方式 | 前端构建 + 代码审查 |
| 结果 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd33-exports-page.png`）：5 步导航 + 生成外供包+调用方式说明+模拟调用统一在一页 + 代码审查确认 `/use` 重定向 + `UsageDesk.tsx` 已删除 |

## TC-44：retrieve 端点 + knowledge_object_ids scope 过滤

| 属性 | 内容 |
|------|------|
| 场景 | US-44 |
| 设计项 | DD-41 |
| 前置条件 | 知识平台运行中，角色已绑定知识文档 |
| 验证点 | (1) retrieve 传入 knowledge_object_ids 时只检索绑定文档；(2) 未绑定文档不参与检索（无范围泄漏）；(3) 空 knowledge_object_ids 返空；(4) 不存在 koid 返空；(5) package_id 被忽略不收窄范围 |
| 验证方式 | `delivery/test-results.md`：retrieve scoped/空/不存在/package_id 忽略 4 项验证 |
| 结果 | PASS — scoped 1 chunk 无泄漏 + 空返空 + 不存在返空 + package_id 被忽略 |
