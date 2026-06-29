# v0.5.0 测试结果（工作方预检 + 测试方独立复核 + Codex / Dify 代表验证）

版本：v0.5.0 | 测试时间：2026-06-11 | 执行主体：Codex  
Formal Status：Self-Tested

> 本文档记录 `v0.5.0` 的工作方预检结果，以及测试方已完成的本地独立复核结论。  
> 当前结论是：**平台内主链路、本地独立复核、`Codex / Dify` 代表环境真实调用与平台回写均已闭合；`v0.5.0` 已达到 `Self-Tested`，可进入最终用户测试。**

## 1. 自动化结果

| 项目 | 命令 / 入口 | 状态 | 结果 |
| --- | --- | --- | --- |
| 后端 API 自动化 | `./venv/bin/python -m pytest tests -q` | PASS | `22 passed, 8 warnings` |
| Python 编译检查 | `python3 -m compileall app` | PASS | 遍历 `app/` 全部模块，无编译错误 |
| React 生产构建 | `cd frontend && npm run build` | PASS | `frontend/dist` 生成成功 |
| Markdown lint | `npm run lint:md` | PASS | `Summary: 0 error(s)` |
| Vale 语法检查 | `vale delivery docs/iterations/v0.5.0 portfolio-sync.md` | PASS | `0 errors, 0 warnings` |
| 迭代守卫 | `python3 scripts/iteration-guard.py --repo-root . --mode release` | PASS | `Delivered version = v0.3.0-commercial-trial`，`Active iteration = v0.5.0`，`Formal Status = Self-Tested` |

## 2. 运行态与浏览器烟测

### 2.1 Smoke runtime

| 项目 | 入口 | 状态 | 结果 |
| --- | --- | --- | --- |
| v0.5 smoke runtime | `npm run smoke:v05:runtime` | PASS | 独立 SQLite + fake knowledge / fake LLM 运行态启动成功 |
| 健康检查 | `GET http://127.0.0.1:18080/health` | PASS | 返回 `{"status":"ok","service":"virtual-actor","version":"0.5.0"}` |

说明：

1. 该 runtime 复用真实 FastAPI + React 构建物，专门用于在本地缺少 Docker / MySQL / 真实知识平台时完成稳定复现。
2. 该 runtime **证明主链路和前后端契约闭合**，但**不证明真实外部依赖已闭合**。

### 2.2 程序化浏览器烟测

执行命令：`npm run smoke:v05:browser`  
执行结果：**PASS**  
证据目录：`tmp/v05-browser-smoke/`  
最新样本角色：`17fb5677-3609-4e75-928d-949319513e8b`

| 步骤 | 验证内容 | 状态 |
| --- | --- | --- |
| 1 | 登录 -> 进入角色列表 | PASS |
| 2 | 管理员新增数据资产 | PASS |
| 3 | AI 起草 -> 创建角色草稿 | PASS |
| 4 | 绑定真实知识目录项 | PASS |
| 5 | 说明卡由 `stale` -> `fresh` 确认闭合 | PASS |
| 6 | 治理侧补齐并进入内部试用 | PASS |
| 7 | `test-consume` 生成验证记录 | PASS |
| 8 | 测试后说明卡再次进入 `stale` 并重新确认 | PASS |
| 9 | 发布当前版本 | PASS |
| 10 | 生成 `Tool package / Skill package` 并模拟外部调用回写 | PASS |
| 11 | 正式消费与资产市场 AI 推荐 | PASS |

已产出截图：

1. `01-role-list.png`
2. `02-data-assets.png`
3. `03-role-edit.png`
4. `04-knowledge-bound.png`
5. `05-briefing-fresh.png`
6. `06-governance-test-ready.png`
7. `07-test-consume.png`
8. `08-published.png`
9. `09-exports.png`
10. `10-usage-desk.png`
11. `11-marketplace.png`

以及 `tmp/v05-browser-smoke/summary.json`。

## 3. 当前预检已经证明的范围

