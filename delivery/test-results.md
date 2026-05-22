# 测试结果

版本: v0.3.0-commercial-trial | 测试时间: 2026-05-22 15:03 CST | 执行主体: Codex

## 自动化结果

| 项目 | 命令 / 入口 | 状态 | 结果 |
|------|-------------|------|------|
| 后端 API 自动化 | `./venv/bin/python -m pytest tests -q` | PASS | `38 passed, 8 warnings` |
| Python 编译检查 | `python3 -m compileall app` | PASS | 遍历 `app/` 全部模块，无编译错误 |
| React 生产构建 | `cd frontend && npm run build` | PASS | 生成 `frontend/dist`，Vite build succeeded |
| 角色产品健康检查 | `GET http://127.0.0.1:18000/health` | PASS | 返回 `{\"status\":\"ok\",\"service\":\"virtual-actor\",\"version\":\"0.2.0\"}` |
| 角色产品正式入口 | `GET http://127.0.0.1:18000/` | PASS | HTTP 200，返回 React `index.html` |
| 角色产品登录 | `POST http://127.0.0.1:18000/auth/login` | PASS | `admin / admin123` 登录成功 |
| 知识平台健康检查 | `GET http://127.0.0.1:3099/api/health` | PASS | `container.status=healthy`、`owui.status=ok`、`knowledge_bases=6`、`last_sync_summary=4 步骤完成，耗时 77.2s` |
| 知识平台版本快照 | `GET http://127.0.0.1:3000/api/v1/version` | PASS | 返回 JSON 版本快照，`commit_hash=ba280c293c5775fae52cf39cd5fd69368bae022e` |
| 本地 `sync-all` 执行 | `POST http://127.0.0.1:3099/api/sync-all` | PASS | 4 步均 `ok`；当前运行态 `收件箱为空，跳过`，总耗时 77.2s |
| post-sync 知识浏览 | `GET /knowledge/bases`、`GET /knowledge/catalog?kb_id=41cee65b-7f9c-4820-ba0d-bb865e0b1e41` | PASS | 角色产品侧读取到 6 个知识库；`knowledge-eve` 当前目录返回 30 条文件 |
| Docker Compose 单入口 | `http://127.0.0.1:18000/` | PASS | 验收栈 `virtualactor_acceptance` 继续可访问，单入口可用 |

## 自动化覆盖摘要

| 范围 | 状态 |
|------|------|
| 鉴权：未登录 401、登录 token、当前用户 | PASS |
| 角色 CRUD、状态迁移、归档、删除 | PASS |
| 知识库列表、知识目录、绑定、查询、解绑 | PASS |
| 多知识库绑定后按 `kb_id` 去重检索 | PASS |
| 角色测试、知识来源返回、人工评分、历史 | PASS |
| 发布校验、发布人、知识版本追溯 | PASS |
| 已发布版本不可覆写，编辑派生新草稿版本 | PASS |
| 异常路径：404、422、400 | PASS |

## 场景链与页面级验证

