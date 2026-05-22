# 角色产品 — 技术选型与数据存储方案

> 版本：v0.1 | 日期：2026-05-14
> 语言：Python 3.12+
> 状态：草案，待确认后进入实现

---

## 一、技术栈总览

```
┌──────────────────────────────────────────────────────┐
│                    前端                              │
│  HTML + CSS + Vanilla JS（原型已存在）                │
│  后续可演进为 React/Vue                               │
├──────────────────────────────────────────────────────┤
│                    后端                              │
│  FastAPI + Uvicorn                                   │
│  SQLAlchemy 2.0 + Alembic（ORM + 迁移）              │
│  Pydantic v2（数据校验 / 序列化）                     │
│  httpx（async HTTP 客户端，调用外部 API）             │
├──────────────────────────────────────────────────────┤
│                    存储                              │
│  MySQL 8.0（Docker 本地，已启动）                     │
│  aiomysql（异步驱动）                                 │
│  本地文件系统（测试记录 / 导出文件）                   │
├──────────────────────────────────────────────────────┤
│                    外部依赖                           │
│  Dify API（知识平台 — 4 项接口）                      │
│  LLM API（OpenAI / Anthropic / Ollama，角色测试用）   │
│  决策产品（消费侧，角色产品只暴露接口）                │
└──────────────────────────────────────────────────────┘
```

---

## 二、后端框架：FastAPI

### 2.1 选型理由

| 维度 | FastAPI 优势 |
|------|------------|
| **Python 生态** | 用户指定 Python，FastAPI 是 Python 后端首选 |
| **异步支持** | async/await 原生支持，调用 Dify + LLM 均为 I/O 密集型 |
| **自动文档** | OpenAPI/Swagger 自动生成，决策产品可直接查阅接口契约 |
| **类型安全** | Pydantic v2 深度集成，请求/响应自动校验 |
| **轻量** | MVP 阶段无需 Django 的全家桶，FastAPI 按需装配 |

### 2.2 依赖清单

```txt
# requirements.txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
aiomysql==0.2.0
alembic==1.14.0
pydantic==2.10.3
httpx==0.28.1
python-dotenv==1.0.1
```

---

## 三、数据存储：MySQL 8.0（Docker）

### 3.1 选型理由

| 维度 | 说明 |
|------|------|
| **当前环境** | 本机 Docker 已有 MySQL 实例运行，零额外成本 |
| **异步驱动** | aiomysql，与 FastAPI async/await 契合 |
| **字段支持** | 原生 JSON 类型（knowledge_retrieved/tags 等），UTF8MB4 |
| **迁移** | Alembic 自动管理 DDL，版本可控 |

### 3.2 连接配置

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = "mysql+aiomysql://root:password@localhost:3306/virtual_actor?charset=utf8mb4"

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=5, max_overflow=10)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

### 3.3 为什么不引入 Redis / 向量数据库

- **Redis**：角色产品 MVP 阶段无高并发缓存需求，不需要
- **向量数据库**：知识检索由知识平台的 Dify 负责，角色产品不做自己的向量索引

### 3.4 文件存储

| 内容 | 路径 | 说明 |
|------|------|------|
| 测试记录 JSON | `data/test_runs/{role_id}/` | 每次测试输入/输出归档 |
| 导出文件 | `data/exports/` | CSV/JSON 导出结果 |

---

## 四、数据库表设计

### 4.1 ER 概览

```
RoleAsset  1 ──→ N  RoleVersion
RoleAsset  1 ──→ N  KnowledgeRef
RoleAsset  1 ──→ N  TestRunRecord
```

### 4.2 表：`role_assets`（角色主表）

