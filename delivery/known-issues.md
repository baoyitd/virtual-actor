# 已知问题清单

版本: v0.3.0-commercial-trial | 日期: 2026-05-22

| # | 问题 | 严重程度 | 影响范围 | 阻塞验收 | 绕行方式 | 后续计划 |
|---|------|---------|---------|---------|---------|---------|
| M01 | React 角色详情页直接显示内部枚举值 `balanced`、`delegatable`，不是中文业务文案 | Major | 中文商务体验与信息可读性 | 否 | 结合表单默认值和字段说明理解 | 补充详情页中文映射，避免最终用户看到内部枚举 |
| M02 | 已发布角色在编辑生成新草稿后，React UI 仅在版本时间线中保留旧发布版本摘要，未提供独立历史版本详情入口；完整版本详情当前仍需 API `/role-versions/{id}` | Major | 历史版本复核与追溯效率 | 否 | 通过 `GET /role-versions/{id}` 查询已发布版本详情 | 下一轮补独立历史版本详情入口或版本详情弹层 |
| M03 | Open WebUI Token 仍可能过期 | Major | 知识平台接口调用 | 否 | 配置 `KNOWLEDGE_AUTH_EMAIL` 和 `KNOWLEDGE_AUTH_PASSWORD` 触发自动刷新 | 商业试用环境必须配置刷新凭据或制定换 token 流程 |
| M04 | 鉴权为内部商业试用基础账号，不是企业级 RBAC | Known Limitation | 用户权限精细化 | 否 | 使用强密码和 `AUTH_SECRET`，限制内网访问 | 公测或企业部署前补账号体系 / RBAC |
| M05 | Pydantic V2 `class Config` 弃用警告仍存在 | Minor | 测试日志 | 否 | 不影响运行 | 后续统一迁移到 `ConfigDict` |

## 已关闭事项

| # | 事项 | 关闭依据 |
|---|------|----------|
| R01 | prototype 作为最终用户入口 | FastAPI 根路径已改为托管 `frontend/dist`，`prototype/` 仅保留为迁移参考 |
| R02 | 无基础鉴权 | 已新增 `/auth/login`、`/auth/logout`、`/auth/me`，业务 API 默认要求登录 |
| R03 | 发布版本可被覆写 | 编辑已发布角色会派生新草稿版本，原发布版本仍可查询 |
| R04 | 发布缺少知识版本追溯 | 发布时保存 `validated_knowledge_versions` 最小结构 |
| R05 | 测试可绕过知识绑定 | 未绑定知识时测试返回 400，避免伪通过 |
| R06 | 文件级绑定与检索范围语义不清 | 知识平台已明确按方案 A 执行：绑定用于展示/追溯，检索仍按 collection 级调用 |
| R07 | `knowledge_object_id` 真源字段不清 | 知识平台已明确正式消费字段统一为顶层 `knowledge_object_id` |
| R08 | 健康检查与鉴权口径不清 | 知识平台已明确上线验收主判据为 `http://localhost:3099/api/health`，推荐邮箱密码换 Bearer token |
| R09 | 知识平台验收账号与版本快照接口运行态异常 | 已修复，真实登录与版本快照均已通过 |
| R10 | 写接口读后即查旧状态 | 已修复，写接口返回前显式提交事务，UI 创建/绑定/测试/发布链均通过 |
| R11 | Docker Compose 启动后应用未执行迁移，登录后首个受保护接口报表不存在 | 已修复；验收栈 `/role-assets` 可正常访问 |
| R12 | Alembic 迁移仍读取 `localhost`，容器内无法连到 MySQL | 已修复；迁移环境改为读取运行时 `settings.database_url` |
| R13 | Docker Compose 空环境部署验收未完成 | 已补齐；隔离栈 `virtualactor_acceptance` 已通过主路径验证 |
| R14 | 知识平台不可达时，知识绑定接口可被手工 `knowledge_version_id` 绕过 | 已修复；绑定前统一校验知识平台健康状态，U05 通过 |
| R15 | 核心路径 1「登录 -> 看板 -> 筛选/搜索」缺少端到端记录 | 已由 React 程序化页面烟测补齐；搜索 `UI烟测 20260522` 与草稿筛选均可命中角色 `066fcc24-6e9c-4a37-b4b7-8fd3f6bd34bd` |
| R16 | `sync-all` 本地执行连续性缺少角色产品侧证据 | 已执行 `POST /api/sync-all` 4/4 成功；执行后角色产品 consumer 读取链和 UI 测试链继续通过 |
| R17 | 人工手动冒烟记录缺失 | 用户已完成 H01-H05，并确认全部通过；`delivery/test-results.md` 已补齐人工手动冒烟记录 |

当前状态: 自动化质量门禁通过；真实集成验收通过；程序化页面烟测通过；人工手动冒烟通过；当前无 Blocker。
