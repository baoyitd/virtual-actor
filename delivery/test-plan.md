# 测试计划

版本: v0.3.0-commercial-trial | 日期: 2026-05-22 | 验收对象: React 正式入口 + FastAPI API + 真实知识平台 + Docker Compose 单机

## 交付范围

- 内部商业试用形态，不按 `prototype/` 原型验收。
- 用户入口为 React 构建物，由 FastAPI 根路径托管；`prototype/` 仅保留为迁移参考。
- 角色资产管理覆盖列表、详情、创建、编辑、知识绑定、测试、测试历史、人工评分、发布、版本记录、归档。
- 基础登录鉴权、用户身份注入、发布人记录、受保护业务 API。
- 知识平台真实集成闭环：知识库列表、知识目录、绑定持久化、测试检索、来源与分数展示、知识平台不可达时阻断。
- 版本规则：已发布版本不可覆写，编辑已发布角色派生新草稿版本，测试记录冻结 `role_version_id`，发布保存 `validated_knowledge_versions` 最小追溯结构。
- Docker Compose 单机交付，包含应用、React 构建物、MySQL、环境变量模板、健康检查。
- 知识平台当前依赖口径按 `/Users/baoyi/Documents/code_buddy/knowledge-workbench/docs/handoff/role-product-release-dependency-note.md` 的当前范围执行：consumer 读取链和 `POST /api/sync-all` 可依赖，但不表述为长期冻结公共契约版本。

## 不交付范围

- 暂不推进角色产品到决策产品的消费侧集成，不冻结决策产品依赖版本。
- 不做公开 SaaS 的计费、多租户、企业级 RBAC、HTTPS 域名和完整监控体系。
- 不修改上位已裁决公共字段、公共对象、读写边界和版本规则。
- 不将 `RolePublishRecord` 作为公共对象暴露。
- 不把知识平台当前 Accepted 口径外推为长期冻结依赖版本。

## 质量门禁

| 门禁 | 通过标准 |
|------|---------|
| 自动化 API | `venv/bin/pytest -q` 全部通过，覆盖鉴权、角色、知识、测试、评分、发布、归档、版本冻结、错误路径 |
| Python 编译检查 | `python3 -m compileall app` 通过，无编译错误 |
| 前端构建 | `npm run build` 通过，React 页面不依赖 `prototype/` |
| 真实知识平台 | 使用真实 Open WebUI/知识平台完成知识库列表、目录、绑定、检索、来源展示；不可用时记录阻塞，不用 fixture 冒充 |
| `sync-all` 联动 | `POST /api/sync-all` 可成功执行；执行后角色产品 consumer 读取链继续可用 |
| 核心场景链 | 覆盖 `delivery/test-plan.md` 中全部核心路径，记录操作步骤、验证点、证据、状态、真实性级别 |
| 页面级 UI 烟测 | 通过 React 正式入口完成页面级主路径验证，记录角色/版本/测试 ID；该项是页面证据补充，不替代人工手动冒烟 |
| 人工手动冒烟 | 由人实际操作 React 正式入口，覆盖本轮全部高风险核心路径；未完成前 Formal Status 不得升级为 `User-Acceptance-Candidate` 或 `Accepted` |
| 部署 | Docker Compose 空环境启动，迁移成功，用户访问一个服务地址完成主路径 |
| 交付证据 | 更新 `test-plan.md`、`test-cases.md`、`test-results.md`、`known-issues.md`、`release-notes.md`、`portfolio-sync.md` |

## 核心用户路径

1. 登录系统 -> 查看角色资产看板 -> 筛选/搜索角色。
2. 新建角色 -> 选择模板或手工填写 -> 浏览真实知识目录 -> 绑定知识 -> 保存 -> 重开仍可见。
3. 角色测试 -> 调用真实知识平台检索 -> LLM 回复 -> 展示来源与分数 -> 人工评分 -> 查看历史。
4. 测试通过 -> 发布角色 -> 生成不可覆写版本 -> 查看版本记录与知识版本追溯。
5. 已发布角色编辑 -> 自动生成新草稿版本 -> 原发布版本仍保留在版本记录中可查询。

## 停止条件

- 需要扩大上位公共字段或新增公共对象时停止并上提。
- 知识平台真实接口不可达、无有效凭据或无法返回版本标识时，停止真实集成验收并记录阻塞。
- Docker Compose 无法从空环境启动时，停止商业试用上线判断。
- 如果后续发现需要改动公共契约、跨项目依赖边界、版本规则或已裁决字段，必须停止相关变更并上提。
- 在人工手动冒烟未完成前，不得将当前版本表述为 `User-Acceptance-Candidate`、`Accepted`、上线完成版本或稳定可冻结依赖版本。