| 列名 | MySQL 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | CHAR(36) | PK | 即 role_id（UUID 字符串） |
| `name` | VARCHAR(128) | NOT NULL | 角色名称 |
| `bio` | VARCHAR(512) | NOT NULL | 一句话描述 |
| `tags` | JSON | | 标签列表：`["finance","risk"]` |
| `status` | VARCHAR(16) | NOT NULL, DEFAULT 'draft' | draft/test/published/archived |
| `current_version_id` | CHAR(36) | nullable, INDEX | 当前发布版本 |
| `avatar_url` | VARCHAR(512) | | 头像 URL |
| `created_at` | DATETIME(6) | NOT NULL, DEFAULT CURRENT_TIMESTAMP(6) | |
| `updated_at` | DATETIME(6) | NOT NULL, DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) | |

### 4.3 表：`role_versions`（版本表）

| 列名 | MySQL 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | CHAR(36) | PK | 即 role_version_id |
| `role_id` | CHAR(36) | FK → role_assets.id, NOT NULL, INDEX | 所属角色 |
| `version_number` | INT | NOT NULL | 自增版本号（1,2,3…） |
| `status` | VARCHAR(16) | NOT NULL | draft/test/published/archived |
| `published_at` | DATETIME(6) | | 发布时间 |
| `published_by` | VARCHAR(64) | | 发布人 |
| `is_deprecated` | TINYINT(1) | DEFAULT 0 | 不建议使用标记 |
| `change_note` | TEXT | | 变更说明 |
| `created_at` | DATETIME(6) | NOT NULL | |

### 4.4 表：`role_version_fields`（版本字段快照 — EAV 模式）

| 列名 | MySQL 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | CHAR(36) | PK | |
| `version_id` | CHAR(36) | FK → role_versions.id, NOT NULL, INDEX | 所属版本 |
| `layer` | VARCHAR(4) | NOT NULL | L1/L2/L3/L4/L5 |
| `field_name` | VARCHAR(64) | NOT NULL | 字段名 |
| `field_value` | JSON | NOT NULL | 字段值 |

唯一约束：`UNIQUE(version_id, field_name)`

### 4.5 表：`knowledge_refs`（知识绑定表）

| 列名 | MySQL 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | CHAR(36) | PK | |
| `role_id` | CHAR(36) | FK → role_assets.id, INDEX | 所属角色 |
| `knowledge_id` | VARCHAR(256) | NOT NULL | 知识平台的知识标识 |
| `title` | VARCHAR(256) | | 知识标题（绑定时快照） |
| `type` | VARCHAR(32) | | 知识类型（design/report/note） |
| `knowledge_source` | VARCHAR(32) | DEFAULT 'knowledge-platform' | |
| `bound_at` | DATETIME(6) | NOT NULL | 绑定时间 |

### 4.6 表：`validated_knowledge_versions`（知识版本溯源表）

| 列名 | MySQL 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | CHAR(36) | PK | |
| `version_id` | CHAR(36) | FK → role_versions.id, INDEX | 关联角色版本 |
| `knowledge_object_id` | VARCHAR(256) | NOT NULL | 知识对象标识 |
| `knowledge_version_id` | VARCHAR(128) | NOT NULL | 知识版本标识 |

### 4.7 表：`test_run_records`（测试记录表）

| 列名 | MySQL 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | CHAR(36) | PK | |
| `role_id` | CHAR(36) | FK → role_assets.id, INDEX | 测试的角色 |
| `version_id` | CHAR(36) | FK → role_versions.id | 测试时的版本 |
| `test_input` | TEXT | NOT NULL | 测试问题 |
| `test_output` | TEXT | NOT NULL | 角色回复 |
| `knowledge_retrieved` | JSON | | 检索到的知识摘要 |
| `human_rating` | TINYINT | CHECK 1-5 | 人工评分 |
| `tested_at` | DATETIME(6) | NOT NULL | 测试时间 |

---

## 五、Pydantic 数据模型分层

### 5.1 三层模型约定

```
DB Model（SQLAlchemy）     →  数据库映射
      ↓
Domain Model（Pydantic）   →  业务逻辑层（含校验）
      ↓
API Schema（Pydantic）     →  请求/响应序列化（区分公开/内部字段）
```

