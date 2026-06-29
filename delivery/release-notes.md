# 交付说明

版本: v0.5.1 | 日期: 2026-06-23 | 当前状态: Accepted

## 本版本包含

- Knowledge Workbench 公共契约切换：从 Open WebUI 直连切换至 `/api/public/*` 公共端点，alpha 阶段无 auth。
- retrieve 范围过滤落地：`knowledge_object_ids` 传入时仅在这些文档内检索；不传时全量检索（兼容模式）。
- route/retrieve 为独立运行态端点，不挂在 package 路径下；`package_id` 不参与 retrieve/route 的运行态范围定义。
- `knowledge_object_id` 格式统一为 Vault 相对路径（含 `10-Areas/` 等根前缀，含 `.md` 后缀），与知识平台存储格式一致，无需转换。
- 端点路径统一为 `/api/public/*` 前缀；默认端口 `3099`；默认包 `eve`。
- 移除 Open WebUI 遗留配置（`KNOWLEDGE_API_TOKEN`、`KNOWLEDGE_AUTH_EMAIL`、`KNOWLEDGE_AUTH_PASSWORD`）。
- React 正式用户入口：登录、角色列表、详情、创建、编辑、知识绑定、测试台、测试历史、人工评分、发布、版本记录、归档。
- FastAPI 根路径托管 `frontend/dist`，用户只访问一个服务地址。
- 角色版本规则：已发布版本不可覆写，编辑后生成新草稿版本。
- Docker Compose 单机交付。

## 补丁修复（已知问题收口）

- M01 收口：详情页与版本页枚举值中文映射。`RoleBriefingCard` 的 `latest_status` 使用 `consumeStatusText` 映射；`RoleVersions` 的 `briefing.status` 使用 `briefingStatusText` 映射；后端 `briefing_service` 的 `latest_status` 同步映射中文；AI 草稿 `decision_style` 默认值由 `balanced` 改为中文商务表达；前端新增 `decisionStyleText`/`collaborationModeText` 映射表。
- M02 收口：版本记录页详情面板从裸 JSON 升级为结构化展示，用户可直接在 UI 查看历史版本的完整定义、知识引用、数据资产和验证记录，不再需要调 API。
- M05 收口：全部 8 处 Pydantic V2 `class Config` 迁移为 `model_config = ConfigDict(from_attributes=True)`，测试日志不再有弃用警告。

## 当前已验证结果

- `./venv/bin/python -m pytest tests -q` 通过，当前为 `44 passed, 0 warnings`。
- Knowledge Workbench 公共契约端到端联调通过：packages/manifest/status/route/retrieve 全部对齐。
- retrieve scope 过滤验证通过：scoped 检索无范围泄漏，空/不存在 koid 返空，package_id 被忽略。
- 快消行业业务分析专家角色 consume 全链路通过：知识检索 + LLM 回答 status=success。
- 知识平台健康检查改为 `GET /api/public/packages`（HTTP 200 即可达），version_id `fafecb7e4b17519c06e7dd2e65ee8865619bf3ff`。

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

## 当前边界

1. React 是唯一正式用户入口，`prototype/` 仅作迁移参考。
2. Knowledge Workbench 公共契约为 alpha 阶段口径，retrieve "不传即全量"为兼容模式，不构成角色产品"专属知识边界已成立"的依据。
3. 决策产品集成暂缓，待角色产品 + 知识平台验收完成后另开准备计划。

## 当前限制

- 鉴权为内部商业试用基础能力，不覆盖企业级 RBAC、多租户、审计报表。
- `evidence_tier` 标注为后续迭代项，角色平台核心结论字段尚未增加知识支撑层级标注。
- retrieve 混合检索（open_webui 向量检索为主 + deterministic 确定性评分补充 + fallback），知识平台 Open WebUI 适配器已实现并运行，2026-06-29 联调验证检索质量通过。
- 中文 `package_id` 的 manifest/status 端点已修复（知识平台 06-24 修复），7 个包全部 200。

## 下一步

1. 最终用户验证（用户执行）。
2. 后续迭代补 evidence_tier 标注。
3. retrieve 执行机制共识确认（混合检索方案，待与知识平台走共识流程）。
