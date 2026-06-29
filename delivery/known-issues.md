# 已知问题清单

版本: v0.5.1 | 日期: 2026-06-23

| # | 问题 | 严重程度 | 影响范围 | 阻塞验收 | 绕行方式 | 后续计划 |
|---|------|---------|---------|---------|---------|---------|
| M04 | 鉴权为内部商业试用基础账号，不是企业级 RBAC | Known Limitation | 用户权限精细化 | 否 | 使用强密码和 `AUTH_SECRET`，限制内网访问 | 公测或企业部署前补账号体系 / RBAC |

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
| R08 | 健康检查与鉴权口径不清 | 已切换至 Knowledge Workbench 公共契约，健康检查改为 `GET /api/public/packages`（HTTP 200 即可达），alpha 阶段无 auth |
| R09 | 知识平台验收账号与版本快照接口运行态异常 | 已修复，真实登录与版本快照均已通过 |
| R10 | 写接口读后即查旧状态 | 已修复，写接口返回前显式提交事务，UI 创建/绑定/测试/发布链均通过 |
| R11 | Docker Compose 启动后应用未执行迁移，登录后首个受保护接口报表不存在 | 已修复；验收栈 `/role-assets` 可正常访问 |
| R12 | Alembic 迁移仍读取 `localhost`，容器内无法连到 MySQL | 已修复；迁移环境改为读取运行时 `settings.database_url` |
| R13 | Docker Compose 空环境部署验收未完成 | 已补齐；隔离栈 `virtualactor_acceptance` 已通过主路径验证 |
| R14 | 知识平台不可达时，知识绑定接口可被手工 `knowledge_version_id` 绕过 | 已修复；绑定前统一校验知识平台健康状态，U05 通过 |
| R15 | 核心路径 1「登录 -> 看板 -> 筛选/搜索」缺少端到端记录 | 已由 React 程序化页面烟测补齐；搜索 `UI烟测 20260522` 与草稿筛选均可命中角色 `066fcc24-6e9c-4a37-b4b7-8fd3f6bd34bd` |
| R16 | `sync-all` 本地执行连续性缺少角色产品侧证据 | 已执行 `POST /api/sync-all` 4/4 成功；执行后角色产品 consumer 读取链和 UI 测试链继续通过 |
| R17 | 人工手动冒烟记录缺失 | 用户已完成 H01-H05，并确认全部通过；`delivery/test-results.md` 已补齐人工手动冒烟记录 |
| R18 | Open WebUI Token 过期（原 M03） | 已切换至 Knowledge Workbench 公共契约（`/api/public/*`），alpha 阶段无 auth，不再依赖 Bearer token；`KNOWLEDGE_API_TOKEN`/`KNOWLEDGE_AUTH_EMAIL`/`KNOWLEDGE_AUTH_PASSWORD` 已从配置中移除 |
| R19 | 知识平台端点路径不一致（`/api/*` vs `/api/public/*`） | 已统一为 `/api/public/*` 前缀；retrieve/route 为独立运行态端点，不挂在 package 路径下 |
| R20 | 默认端口与包名不一致 | 已统一为 `localhost:3099` + 默认包 `eve`；`.env`/`.env.example`/`config.py`/`docker-compose.yml` 对齐 |
| R21 | retrieve 返回 `knowledge_object_id` 字段未被映射 | 已更新 chunk 映射，`normalize_file` 优先取 `knowledge_object_id`（Vault 相对路径含 `.md` 后缀） |
| M01 | React 角色详情页显示内部枚举值 | `RoleBriefingCard` 的 `latest_status` 使用 `consumeStatusText` 映射；`RoleVersions` 的 `briefing.status` 使用 `briefingStatusText` 映射；版本详情面板移除裸 JSON 改为结构化展示；后端 `briefing_service` 的 `latest_status` 映射中文；AI 草稿 `decision_style` 默认值改为中文；前端新增 `decisionStyleText`/`collaborationModeText` 映射表 |
| M02 | 无独立历史版本详情入口 | `RoleVersions` 版本详情面板从裸 JSON 升级为结构化展示（版本ID、输出方式、核心职责、分析视角、知识边界、说明卡状态、知识引用、数据资产、验证记录），用户可直接在版本记录页查看完整版本详情 |
| M05 | Pydantic V2 `class Config` 弃用警告 | 全部 8 处 `class Config: from_attributes = True` 迁移为 `model_config = ConfigDict(from_attributes=True)`，涉及 knowledge/role/test_run/data_asset/version/config 共 6 个 schema 文件 |

当前状态: 自动化质量门禁通过（44 passed，0 warnings）；Knowledge Workbench 公共契约切换完成；端到端联调通过；M01/M02/M05 已收口；当前无 Blocker。