1. `v0.5` 的主工作区、说明卡生命周期、治理门禁、测试台、使用台、外供页、市场页已形成可执行闭环，不是“只有字段保存”的静态实现。
2. `L3` 数据能力与 `L4` 输出契约至少在平台内 smoke runtime 上已经真实影响 `test / consume` 返回，而不是只显示在页面。
3. 外供链路已能生成 `Tool / Skill` 形态、模拟外部调用并回写平台侧记录。
4. 程序化浏览器烟测已覆盖从创建到正式消费、再到市场推荐的完整主链路，页面未出现白屏、死链或核心动作失效。

## 4. 本轮补齐并闭合的范围

本轮新增闭合了此前唯一剩余阻塞项：

1. `Dify` 代表环境真实调用与平台回写证据。
2. `Tool package` 在 `Dify` 中“只补环境配置即可调用”的最小直用标准。

## 5. 风险与备注

1. `pytest` 仍有 8 条 Pydantic V2 class-based config deprecation warnings；当前不阻断功能，但应列入后续技术清理。
2. 当前 smoke runtime 使用 fake knowledge / fake LLM，因此不能把本轮结果表述为“真实知识平台 / 真实模型 / 真实外部平台均已闭合”。
3. 浏览器烟测脚本已修正为可容忍重复 smoke 数据，不再因同名卡片导致假失败。

## 6. 测试方独立复核结果（2026-06-11）

### 6.1 测试方复跑结果

| 项目 | 命令 / 入口 | 状态 | 结果 |
| --- | --- | --- | --- |
| 后端 API 自动化（不写盘） | `PYTHONDONTWRITEBYTECODE=1 ./venv/bin/python -m pytest tests -q -p no:cacheprovider` | PASS | `22 passed, 8 warnings` |
| Python 编译检查 | `python3 -m compileall app` | PASS | Codex 外供契约修复后复跑通过 |
| Markdown lint | `npm run lint:md` | PASS | `0 error(s)` |
| Vale 语法检查 | `vale delivery docs/iterations/v0.5.0 portfolio-sync.md` | PASS | `0 errors, 0 warnings` |
| 迭代守卫 | `python3 scripts/iteration-guard.py --repo-root . --mode release` | PASS | `Active iteration = v0.5.0`，`Formal Status = Self-Tested` |
| smoke runtime 健康检查 | `GET http://127.0.0.1:18080/health` | PASS | 返回 `{"status":"ok","service":"virtual-actor","version":"0.5.0"}` |
| 浏览器烟测 | `npm run smoke:v05:browser` | PASS | 从登录到市场推荐整条链路复现成功 |

说明：

1. 测试方本轮未重复执行 `compileall` 和前端 build；这两项仍沿用工作方预检结果。
2. 当前卡点已从代表环境真实调用证据转为最终用户测试 / 验收阶段。

### 6.2 测试方人工与运行效果补证

人工 UI / Human smoke 抽查证据：

1. `tmp/v05-tester-manual/manual-00-role-list.png`
2. `tmp/v05-tester-manual/manual-role-edit.png`
3. `tmp/v05-browser-smoke/05-briefing-fresh.png`
4. `tmp/v05-browser-smoke/06-governance-test-ready.png`
5. `tmp/v05-browser-smoke/09-exports.png`
6. `tmp/v05-browser-smoke/10-usage-desk.png`
7. `tmp/v05-tester-manual/manual-07-marketplace-out-of-scope-debug.png`

API 级运行效果验证报告：

- `tmp/v05-tester-api-runtime/report.json`

报告已验证：

1. 绑定知识 + 数据 + `structured` 时，结果同时包含 `knowledge` 和 `data` 来源。
2. 无知识绑定但询问制度依据时，正确返回 `insufficient_knowledge`。
3. `freeform` 角色返回自由文本，`structured_result` 为空。
4. 有知识无数据时，只返回 `knowledge` 来源，不伪装数据能力。
5. 按导出的 `Skill / Tool` 包内 `consume-contract.json` 发起真实调用时，`external_skill / external_tool` 都能成功写回 `usage_record`。

### 6.3 Codex 代表环境真实验证（2026-06-11）

隔离验证环境：

