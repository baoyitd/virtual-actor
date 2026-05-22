# 测试用例

版本: v0.3.0-commercial-trial | 日期: 2026-05-22

## 自动化 API 测试

| # | 用例 | 验证点 |
|---|------|--------|
| A01 | `GET /health` | 匿名可访问，返回服务状态 |
| A02 | 未登录访问 `/role-assets` | 返回 401 |
| A03 | `POST /auth/login` | 正确账号返回 Bearer token 与用户信息 |
| A04 | `GET /auth/me` | 登录后返回当前用户 |
| A05 | `POST /role-assets` 创建角色 | 201，生成草稿角色与 `role_version_id` |
| A06 | `GET /role-assets` 角色列表 | 200，包含状态、版本、模型、测试统计 |
| A07 | `GET /role-assets/{id}` 角色详情 | 200，包含五层字段、知识绑定、版本追溯 |
| A08 | `PATCH /role-assets/{id}` 更新角色 | 字段更新并写入当前版本快照 |
| A09 | `DELETE /role-assets/{id}` 删除角色 | 204，后续访问返回 404 |
| A10 | `POST /role-assets/{id}/to-test` | 状态变为 `test` |
| A11 | 发布前无知识或无测试 | 返回 400，明确阻断 |
| A12 | `POST /role-assets/{id}/publish` | 状态变为 `published`，发布人记录为当前用户 |
| A13 | `POST /role-assets/{id}/archive` | 状态变为 `archived` |
| A14 | `GET /role-assets/{id}/published-version` | 返回已发布版本 |
| A15 | `GET /role-versions/{version_id}` | 返回不可变版本详情与模型绑定 |
| A16 | `GET /role-assets/{id}/versions` | 返回版本列表 |
| A17 | `GET /knowledge/bases` | 返回当前账号可访问的知识库列表 |
| A18 | `GET /knowledge/catalog` | 从真实知识平台读取知识目录，失败时 503 |
| A19 | `POST /role-assets/{id}/knowledge` | 绑定知识并补齐知识版本标识 |
| A20 | `GET /role-assets/{id}/knowledge` | 绑定后重开仍可见 |
| A21 | `DELETE /role-assets/{id}/knowledge/{ref_id}` | 解绑成功 |
| A22 | 未绑定知识运行测试 | 返回 400，避免绕过真实知识集成 |
| A23 | `POST /role-assets/{id}/test` | 运行测试，冻结当前 `role_version_id`，返回知识来源与分数 |
| A24 | `GET /role-assets/{id}/tests` | 返回测试历史 |
| A25 | `POST /test-runs/{id}/rate` | 保存人工评分 |
| A26 | 编辑已发布角色 | 派生新草稿版本，原发布版本仍可查询 |
| A27 | 多知识库绑定后运行测试 | 基于绑定集合中的 `kb_id` 去重后检索，不把 `knowledge_object_id` 当 collection |
| A28 | 筛选 `status=published` | 仅返回已发布角色 |
| A29 | 筛选 `status=draft` | 仅返回草稿角色 |
| A30 | 不存在角色详情 | 返回 404 |
| A31 | 更新不存在角色 | 返回 404 |
| A32 | 创建时名称为空 | 返回 422 |
| A33 | 创建时缺少 `model_binding` | 返回 422 |
| A34 | 绑定知识到不存在角色 | 返回 404 |

## 前端构建与页面用例

| # | 用例 | 验证点 |
|---|------|--------|
| F01 | `npm run build` | TypeScript 与 Vite 构建通过，输出 `frontend/dist` |
| F02 | 登录页 | 中文商务登录文案、错误提示、Loading 状态 |
| F03 | 角色列表 | 看板指标、状态筛选、搜索、表格操作可用 |
| F04 | 创建/编辑表单 | 字段说明、示例、推荐写法、模板卡片清晰可用 |
| F05 | 知识选择弹层 | 支持搜索、知识库分组、目录展开、文件选择 |
| F06 | 角色详情 | 五层信息、知识绑定、版本记录、发布追溯展示清晰 |
| F07 | 测试台 | 历史、来源、评分、上下文面板和发送状态完整 |
| F08 | 发布与归档操作 | 状态切换正确，按钮状态符合角色状态 |
| F09 | 已发布角色编辑 | 保存后生成新草稿版本，版本时间线保留旧发布版本 |
| F10 | 错误/空/加载状态 | 不出现空白页或不可恢复状态 |
| F11 | 1280 / 1440 / 平板宽度 | 核心操作无遮挡、无错位 |
| F12 | 页面级程序化烟测 | 登录 -> 看板筛选/搜索 -> 新建 -> 绑定 -> 测试 -> 评分 -> 发布 -> 编辑 全链可走通 |

## 真实集成场景链

| # | 场景 | 类型 | 验证点 |
|---|------|------|--------|
| U01 | React UI 登录 -> 看板筛选/搜索 -> 新建角色 -> 绑定真实知识 -> 保存 -> 重开详情 | real integration + programmatic UI | 正式入口可用，知识目录来自真实知识平台，绑定持久化可见 |
| U02 | React UI 测试 -> 真实知识平台检索 -> LLM 回复 -> 展示来源与分数 -> 人工评分 -> 查看历史 | real integration + programmatic UI | 检索不是 mock/fixture，测试记录冻结当前版本 |
| U03 | React UI 发布 -> 查看版本记录 -> 查看知识版本追溯 | real integration + programmatic UI | 发布版本不可覆写，`validated_knowledge_versions` 仅含两个裁决字段 |
| U04 | React UI 编辑已发布角色 -> 生成新草稿 -> 旧发布版本仍保留在版本记录 | consumer scene chain + programmatic UI | 新草稿版本生成成功，旧发布版本仍可查询 |
| U05 | 知识平台不可达 -> 浏览/绑定/测试 | real runtime negative | 返回明确错误并阻断相关操作 |
| U06 | Docker Compose 空环境启动 -> 登录 -> 完成主路径 | deployment | 一个入口可访问 React，迁移和 MySQL 持久化正常 |
| U07 | `POST /api/sync-all` -> 角色产品 post-sync 浏览知识并继续完成消费链 | real integration | `sync-all` 可执行，执行后角色产品 consumer 读取链继续可用 |

## 人工手动冒烟用例

| # | 用例 | 验证点 |
|---|------|--------|
| H01 | 人工登录 -> 看板草稿筛选 -> 搜索 `UI烟测 20260522` | 登录态、筛选、搜索结果与角色卡片一致 |
| H02 | 人工新建角色 -> 选模板 -> 打开知识弹层 -> 搜索并选择知识 -> 保存 | 中文说明可理解，知识选择可操作，保存后详情正确 |
| H03 | 人工进入测试台 -> 发起测试 -> 查看来源 -> 评分 -> 返回历史 | 回复、来源、评分回写正常 |
| H04 | 人工发布角色 -> 查看版本记录与知识追溯 | 发布状态、发布时间、知识版本信息正确 |
| H05 | 人工编辑已发布角色 -> 保存 -> 查看新草稿和旧发布版本 | 新草稿生成成功，旧发布版本仍在版本记录中保留 |
