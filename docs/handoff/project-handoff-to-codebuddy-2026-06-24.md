# 项目交接说明：Virtual Actor（角色产品）

版本：`v0.5.1` | 日期：`2026-06-24` | 状态：`Accepted`

接收方：CodeBuddy + GLM-5.2

---

## 一、项目概述

**Virtual Actor** 是一个企业级 AI 角色管理平台。用户可以在平台上创建、配置、发布 AI 角色，绑定知识库和数据资产，生成外供包供外部系统（Dify / Codex）调用。

### 核心能力

1. **角色五步主链路**：01 编辑定义 → 02 使用前说明 → 03 知识与数据绑定 → 04 治理与发布 → 05 外供与调用
2. **知识检索**：通过 Knowledge Workbench 公共契约接口，按角色绑定的知识范围做 scoped retrieve
3. **外供包生成**：生成 Tool 包（Dify）或 Skill 包（Codex），下载 zip 导入外部系统
4. **consume API**：外部系统通过统一 API 调用角色，返回结构化或自由文本结果

---

## 二、技术栈

| 层 | 技术 | 版本 |
|---|---|---|
| 后端 | Python + FastAPI + Uvicorn | Python 3.14, FastAPI 0.115.6 |
| ORM | SQLAlchemy 2.0 (async) + Alembic | 2.0.36 |
| 数据库 | MySQL | 8.x |
| 前端 | React + TypeScript + Vite | React 18, Vite 5 |
| LLM | GLM-5.2（通过自定义 gateway） | — |
| 知识平台 | Knowledge Workbench（独立项目） | — |
| 部署 | Docker Compose | — |

### Python 依赖（核心）

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
aiomysql==0.2.0
alembic==1.14.0
pydantic==2.10.3
httpx==0.28.1
python-dotenv==1.0.1
pytest==8.3.4
pytest-asyncio==0.25.3
```

---

## 三、项目目录结构

```
virtual-actor/
├── app/                        # 后端
│   ├── config.py               # 全局配置（从 .env 读取）
│   ├── main.py                 # FastAPI 入口
│   ├── database.py             # 数据库连接
│   ├── init_db.py              # 建表初始化
│   ├── auth.py                 # 基础鉴权（JWT）
│   ├── models/                 # ORM 模型
│   │   ├── role_asset.py       # 角色资产
│   │   ├── role_version.py     # 角色版本
│   │   ├── role_briefing.py    # 说明卡
│   │   ├── knowledge_ref.py    # 知识引用
│   │   ├── export_package.py   # 外供包
│   │   ├── data_asset.py       # 数据资产
│   │   ├── usage_record.py     # 调用记录
│   │   └── ...
│   ├── schemas/                # Pydantic 响应模型
│   ├── routers/                # API 路由
│   │   ├── role_assets.py      # 角色 CRUD
│   │   ├── role_knowledge.py   # 知识目录/绑定
│   │   ├── role_consume.py     # consume API
│   │   ├── role_exports.py     # 外供包生成/下载
│   │   ├── role_governance.py  # 治理（发布/评分）
│   │   ├── role_ai.py          # AI 创建/推荐
│   │   └── ...
│   └── services/               # 业务逻辑
│       ├── role_service.py     # 角色核心服务（最大文件，~1274 行）
│       ├── knowledge_platform.py # 知识平台 API 调用
│       ├── consume_service.py  # consume 调用编排
│       ├── llm_service.py      # LLM 调用封装
│       ├── briefing_service.py # 说明卡生成/指纹
│       ├── export_service.py   # 外供包文件拼装
│       └── ...
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── api.ts              # API 封装
│   │   ├── pages/              # 页面组件
│   │   │   ├── RoleEdit.tsx    # 01 编辑
│   │   │   ├── RoleBriefing.tsx# 02 使用前说明
│   │   │   ├── RoleGovernance.tsx # 04 治理与发布
│   │   │   ├── RoleExports.tsx # 05 外供与调用
│   │   │   └── ...
│   │   ├── components/         # 公共组件
│   │   └── index.css           # 全局样式
│   ├── package.json
│   └── vite.config.ts
├── tests/                      # 测试
│   ├── conftest.py             # 测试 fixtures（含 mock 知识平台）
│   ├── test_api.py             # API 层测试
│   └── test_knowledge_platform_service.py # 知识平台服务测试
├── migrations/                 # Alembic 数据库迁移
│   └── versions/
├── delivery/                   # 交付文档
│   ├── known-issues.md         # 已知问题清单
│   ├── release-notes.md        # 发布说明
│   └── test-results.md         # 测试结果
├── docs/                       # 设计文档与 handoff
│   ├── handoff/                # 历次交接记录
│   └── iterations/             # 迭代设计文档
├── scripts/                    # 脚本
├── prototype/                  # 旧版原型（仅参考，不再维护）
├── .env                        # 运行态环境变量（不提交）
├── .env.example                # 环境变量模板
├── docker-compose.yml          # Docker 部署
└── venv/                       # Python 虚拟环境
```

---

## 四、环境配置

### 4.1 .env 文件（运行态实际加载）

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=virtual_actor

KNOWLEDGE_API_BASE=http://localhost:3099
KNOWLEDGE_DEFAULT_PACKAGE_ID=eve

LLM_PROVIDER=custom
LLM_API_KEY=<你的 API Key>
LLM_BASE_URL=https://mcpgateway.mengniu.cn/glm-qwen
```