| # | 场景链 | 类型 | 状态 | 当前证据 |
|---|--------|------|------|----------|
| U01 | React UI 登录 -> 看板筛选/搜索 -> 新建角色 -> 搜索并绑定真实知识 -> 保存 -> 重开详情 | real integration + programmatic UI | PASS | 角色 `066fcc24-6e9c-4a37-b4b7-8fd3f6bd34bd` 由 React UI 创建；绑定 `STARTUP-PROMPT.md`；详情页显示当前版本 `acf25ae5-7dd7-4ee2-b35b-612c83c98908` 和知识版本 `ba280c293c5775fae52cf39cd5fd69368bae022e` |
| U02 | React UI 测试 -> 真实知识平台检索 -> LLM 回复 -> 展示来源与分数 -> 人工评分 -> 查看历史 | real integration + programmatic UI | PASS | 测试记录 `cabfd87b-0e23-4fcf-90c8-51d9f74cd2f4` 生成成功；来源为 `subproject-ai-execution-protocol.md`、`SOURCE-OF-TRUTH.md`、`SUBPROJECT-GOVERNANCE-UPDATE-STARTUP-PROMPT-2026-05-21.md`；评分 3 分写回成功 |
| U03 | React UI 发布 -> 查看版本记录 -> 查看知识版本追溯 | real integration + programmatic UI | PASS | 角色在 UI 中发布成功；已发布版本 `acf25ae5-7dd7-4ee2-b35b-612c83c98908`；`GET /role-versions/{id}` 返回 `validated_knowledge_versions=[STARTUP-PROMPT.md, ba280c293c5775fae52cf39cd5fd69368bae022e]` |
| U04 | React UI 编辑已发布角色 -> 保存 -> 新草稿生成 -> 旧发布版本保留 | consumer scene chain + programmatic UI | PASS | 编辑后当前版本变为 `e828049a-0cb8-463f-a189-488b1c3ecdcc`；UI 版本时间线显示 `v2 草稿` 与 `v1 已发布`；`GET /published-version` 仍返回 `acf25ae5-7dd7-4ee2-b35b-612c83c98908` |
| U05 | 知识平台不可达 -> 浏览/绑定/测试阻断 | real runtime negative | PASS | 隔离运行态 `http://127.0.0.1:18001` 下，`/health/knowledge-platform` 返回 `unreachable`；`GET /knowledge/catalog` 返回 503；绑定返回 503；测试返回 400 |
| U06 | Docker Compose 空环境启动 -> 登录 -> 完成主路径 | deployment | PASS | 验收栈 `virtualactor_acceptance` 已验证 `/health`、`/`、`/auth/login`、`/role-assets` 主路径可用 |
| U07 | `POST /api/sync-all` -> 角色产品 post-sync 浏览知识并继续完成消费链 | real integration + upstream handoff | PASS | 本地 `sync-all` 4 步执行成功；执行后角色产品侧 `/knowledge/bases`、`/knowledge/catalog`、React UI 测试链继续通过。当前本地这次运行未发布新 inbox 对象，因此“新增知识被检索命中”的强证据沿用知识平台已交付的 Accepted handoff 文档 |

### U01 React UI 新建、绑定与重开详情

- 起始状态: `http://127.0.0.1:18000/` 可访问，`admin / admin123` 可登录，知识平台健康检查通过。
- 操作步骤: 在看板搜索并确认当前角色列表可用；进入“新建角色”；选择模板“项目治理助手”；在知识弹层搜索 `STARTUP-PROMPT` 并选择 `knowledge-eve` 中的 `STARTUP-PROMPT.md`；保存角色；重开详情页。
- 实际结果: 生成角色 `066fcc24-6e9c-4a37-b4b7-8fd3f6bd34bd`；详情页显示绑定知识 `10-Areas/eve/master/l6/product-combinations/decision-closed-loop/STARTUP-PROMPT.md` 和知识版本 `ba280c293c5775fae52cf39cd5fd69368bae022e`。
- 集成真实性级别: `real integration`；页面执行方式: `programmatic UI`。

### U02 React UI 测试、评分与历史

- 起始状态: 角色已绑定真实知识，处于可进入测试的状态。
- 操作步骤: 从详情页进入测试台；输入“请根据 STARTUP-PROMPT，概括角色产品在进入实现前必须先完成哪些治理动作。”；等待检索与 LLM 回答；点击 `3 分` 评分。
- 实际结果: 生成测试记录 `cabfd87b-0e23-4fcf-90c8-51d9f74cd2f4`；知识来源显示 `subproject-ai-execution-protocol.md`、`SOURCE-OF-TRUTH.md`、`SUBPROJECT-GOVERNANCE-UPDATE-STARTUP-PROMPT-2026-05-21.md`；评分 3 分回写成功，详情页统计显示 `测试次数=1`、`最新评分=3`。
- 集成真实性级别: `real integration`；页面执行方式: `programmatic UI`。

### U03 React UI 发布与知识版本追溯

- 起始状态: 角色已完成至少一次测试并已有评分。
- 操作步骤: 在详情页点击“发布”；查看状态、版本记录和发布追溯；再调用 `GET /role-versions/acf25ae5-7dd7-4ee2-b35b-612c83c98908` 校验已发布版本详情。
- 实际结果: 角色状态变为 `published`；已发布版本 `acf25ae5-7dd7-4ee2-b35b-612c83c98908`；发布追溯保存 `knowledge_object_id=10-Areas/eve/master/l6/product-combinations/decision-closed-loop/STARTUP-PROMPT.md` 与 `knowledge_version_id=ba280c293c5775fae52cf39cd5fd69368bae022e`。
- 集成真实性级别: `real integration`；页面执行方式: `programmatic UI`。