1. fresh `CODEX_HOME`：`/private/tmp/v05-codex-home-isolated`
2. fresh workspace：`/private/tmp/v05-codex-fresh-workspace-isolated`
3. 仅复制导出的 `Skill package` 与 provider 配置，不读取仓库源码

关键证据：

1. `tmp/v05-codex-runtime-isolated/summary.json`
2. `tmp/v05-codex-runtime-isolated/skill-events.jsonl`
3. `tmp/v05-codex-runtime-isolated/skill-last.txt`

本轮先暴露并修复了两个真实缺口：

1. 初版 `SKILL.md` 缺少 Codex 所需 YAML frontmatter，fresh session 无法把导出物识别为合法 skill。
2. 初版 `consume-contract.json` 缺少 auth / input / output 边界；在隔离环境中模型按错误结构发起请求，返回 `422 body.query missing`。

修复后复验结果：

1. 导出的 `Skill package` 可在隔离 fresh session 中被自然语言触发。
2. 事件日志仅读取 `/private/tmp/v05-codex-home-isolated/skills/...` 下的包文件，不依赖仓库源码推断请求结构。
3. `consume` 真实返回 `200`，并生成 `usage_record_id = 3abf38c7-7f7e-4ee2-984c-3befe765e25e`。
4. 平台侧 `consume-records` 可见 `caller_type = external_skill`、`caller_id = codex-skill`、`role_version_id = 92771524-346e-4817-b018-5288af669a28`、`status = success`。

结论：`Codex` 代表环境真实验证**已闭合**。

### 6.4 Dify 代表环境真实验证（2026-06-11）

真实环境与接入方式：

1. 本地 `Dify` 环境入口：`http://127.0.0.1/`
2. 验证路径：导出 `Tool package` -> 仅补 `VIRTUAL_ACTOR_BASE_URL / VIRTUAL_ACTOR_TOKEN` -> 导入 `Dify` custom API provider -> 发起一次真实调用
3. 未要求接入方手工拼接 `role_id / role_version_id / consume` 契约

关键证据：

1. `tmp/v05-dify-runtime/dify-provider-runtime.json`
2. `tmp/v05-dify-runtime/dify-provider-add-result.json`
3. `tmp/v05-dify-runtime/dify-preview-runtime.json`
4. `tmp/v05-dify-runtime/dify-preview-result.json`
5. `tmp/v05-dify-runtime/platform-consume-records.json`
6. `tmp/v05-dify-runtime/db-usage-record.json`
7. `tmp/v05-dify-runtime/reconciliation-summary.json`

复核结果：

1. `Dify` 已成功导入 package-derived provider，返回 `{"result":"success"}`。
2. `Dify` 真实调用返回 `status = success`、`role_id = 31a5ecdd-e437-402b-8bc8-a1285f601263`、`role_version_id = 4aef4b97-597f-4fc7-b3ab-bb0d43ff9887`、`output_type = decision_advice`、`usage_record_id = 3fd80795-41b0-47a3-a67f-e4150d6cfa11`。
3. 平台侧 `/consume-records?caller_type=external_tool` 可见同一条记录，`caller_id = dify-tool-package`、`caller_type = external_tool`、`status = success`、`boundary_status` 与 `sources` 全量一致。
4. SQLite 运行库中的 `usage_records` 表可按同一 `usage_record_id` 查到完全一致的记录。
5. `reconciliation-summary.json` 已逐项核对 `role_id / role_version_id / status / boundary_status / output_type / caller_id / caller_type / sources`，结论为 `closed`。

结论：`Dify` 代表环境真实验证**已闭合**。

## 7. 当前结论

当前判定应为：

1. 工作方预检：通过
2. 测试方本地独立复核：通过
3. `Codex` 代表环境真实调用：已闭合
4. `Dify` 代表环境真实调用：已闭合
5. 是否允许进入最终用户测试：是

因此当前仍保持：

- `Formal Status = Self-Tested`
- 可进入最终用户测试
- 不升级为 `User-Acceptance-Candidate / Accepted`（直到完成最终用户测试与正式签收）
