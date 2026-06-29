# v0.5.1 追溯矩阵

> 目的：把场景、设计、实现、测试与交付串起来
> 最后更新：2026-06-26（独立复审 B-2 修复，回更全部证据和发布口径）

| 场景 ID | 设计项 | 主要实现 | 用例 / 场景链 | 结果证据 | 发布口径 |
|---|---|---|---|---|---|
| US-31 | DD-25, DD-26 | `knowledge_platform.py` retrieve 对接 + `consume_service.py` 结构适配 | TC-31 | PASS — `delivery/test-results.md`：retrieve 全量 5 chunks + scoped 1 chunk + koid 字段完整 + tier/doc_role/evidence_type 映射 | 已通过 |
| US-32 | DD-28 | `role_service.py` 发布版本快照适配 | TC-32 | PASS — `delivery/test-results.md`：知识平台版本快照 version_id=`fafecb7e4b17519c06e7dd2e65ee8865619bf3ff`，发布时快照记录 | 已通过 |
| US-33 | DD-27 | `briefing_service.py` 说明卡 tier 分布 | TC-33 | PASS — 代码审查确认 `role_service.py:1018-1022` 生成「N篇P1、M篇P2」格式；`briefing_service.py` source_hash 不含 business_domain/validation_summary | 已通过 |
| US-34 | DD-29 | `knowledge_platform.py` health() 适配 | TC-34 | PASS — `delivery/test-results.md`：`GET /api/public/packages` HTTP 200 即可达；健康代理 `GET /health/knowledge-platform` 返回 `reachable` | 已通过 |
| US-35 | DD-31 | `RoleTest.tsx` 测试查询为核心，角色信息紧凑化 | TC-35 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd31-test-page.png`）：返回按钮在顶部 back-link、测试查询 section 在第一个核心位置、角色信息紧凑信息栏、5 步导航 | 已通过 |
| US-36 | DD-32 | `RoleGovernance.tsx` 发布动作提前，信息概况降级 | TC-36 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd32-34-39-governance-page.png`）：紧凑状态栏替代 metric-row、治理主路径 section 在核心位置、发布前检查+保存发布按钮在表单之后 | 已通过 |
| US-37 | DD-33 | `RoleExports.tsx` 生成按钮提前，说明卡紧凑化 | TC-37 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd33-exports-page.png`）：RoleBriefingCard 移除改为紧凑状态栏、生成按钮在第一个核心 section、刷新按钮移到顶部 back-link 区域 | 已通过 |
| US-38 | DD-34, DD-35 | `RoleGovernance.tsx` 表单交互 + 配置API + 建表 | TC-38 | PASS — pytest 44 passed + UI 级验证（`tmp/ui-dd32-34-39-governance-page.png`）：Owner/Maintainer 下拉用户列表、业务域下拉（12 域）、企业角色多选（按业务域过滤）、标签 chip 组件（输入+回车添加+×删除）+ 代码审查确认建表+迁移+种子数据+API | 已通过 |
| US-39 | DD-36 | `consume_service.py` 两次调用机制 | TC-39 | PASS — pytest 44 passed；代码审查确认第一次自由回答 + 第二次结构化提取（temp=0.1） | 已通过 |
| US-40 | DD-37, DD-38 | `briefing_service.py` source hash 移除 business_domain + validation_summary | TC-40 | PASS — pytest 44 passed；代码审查确认 payload 不含 business_domain/validation_summary | 已通过 |
| US-41 | DD-39 | `RoleGovernance.tsx` 操作区合并+发布反馈+归档确认 | TC-41 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd32-34-39-governance-page.png`）：保存+发布合并同一操作区（"仅保存"+"保存并发布"）、发布按钮禁用（有未满足检查项）、归档区域有"此操作不可逆"提示 | 已通过 |
| US-42 | DD-39 | `RoleGovernance.tsx` 发布前检查清单统一 | TC-42 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd32-34-39-governance-page.png`）：统一"发布前检查"清单（10 项检查项），不再分准备度卡片和证据概况两个重复 section | 已通过 |
| US-43 | DD-40 | `RoleExports.tsx` 合并05+06，`UsageDesk.tsx` 删除 | TC-43 | PASS — 前端构建通过 + UI 级验证（`tmp/ui-dd33-exports-page.png`）：5 步导航 + 生成外供包+调用方式说明+模拟调用统一在一页 + 代码审查确认 `/use` 重定向 + `UsageDesk.tsx` 已删除 | 已通过 |
| US-44 | DD-41 | `knowledge_platform.py` retrieve 端点+knowledge_object_ids | TC-44 | PASS — `delivery/test-results.md`：retrieve scoped 无范围泄漏 + 空 scope 返空 + 不存在 koid 返空 + package_id 被忽略 | 已通过 |

## 追溯使用规则

1. 新增高风险场景时，必须先补追溯关系，再开始实现。
2. 修复 P1 问题时，必须补对应回归用例。
3. 如果发布说明写了某项能力"已支持"，但没有实现和证据映射，不得对外表述为已完成。

## 补充说明

- US-35/36/37/38/41/42/43 的 UI 级验证证据已通过 playwright-cli 自动化浏览器验证补齐，截图保存在 `tmp/ui-dd31-test-page.png`、`tmp/ui-dd32-34-39-governance-page.png`、`tmp/ui-dd33-exports-page.png`。
- US-44 有已知偏差：retrieve 端点路径实际为 `/api/public/retrieve`，设计文档原写 `/api/retrieve`，已在 known-issues R19 记录统一为 `/api/public/*` 前缀的决策。
