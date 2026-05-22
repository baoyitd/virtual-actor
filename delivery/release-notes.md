# 交付说明

版本: v0.3.0-commercial-trial | 日期: 2026-05-22 | 当前状态: Accepted

## 本版本包含

- React 正式用户入口：登录、角色列表、详情、创建、编辑、知识绑定、测试台、测试历史、人工评分、发布、版本记录、归档。
- FastAPI 根路径托管 `frontend/dist`，用户只访问一个服务地址；`prototype/` 不再作为验收对象。
- 中国企业商务后台风格 UI：稳重配色、中文业务文案、字段说明、模板辅助、状态标签、筛选/搜索、加载/错误/空状态。
- 基础登录鉴权：`POST /auth/login`、`POST /auth/logout`、`GET /auth/me`，业务 API 默认需要 Bearer token。
- 角色版本规则：已发布版本不可覆写，编辑后生成新草稿版本；测试记录冻结当时 `role_version_id`。
- 知识平台集成：知识库列表、知识目录 API、绑定持久化、绑定版本补齐、测试时真实检索入口、来源与分数展示、知识平台不可达时阻断。
- 知识平台上线验收语义已收口：文件绑定不直接限制检索范围，检索仍按 knowledge collection 级执行；正式真源字段统一为顶层 `knowledge_object_id`。
- 发布规则：发布前必须有知识绑定和当前版本测试记录，发布时写入最小 `validated_knowledge_versions`。
- 写接口一致性修复：创建、绑定、测试、评分、发布、状态迁移等写操作在返回前显式提交，避免用户刷新后读到旧状态。
- 启动迁移修复：应用启动阶段显式执行 Alembic 迁移，失败直接阻断启动；迁移连接串读取运行时数据库配置，并增加短重试以适配 Compose 冷启动。
- Docker Compose 单机交付：应用镜像、React 构建、MySQL、环境变量模板、健康检查。

## 当前已验证结果

- `./venv/bin/python -m pytest tests -q` 通过，当前为 `38 passed, 8 warnings`。
- `python3 -m compileall app` 通过。
- `cd frontend && npm run build` 通过。
- React 正式入口已完成页面级程序化烟测：登录、看板筛选/搜索、模板建角、知识搜索/选择、保存、测试、评分、发布、发布后编辑均可走通。
- 用户已完成 H01-H05 人工手动冒烟，当前 5 条高风险核心路径均通过。
- 知识平台当前依赖说明已更新为 `/Users/baoyi/Documents/code_buddy/knowledge-workbench/docs/handoff/role-product-release-dependency-note.md`，其当前交付范围 Formal Status 为 `Accepted`；最新运行态复核中 `/api/health` 正常，`health-check.sh` 为 `15/15` 通过，版本快照为 `ba280c293c5775fae52cf39cd5fd69368bae022e`。
- 本地 `POST /api/sync-all` 已执行成功，4 步均 `ok`；执行后角色产品 consumer 读取链和 UI 测试链保持可用。

## 启动方式

本地开发:

```bash
cd /Users/baoyi/Documents/code_buddy/virtual-actor
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Docker Compose:

```bash
cd /Users/baoyi/Documents/code_buddy/virtual-actor
cp .env.example .env
docker compose up --build
```

默认访问地址: `http://localhost:8000`

当前验收栈入口: `http://127.0.0.1:18000`

## 当前边界

1. React 是唯一正式用户入口，`prototype/` 仅作迁移参考。
2. 知识平台当前可以按 Accepted handoff 继续作为本轮交付范围内的真实上游，但不能外推为长期冻结公共契约版本。
3. 本地 `sync-all` 这次运行的收件箱为空，因此本轮本地证据只覆盖“`sync-all` 可执行且执行后 consumer 链继续可用”；“新增知识被 consumer 检索命中”的强证据沿用知识平台 handoff。
4. 决策产品集成暂缓，待角色产品 + 知识平台验收完成后另开准备计划。

## 当前限制

- React 详情页仍有少量中文体验问题：`decision_style`、`collaboration_mode` 会显示内部枚举值。
- 已发布角色在进入新草稿后，React UI 仅保留历史版本摘要时间线，尚无独立历史版本详情入口。
- 鉴权为内部商业试用基础能力，不覆盖企业级 RBAC、多租户、审计报表。
- 当前 Accepted 仅覆盖本轮已验收范围，不外推为长期冻结公共契约版本。

## 下一步

1. 如需继续收口体验问题，可补“详情页中文映射”和“历史版本详情入口”。
2. 若后续扩大到新能力、新边界或新的依赖冻结口径，需要按新范围重新补齐证据并走治理流程。