### 5.2 关键 Domain Model 示例

```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum

class RoleStatus(str, Enum):
    DRAFT = "draft"
    TEST = "test"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Layer(str, Enum):
    """角色 5 层模型"""
    L1_IDENTITY = "L1"
    L2_MIND = "L2"
    L3_KNOWLEDGE = "L3"
    L4_CAPABILITY = "L4"
    L5_CONFIG = "L5"

class RoleAsset(BaseModel):
    id: UUID
    name: str = Field(min_length=1, max_length=128)
    bio: str = Field(min_length=1, max_length=512)
    tags: list[str] = []
    status: RoleStatus = RoleStatus.DRAFT
    current_version_id: UUID | None = None
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime

class RoleVersionField(BaseModel):
    version_id: UUID
    layer: Layer
    field_name: str
    field_value: dict | str | list  # JSON value

class ModelBinding(BaseModel):
    """L5 配置层 — 模型绑定"""
    model_provider: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    temperature: float = Field(default=0.7, ge=0, le=2.0)
    max_tokens: int = Field(default=4096, gt=0)
    fallback_enabled: bool = False

class KnowledgeRef(BaseModel):
    id: UUID
    role_id: UUID
    knowledge_id: str
    title: str | None = None
    type: str | None = None
    knowledge_source: str = "knowledge-platform"
    bound_at: datetime

class ValidatedKnowledgeVersion(BaseModel):
    """上位裁决后的最小追溯结构"""
    knowledge_object_id: str
    knowledge_version_id: str

class TestRunRecord(BaseModel):
    id: UUID
    role_id: UUID
    version_id: UUID
    test_input: str
    test_output: str
    knowledge_retrieved: list[dict] | None = None
    human_rating: int | None = Field(default=None, ge=1, le=5)
    tested_at: datetime
```

### 5.3 API Schema — 与公共契约对齐

```python
class RoleListPublicResponse(BaseModel):
    """GET /role-assets?status=published — 角色列表公开响应"""
    # 必需
    role_id: UUID = Field(alias="id")
    role_version_id: UUID = Field(alias="current_version_id")
    role_name: str = Field(alias="name")
    summary: str                       # 计算字段：bio 截断
    model_binding: ModelBinding
    # 可选
    knowledge_refs: list[KnowledgeRef] | None = None
    identity_background: str | None = None
    point_of_view: str | None = None
    decision_style: str | None = None
    responsibility_boundary: str | None = None
    validated_knowledge_versions: list[ValidatedKnowledgeVersion] | None = None
    # 双边局部扩展（不进公共字段集）
    has_test_record: bool = False
    latest_test_rating: int | None = None
    latest_tested_at: datetime | None = None
    test_run_count: int = 0
    publish_confirmed_by: str | None = None

class RoleVersionDetailResponse(BaseModel):
    """GET /role-versions/{role_version_id} — 版本详情"""
    # 必需
    role_id: UUID
    role_version_id: UUID
    summary: str
    model_binding: ModelBinding
    # 可选
    identity_background: str | None = None
    point_of_view: str | None = None
    decision_style: str | None = None
    responsibility_boundary: str | None = None
    speaking_style: str | None = None
    knowledge_refs: list[KnowledgeRef] | None = None
    validated_knowledge_versions: list[ValidatedKnowledgeVersion] | None = None
    # 局部扩展
    has_test_record: bool = False
    latest_test_rating: int | None = None
    latest_tested_at: datetime | None = None
    test_run_count: int = 0
    publish_confirmed_by: str | None = None
```

---

## 六、外部 API 对接架构

### 6.1 知识平台（Dify）