**接收方需修改的配置项**：

| 配置项 | 说明 | 修改建议 |
|--------|------|---------|
| `LLM_API_KEY` | LLM 网关密钥 | 替换为你的 API Key |
| `LLM_BASE_URL` | LLM 网关地址 | 替换为你的 GLM-5.2 endpoint |
| `DB_PASSWORD` | MySQL 密码 | 按你的环境调整 |
| `KNOWLEDGE_API_BASE` | 知识平台地址 | 如果知识平台不在 localhost:3099，需修改 |
| `AUTH_SECRET` | JWT 签名密钥 | 建议替换为新的随机值 |

### 4.2 LLM 配置说明

当前 LLM 调用链路：
- `app/services/llm_service.py` 封装了 LLM 调用
- 使用 OpenAI 兼容协议（chat completions）
- `LLM_PROVIDER=custom` 表示使用自定义 gateway
- `LLM_BASE_URL` 指向 gateway 地址

如果接收方使用不同的 LLM endpoint，只需修改 `.env` 中的 `LLM_API_KEY` 和 `LLM_BASE_URL`，代码无需改动（只要 endpoint 兼容 OpenAI chat completions 协议）。

---

## 五、启动方式

### 5.1 后端

```bash
cd /path/to/virtual-actor
source venv/bin/activate  # 或用你的 Python 环境
uvicorn app.main:app --host 0.0.0.0 --port 18120
```

应用启动时会自动执行 Alembic 迁移。首次启动需确保 MySQL 已建库 `virtual_actor`。

### 5.2 前端

```bash
cd /path/to/virtual-actor/frontend
npm install
npm run build  # 生产构建，输出到 dist/
```

后端 FastAPI 根路径托管 `frontend/dist`，用户只需访问一个地址。

开发模式：

```bash
cd frontend
npm run dev  # Vite 开发服务器，热更新
```

### 5.3 测试

```bash
cd /path/to/virtual-actor
source venv/bin/activate
python -m pytest tests/ -q       # 全部测试
python -m pytest tests/test_knowledge_platform_service.py -v  # 知识平台专项
```

当前基线：`44 passed, 10 warnings`。

### 5.4 Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

---

## 六、知识平台依赖

角色平台依赖外部的 Knowledge Workbench 提供知识检索能力。这是独立项目，位于 `/Users/baoyi/Documents/code_buddy/knowledge-workbench`。

### 6.1 公共契约端点

所有端点前缀为 `/api/public/`，alpha 阶段无需 auth：

| 端点 | 用途 |
|------|------|
| `GET /api/public/packages` | 知识包列表（同时用作健康检查） |
| `GET /api/public/packages/{package_id}/manifest` | 知识包结构化元数据（文档列表） |
| `GET /api/public/packages/{package_id}/status` | 版本标识 + 健康状态 |
| `POST /api/public/route` | 问题路由（判断问题类型 Q0-Q5） |
| `POST /api/public/retrieve` | 检索（支持 `knowledge_object_ids` scope 过滤） |

### 6.2 关键约定

- `knowledge_object_id` 格式为 Vault 相对路径（如 `30-Resources/快消品行业知识/44-消费者行为与FMOT.md`），含根前缀和 `.md` 后缀
- `package_id` 可能是中文（如 `快消品行业知识`），URL 中需做 percent-encode
- retrieve 的 `knowledge_object_ids` 参数控制检索范围；不传则全量检索
- `package_id` 不参与 retrieve/route 的运行态范围定义

### 6.3 启动知识平台

```bash
cd /path/to/knowledge-workbench
python scripts/management-api.py  # 默认端口 3099
```

---

## 七、关键机制说明

### 7.1 角色版本规则

- 每次编辑生成新的草稿版本（test 状态）
- 发布后版本变为 published，不可覆写
- 外供包和 consume 调用绑定的是**已发布版本**，不是草稿

### 7.2 说明卡 source_hash

- 说明卡通过 `source_hash` 检测来源变化（角色字段 + 知识绑定 + 数据资产）
- hash 不匹配时说明卡状态为 `stale`，阻断外供包生成
- 修改角色定义或知识绑定后，需到 02 页重新保存说明卡

### 7.3 kb_id 解析逻辑