### U04 React UI 已发布角色编辑生成新草稿

- 起始状态: 角色已发布，版本 `v1` 已存在。
- 操作步骤: 进入编辑页；修改“核心立场”；保存；回到详情页查看状态与版本时间线；再调用 `GET /published-version`。
- 实际结果: 当前角色状态回到 `draft`；新草稿版本为 `e828049a-0cb8-463f-a189-488b1c3ecdcc`；UI 版本时间线保留 `v1 已发布` 与 `v2 草稿`；`GET /published-version` 仍返回 `acf25ae5-7dd7-4ee2-b35b-612c83c98908`。
- 集成真实性级别: `consumer scene chain`；页面执行方式: `programmatic UI`。

### U05 知识平台不可达阻断

- 起始状态: 以隔离运行态 `http://127.0.0.1:18001` 启动角色产品，数据库连接真实验收库，知识平台地址显式指向不可达端口 `127.0.0.1:65534`。
- 操作步骤: 访问知识目录、尝试绑定、对已绑定角色发起测试。
- 实际结果: 健康接口返回 `knowledge_platform=unreachable`；浏览知识返回 503；绑定返回 503；测试返回 400；未写入新的绑定或测试记录。
- 集成真实性级别: `real runtime negative`。

### U06 Docker Compose 部署主路径

- 起始状态: 隔离端口 `APP_PORT=18000`、`MYSQL_PORT=13306`，空 MySQL 数据卷。
- 操作步骤: 启动 `docker compose -p virtualactor_acceptance up --build --wait -d`；访问根入口；登录；读取角色列表。
- 实际结果: `/health` 返回 200；`/` 返回 React；`/auth/login` 成功；`/role-assets` 可访问。
- 集成真实性级别: `deployment`。

### U07 本地 `sync-all` 执行与 post-sync 消费连续性

- 起始状态: 知识平台管理健康接口可达，`last_sync_summary` 可读。
- 操作步骤: 执行 `POST http://127.0.0.1:3099/api/sync-all`；随后从角色产品侧重新读取 `/knowledge/bases` 和 `/knowledge/catalog?kb_id=41cee65b-7f9c-4820-ba0d-bb865e0b1e41`；再完成一次 React UI 测试链。
- 实际结果: `sync-all` 四步均返回 `ok`，耗时 77.2 秒；当前运行态本次没有新 inbox 条目，因此没有在这一轮本地执行中生成新的知识对象；但执行后角色产品 consumer 读取链、绑定知识与测试链继续可用。
- 真实性说明: “新增知识在 consumer 语义检索中可命中”的强证据，当前沿用知识平台 `/Users/baoyi/Documents/code_buddy/knowledge-workbench/docs/handoff/role-product-release-dependency-note.md` 的 Accepted handoff，不在本次空 inbox 运行中重复制造假证据。该 handoff 明确给出：知识平台 v1.3 当前已完成本轮交付范围的最终用户验收，`/api/health` 正常，`health-check.sh` 为 `15/15` 通过，当前版本快照为 `ba280c293c5775fae52cf39cd5fd69368bae022e`；但该 Accepted 仅覆盖本轮已验收范围，不外推为长期冻结公共契约版本。

## 核心路径覆盖矩阵