```
角色产品                    Dify API
  │                           │
  │ GET /api/v1/datasets/{id}/documents?metadata[status]=reviewed
  ├──────────────────────────→│  接口 1：知识对象列表查询
  │←──────────────────────────┤
  │                           │
  │ GET /api/v1/datasets/{id}/documents/{doc_id}
  ├──────────────────────────→│  接口 2：知识内容获取
  │←──────────────────────────┤
  │                           │
  │ POST /api/v1/datasets/{id}/retrieval
  ├──────────────────────────→│  接口 3：知识检索（RAG）
  │←──────────────────────────┤
  │                           │
  │ 接口 4 版本标识：待知识平台确认方案
  │                           │
```

### 6.2 LLM 调用（角色测试用）

角色测试时需要调用 LLM 获取角色的实际回复，请求结构：

```python
# 角色测试请求
{
    "model": model_binding.model_name,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": test_input}
    ],
    "temperature": model_binding.temperature,
    "max_tokens": model_binding.max_tokens
}
```

其中 `system_prompt` 由角色 5 层模型拼接生成：
1. L1：`你是{role_name}，{bio}`
2. L2：`你的背景是...，你的立场是...，你的决策风格是...`
3. L3：从知识平台检索到的相关知识 chunk 注入
4. L4：`你可以使用以下工具：...`

### 6.3 决策产品（消费侧）

角色产品只暴露 3 个本地接口，决策产品 API 直连消费。角色产品不调用决策产品 API。

---

## 七、工程目录结构

```
virtual-actor/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 环境变量 / 配置
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── role_asset.py    # RoleAsset ORM
│   │   ├── role_version.py  # RoleVersion + RoleVersionField ORM
│   │   ├── knowledge_ref.py # KnowledgeRef ORM
│   │   └── test_run.py      # TestRunRecord ORM
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── role.py          # RoleAsset Domain + API Schemas
│   │   ├── version.py       # RoleVersion Schemas
│   │   ├── knowledge.py     # KnowledgeRef Schemas
│   │   └── test_run.py      # TestRun Schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── role_service.py      # 角色 CRUD + 状态迁移
│   │   ├── version_service.py   # 版本管理 + 发布逻辑
│   │   ├── knowledge_service.py # 知识平台 API 调用
│   │   ├── llm_service.py       # LLM 调用
│   │   └── test_service.py      # 测试运行逻辑
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── role_assets.py   # 角色 CRUD 路由
│   │   ├── role_versions.py # 版本路由
│   │   └── role_test.py     # 测试路由
│   └── utils/
│       ├── __init__.py
│       └── prompt_builder.py # system prompt 构建
├── data/                    # 本地文件存储（测试记录、导出文件）
├── migrations/              # Alembic 迁移文件
├── tests/                   # pytest 测试
├── docs/                    # 设计文档
├── prototype/               # UI 原型
├── requirements.txt
├── alembic.ini
└── .env.example
```

---

## 八、MVP vs 后续迭代

| 能力 | MVP（当前阶段） | 后续 |
|------|-------------|------|
| 数据库 | MySQL 8.0（Docker 本地） | 云数据库（腾讯云 CDB） |
| 知识 Dify 对接 | 接口 1 + 接口 3（RAG） | 接口 2 + 接口 4 |
| 版本管理 | 单版本草稿 + 发布 | 多版本分支、版本对比 |
| 角色测试 | 单次输入→输出 | 批量测试、回归测试 |
| 前端 | 原型 HTML 直接使用 | 前后端分离（React） |
| 部署 | 本地 uvicorn 运行 | Docker Compose + 云部署 |
| 导出 | 无 | CSV/JSON 导出 |
| 权限 | 无 | 认证 + 权限 |

---

## 九、待确认项

1. ~~SQLite 能否满足 MVP 需求？~~ → **MySQL 8.0（Docker 本地，已启动）**
2. **MySQL 连接信息**（host/port/user/password/database name）是否需要现在配置？
3. **前端框架**：原型 HTML 暂不拆分，保持简洁。确认后是否需要启动前后端分离？
4. **LLM API**：角色测试用的 LLM 服务商（OpenAI / Anthropic / 本地 Ollama）是否有偏好？