- `resolve_runtime_kb_id_from_bases` 负责将 `kb_id` 解析为知识平台的 `package_id`
- 解析优先级：精确匹配 package_id → 按 name 匹配 → 从 `knowledge_object_id` 路径反推 → 默认包
- `_hydrate_runtime_kb_ids` 在读取时做内存解析，**不落库**（历史教训：之前会 flush 落库导致数据污染）

### 7.4 外供包

- 生成时同类型自动替换旧包（每个角色最多 1 个 Tool 包 + 1 个 Skill 包）
- 生成后返回包 ID，用户通过 download 端点下载 zip
- 包内文件：`package-manifest.json`、`role-brief.md`、`consume-contract.json`、`output-contract.json`、`writeback-policy.md`，Skill 包额外含 `SKILL.md`，Tool 包额外含 Dify 契约文件

### 7.5 consume API

```
POST /role-assets/{role_id}/consume
Authorization: Bearer {token}
Content-Type: application/json

{
  "query": "用户问题",
  "context": "可选上下文",
  "caller_type": "human | external_tool | external_skill",
  "caller_id": "调用方标识",
  "role_version_id": "已发布版本 ID"
}
```

返回包含：`status`、`answer`、`structured_result`、`sources`、`boundary_status`、`usage_record_id`。

---

## 八、当前状态与已知问题

### 已完成

- v0.5.1 Knowledge Workbench 公共契约切换完成
- 知识绑定全链路修复（kb_id 解析、URL 编码、跨包 tier 统计）
- 外供包交互重设计（生成与下载分离、同类型替换、无历史列表）
- 44 项自动化测试通过
- 端到端联调验证通过（consume 全链路 + Skill 包下载 + 外部调用）

### 已知问题（非阻塞）

| # | 问题 | 严重程度 | 说明 |
|---|------|---------|------|
| M01 | React 详情页显示内部枚举值 | Major | `decision_style`、`collaboration_mode` 未映射中文 |
| M02 | 无独立历史版本详情入口 | Major | 需通过 API 查询 |
| M04 | 鉴权为基础账号，非企业级 RBAC | Limitation | 内部商业试用阶段 |
| M05 | Pydantic V2 `class Config` 弃用警告 | Minor | 不影响运行 |

### Git 状态

当前有大量未提交的改动（v0.4.0 ~ v0.5.1 的全部迭代内容）。git 仓库只有 2 个 commit（初始化 + iteration control gates），**所有业务代码均为未跟踪或已修改状态**。建议接收后先做一次完整 commit。

---

## 九、注意事项

### 9.1 不要做的事

1. **不要修改 `_hydrate_runtime_kb_ids` 让它 flush 落库**——之前因此导致 DB 中 kb_id 被静默改写
2. **不要去掉 `list_documents` 中的 `urllib.parse.quote`**——中文包名会 404
3. **不要在前端硬编码知识库偏好**（如 `10-Areas/eve`）——应信任后端返回
4. **不要在外供包生成时检查草稿版本的说明卡**——export 检查的是已发布版本
5. **`prototype/` 目录不再维护**——仅保留为迁移参考，生产入口是 React 前端

### 9.2 容易踩坑的地方

1. **后端改了代码必须重启**——uvicorn 没开 `--reload`，改代码后不会自动生效
2. **`.env` 优先级高于 `config.py` 默认值**——改了 config.py 但 .env 没改，运行时还是用 .env 的值
3. **说明卡 stale 不一定是用户改了东西**——知识平台迁移、kb_id 修复等底层变更也会导致 hash 不匹配
4. **已发布版本的说明卡和当前草稿版本的说明卡是分开的**——在 02 页保存的是当前版本，export 检查的是已发布版本

### 9.3 与知识平台的协作机制

双方通过 handoff 文档在 `docs/handoff/` 目录交换信息，遵循"先反馈再执行"原则。关键 handoff 文档：

- `knowledge-to-role-retrieve-scope-ready-2026-06-23.md`：知识平台就绪通知
- `role-to-knowledge-chinese-package-manifest-404-2026-06-24.md`：中文包名 404 缺陷反馈
- `knowledge-to-role-chinese-package-manifest-fix-2026-06-24.md`：知识平台修复回同步

---

## 十、快速验证清单

接收后按以下步骤验证环境是否就绪：

```bash
# 1. 检查 Python 环境
cd /path/to/virtual-actor
source venv/bin/activate
python -c "import fastapi, sqlalchemy, httpx; print('deps OK')"

# 2. 检查 MySQL
mysql -u root -p -e "USE virtual_actor; SHOW TABLES;"

# 3. 检查前端构建
cd frontend && npm install && npm run build

# 4. 启动后端
cd ..
uvicorn app.main:app --host 0.0.0.0 --port 18120

# 5. 健康检查
curl http://localhost:18120/health

# 6. 知识平台健康检查（需知识平台已启动）
curl http://localhost:3099/api/public/packages

# 7. 运行测试
python -m pytest tests/ -q

# 8. 登录验证
curl -s http://localhost:18120/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

全部通过即可开始工作。