| 核心路径 | 程序化页面 / 消费链验证 | 人工手动冒烟 | 当前判定 | 证据 |
|----------|-------------------------|--------------|----------|------|
| 1. 登录系统 -> 查看角色资产看板 -> 筛选/搜索角色 | 已验证 | 未验证 | 系统已验证，人工待补 | U01；看板草稿筛选与搜索 `UI烟测 20260522` 命中角色 `066fcc24-6e9c-4a37-b4b7-8fd3f6bd34bd` |
| 2. 新建角色 -> 配置五层信息 -> 浏览真实知识目录 -> 绑定知识 -> 保存 -> 重开仍可见 | 已验证 | 未验证 | 系统已验证，人工待补 | U01 |
| 3. 角色测试 -> 调用真实知识平台检索 -> LLM 回复 -> 展示来源与分数 -> 人工评分 -> 查看历史 | 已验证 | 未验证 | 系统已验证，人工待补 | U02 |
| 4. 测试通过 -> 发布角色 -> 生成不可覆写版本 -> 查看版本记录与知识版本追溯 | 已验证 | 未验证 | 系统已验证，人工待补 | U03 |
| 5. 已发布角色编辑 -> 自动生成新草稿版本 -> 原发布版本仍保留在版本记录中可查询 | 已验证 | 未验证 | 系统已验证，人工待补 | U04 |

## 页面级 UI 烟测（程序化）

状态: 已完成

说明:

- 执行入口: `http://127.0.0.1:18000/`
- 执行方式: Codex in-app browser 直接操作 React 正式入口
- 覆盖范围: 登录、看板筛选/搜索、模板建角、知识搜索/选择、保存、测试、评分、发布、发布后编辑
- 结果: 主路径全部可走通，未出现白屏、死链、不可恢复状态或错误弹窗

程序化页面烟测不是“人工手动冒烟”。它补齐了页面级运行证据，但不替代由人实际操作形成的验收记录。

## 人工手动冒烟验证

状态: 已完成

执行人: 用户

执行入口: `http://127.0.0.1:18000/`

执行结果:

| 用例 | 结果 | 备注 |
|------|------|------|
| H01 登录 + 看板筛选/搜索 | PASS | 用户确认通过 |
| H02 新建角色 + 绑定知识 | PASS | 用户确认通过 |
| H03 测试 + 评分 + 历史 | PASS | 用户确认通过 |
| H04 发布 + 版本追溯 | PASS | 用户确认通过 |
| H05 已发布后编辑 + 新草稿 | PASS | 用户确认通过 |

说明:

- 本轮核心高风险路径的人工手动冒烟已由用户实际操作完成。
- 当前 `delivery/test-plan.md` 中 5 条核心路径，现已同时具备系统级 / 程序化页面证据与人工手动冒烟结果。
- 因此“人工手动冒烟缺失”这一质量门禁缺口已关闭。

## 真实集成补充证据

| 项目 | 状态 | 结果 |
|------|------|------|
| 知识平台当前依赖口径 | PASS | 上游 `/Users/baoyi/Documents/code_buddy/knowledge-workbench/docs/handoff/role-product-release-dependency-note.md` 已更新为 `Formal Status: Accepted`；`/api/health` 正常，`health-check.sh=15/15`，版本快照为 `ba280c293c5775fae52cf39cd5fd69368bae022e`；但明确仅限当前交付范围 |
| 知识目录真源字段 | PASS | 角色产品经 `/knowledge/catalog` 读取到顶层 `knowledge_object_id` |
| 写接口读后即查一致性 | PASS | UI 新建、绑定、测试、评分、发布、再次读取均即时一致 |
| Docker Compose 启动迁移 | PASS | 验收栈 `virtualactor_acceptance` 持续可用，空环境启动证据已存在且当前入口健康 |
| `sync-all` 本地执行 | PASS | 角色产品侧已验证本地执行成功与 post-sync 连续性；当前运行无新 inbox 条目，因此未伪造“本次新增知识命中”证据 |

## 当前结论

自动化/API 质量门禁、真实知识平台集成、`sync-all` 本地执行连续性、Docker Compose 部署主路径、React 正式入口的程序化页面烟测，以及 H01-H05 人工手动冒烟结果均已补齐。

当前 5 条核心用户路径都已有系统级、程序化页面级和人工手动冒烟证据，不再存在“核心路径 1 未验证”“人工手动冒烟缺失”或“只有部分场景链”的问题。

当前线程中用户已明确确认正式签收，因此当前版本可从 `User-Acceptance-Candidate` 升级为 `Accepted`。

同时保持边界不变：

- 本项目当前 `Accepted` 仅覆盖本轮已验收范围。
- 不外推为长期冻结公共契约版本。
- 决策产品消费侧集成仍不在本轮 Accepted 范围内。
