# v0.4.0 研究结论

> 版本：v0.4.0
> Formal Status：Draft
> 最后更新：2026-05-25
> 用途：基于 `research-brief.md` 的研究框架和初始假设，补充深度竞品分析、治理缺口识别、资产属性建模和范围决策建议，供规划方复审后冻结 v0.4.0 实现范围
> 前置文档：`research-brief.md`

---

## 1. v0.3.0 已建能力与限制复盘

### 1.1 已建能力基线

v0.3.0-commercial-trial 已通过 Accepted 验收，形成 7 项可追溯能力：

| 能力 | 实现形态 | 追溯证据 | 资产意义 |
|---|---|---|---|
| 角色五层配置 | RoleAsset + RoleVersion + RoleVersionField (EAV) | US-02 / U01 / H02 | 结构化角色定义，可版本化 |
| 知识绑定 | KnowledgeRef + 文件级选择 + kb_id 去重检索 | US-02 / U01 / H02 | 角色的专业知识来源和边界 |
| 角色测试 | TestService + KnowledgePlatformService + LLMService + PromptBuilder | US-03 / U02 / H03 | 角色质量的验证入口 |
| 人工评分 | 1-5 星评分 + 评分历史展示 | US-03 / U02 / H03 | 质量反馈信号 |
| 发布与版本 | 不可覆写 RoleVersion + ValidatedKnowledgeVersion | US-04 / U03 / H04 | 可复用、可追溯的资产版本 |
| 编辑已发布角色 | fork 新草稿 + 旧版本保持 published | US-05 / U04 / H05 | 资产演进和版本并存 |
| React + Docker Compose | HashRouter 5 页面 + FastAPI 托管 dist + MySQL 8 + Alembic | H01-H05 全链路 | 最终用户交付形态 |

### 1.2 核心限制（影响 v0.4 方向判断）

| 限制 | 说明 | 对商业定位的影响 |
|---|---|---|
| 角色缺少资产治理属性 | 无分类、所有者、适用场景、可见范围、使用权限和复用方式 | 角色仍是"配置对象"，不是"企业资产" |
| 角色只有测试台，没有正式使用台 | 测试记录和正式使用场景未区分，发布后仍只在测试页操作 | 无法形成"使用"闭环，角色被发布后缺乏使用入口 |
| 角色发布后如何被他人/他系统使用无产品级设计 | 当前只有管理侧内部 API，无面向消费方的产品入口 | 无法支撑资产分发和调用场景 |
| 知识边界声明（L3 knowledge_boundary）未填入 | RoleCreate/RoleUpdate/RoleDetail schema 中无此字段定义；前端类型和 UI 也无此字段；仅 role_service.py LAYER_MAP 有映射声明，但 _save_fields 不遍历此字段，数据库层也不会写入 | 角色无法表达"我知道什么 / 我不知道什么" |
| 能力边界声明（L4 capability_boundary）已完整暴露 | RoleCreate/RoleUpdate/RoleDetail schema 已有此字段；创建/编辑页有 textarea 输入；详情页已展示；数据库通过 EAV 写入 | 已满足基本填写和展示，但可做资产化展示和语义强化 |
| 角色列表和详情页缺少中文枚举映射 | status / layer 等枚举显示英文原始值 | 降低中文用户的理解效率 |
| 历史版本只能看版本号列表，无详情入口 | 版本列表页缺失 | 无法回溯角色演进历程 |

---

## 2. 市场竞品深度分析

### 2.1 分析框架

对 7 类产品进行结构化对比，重点评估它们在"角色定义"、"知识绑定"、"质量验证"、"版本治理"和"资产分发"五个维度上的覆盖程度。

### 2.2 竞品能力矩阵

| 维度 | CrewAI | OpenPersona | FastGPT | Open WebUI | Coze/Dify/百炼 | MS Copilot Studio | Character.AI |
|---|---|---|---|---|---|---|---|
| **角色定义结构** | role + goal + backstory + tools + llm (YAML) | Soul (4 层: personaName/bio/personality/speakingStyle/constitution) | name + type + system prompt (flat) | Model(id/name/base_model/params/meta) | name + prompt + plugins (flat) | name + instructions + actions + knowledge (flat) | name + description + greeting (flat) |
| **知识绑定** | knowledge_sources (文件级, 无版本) | Cognition (会话记忆, 无文档知识) | Dataset + Collection + Vector (强, 无角色绑定) | Knowledge + KnowledgeFile + AccessGrants (强, 无版本追踪) | 知识库挂载 (无版本, 无角色专属边界) | 企业知识源连接 (无角色版本关联) | 无 |
| **知识版本追踪** | 无 | 无 | schema version 标记 (非内容版本) | 无 | 无 | 无 | 无 |
| **质量验证** | CLI training (质量分数 0-10, 非门禁) | 3 gate (生成/安装/运行, 非结构化验收) | 单点搜索测试 + 应用评估 (非门禁) | 无 | 预览调试 (非门禁) | 测试面板 (非门禁) | 社区评分 (非门禁) |
| **发布门禁** | 无 | 无 | 无 | 无 | 无 | 无 | 无 |
| **版本生命周期** | 无 (覆盖更新) | Fork + Lineage (推导追踪, 无状态机) | updateTime (无版本) | is_active (无状态机) | 无 | 无 | 无 |
| **资产分发/调用** | Agent Repository + A2A protocol | skills.sh + ClawHub | iframe 分享 + OpenAPI | Community hub + Pipeline + RBAC | API 发布 + Bot 分发 | Copilot 嵌入 + Connector | Marketplace |
| **多角色协作** | Sequential + Hierarchical + A2A delegation | 无 | 无 | Many Models Conversations (非协作编排) | Workflow 多节点 (非角色治理) | Agent handoff | Group chat (非结构化) |

### 2.3 关键发现

1. **市场不缺 Agent Builder，缺角色资产治理产品。** 在当前抽样竞品中，所有产品都以"创建一个应用/Bot/Agent"为核心交互，角色只是运行时配置，不是被治理的企业资产。
2. **知识绑定是当前抽样竞品普遍的薄弱环节。** 只有 FastGPT 和 Open WebUI 有较强的知识基础设施，但都不支持"角色专属知识边界 + 版本追踪 + 过期检测"。
3. **质量门禁在当前抽样竞品中普遍缺失。** 当前抽样竞品的"测试"均为调试性质，没有 draft → test → published 的正式门禁流程。
4. **版本生命周期是当前抽样竞品中最大的缺口。** 除 OpenPersona 的 Fork/Lineage 有推导追踪外，当前抽样竞品均没有完整的版本状态机 (draft/test/published/archived) + 不可覆写版本 + 知识版本追溯。
5. **CrewAI 的 Agent Repository + A2A 是最接近的企业级方案。** 但它仍缺版本治理、质量门禁和知识绑定追踪。virtual-actor 应关注 A2A 协议兼容性作为未来互操作方向。
6. **FastGPT 是知识基础设施的最强参考。** 其 Dataset/Collection/Vector/chunk 模式值得 virtual-actor 在知识层设计时参考，但 virtual-actor 的差异在于知识绑定到角色而非全局到应用。
7. **Microsoft Agent Framework (MAF) 是企业 Agent 的方向标。** 声明式 YAML Agent + Foundry 托管 + A2A 兼容 + workflow 模式代表了市场走向。virtual-actor 应考虑未来与 MAF/A2A 的互操作兼容。

### 2.4 竞品能力矩阵证据链

以下为 §2.2 竞品能力矩阵中各项判断的官方来源证据。

#### CrewAI

| 判断项 | 证据来源 | 证据要点 |
|---|---|---|
| role + goal + backstory + tools + llm (YAML) | [CrewAI Agents 官方文档](https://docs.crewai.com/concepts/agents) + [GitHub 源码 agents.mdx](https://github.com/crewAIInc/crewAI/blob/main/docs/en/concepts/agents.mdx) | Agent 属性表明确列出 `role`, `goal`, `backstory`, `llm`, `tools`, `knowledge_sources` 参数；YAML 配置示例 `agents.yaml` 展示 role/goal/backstory 三字段结构 |
| knowledge_sources (文件级, 无版本) | [CrewAI Knowledge 官方文档](https://docs.crewai.com/concepts/knowledge) + [GitHub 源码 knowledge.mdx](https://github.com/crewAIInc/crewAI/blob/main/docs/en/concepts/knowledge.mdx) + [knowledge.py 源码](https://github.com/crewAIInc/crewAI/blob/main/lib/crewai/src/crewai/knowledge/knowledge.py) | `knowledge_sources` 参数在 Agent/Crew 层挂载，支持 String/CSV/PDF/JSON/Text 等文件级来源；知识存储基于 ChromaDB/Qdrant 向量库，无版本追踪机制 |
| Agent Repository + A2A protocol | [CrewAI Agent Repositories 官方文档](https://docs.crewai.com/enterprise/features/agent-repositories) + [GitHub 源码 agent-repositories.mdx](https://github.com/crewAIInc/crewAI/blob/main/docs/en/enterprise/features/agent-repositories.mdx) + [A2A Agent Delegation 文档](https://docs.crewai.com/learn/a2a-agent-delegation) + [A2A on AMP 文档](https://docs.crewai.com/enterprise/features/a2a) + [GitHub 源码 a2a-agent-delegation.mdx](https://github.com/crewAIInc/crewAI/blob/main/docs/en/learn/a2a-agent-delegation.mdx) + [GitHub 源码 a2a.mdx](https://github.com/crewAIInc/crewAI/blob/main/docs/en/enterprise/features/a2a.mdx) | Agent Repositories 支持 `from_repository` 参数加载预定义 agent 定义并共享复用；A2A 协议作为一等委派原语，Agent 可配置 `A2AClientConfig`/`A2AServerConfig` 进行跨 Agent 委派和服务暴露；AMP 平台提供分布式状态、企业认证、gRPC 传输 |
| Sequential + Hierarchical + A2A delegation | 同上 A2A 文档 | Process 支持 Sequential/Hierarchical 模式；A2A 协议支持 Agent-to-Agent 委派 |

#### OpenPersona (acnlabs/OpenPersona)

| 判断项 | 证据来源 | 证据要点 |
|---|---|---|
| Soul 4 层结构 (personaName/bio/personality/speakingStyle/constitution) | [OpenPersona GitHub README](https://github.com/acnlabs/OpenPersona/blob/main/README.md) | 明确声明 4+5+3 架构：四层为 **Soul / Body / Faculty / Skill**；Soul 层包含 `persona.json`（身份定义）+ `state.json`（动态演化）+ `soul/` 目录（`injection.md`, `constitution.md`, `lineage.json`, `self-narrative.md`）；`constitution.md` 基于五条公理 Purpose/Honesty/Safety/Autonomy/Hierarchy，不可被单个 persona 覆盖 |
| Fork + Lineage (推导追踪, 无状态机) | [OpenPersona GitHub README](https://github.com/acnlabs/OpenPersona/blob/main/README.md) | Persona Fork 功能："Derive a specialized child persona from any installed parent, inheriting constraint layer while starting fresh on runtime state"；`lineage.json` 存在于 `soul/` 目录中追踪 fork 溯源；但无 draft/test/published/archived 状态机 |
| 3 gate (生成/安装/运行) | [OpenPersona GitHub README](https://github.com/acnlabs/OpenPersona/blob/main/README.md) | 明确声明三闸门：Generate Gate（拒绝无效声明）、Install Gate（验证 constitution 完整性）、Runtime Gate（演化边界运行时约束）；但这些闸门是约束验证而非质量验收门禁 |
| skills.sh + ClawHub | [OpenPersona GitHub README](https://github.com/acnlabs/OpenPersona/blob/main/README.md) | Skill 层支持外部 skills.sh (`install` 字段)；默认集成 [OpenClaw](https://github.com/openclaw/openclaw) 和 ClawHub；A2A agent card 生成 `agent-card.json` 和 `acn-config.json` |
| Cognition (会话记忆, 无文档知识) | [OpenPersona GitHub README](https://github.com/acnlabs/OpenPersona/blob/main/README.md) | Faculty 层 Cognition 维度为 memory（跨会话记忆），支持 Mem0/Zep/local 插件；有 `persona-knowledge` companion skill 提供 MemPalace + Knowledge Graph，但 Cognition 本身无文档级知识绑定 |

#### FastGPT

| 判断项 | 证据来源 | 证据要点 |
|---|---|---|
| Dataset + Collection + Vector (强, 无角色绑定) | [FastGPT GitHub schema.ts](https://github.com/labring/FastGPT/blob/main/packages/service/core/dataset/schema.ts) + [collection/schema.ts](https://github.com/labring/FastGPT/blob/main/packages/service/core/dataset/collection/schema.ts) + [FastGPT README](https://github.com/labring/FastGPT/blob/main/README.md) | `MongoDataset` 模型包含 `parentId`, `teamId`, `type`, `name`, `vectorModel`, `chunkSettings` 等字段；`MongoDatasetCollection` 模型包含 `datasetId`, `type`, `name`, `fileId`, `rawTextLength`, `hashRawText` 及 chunkSettings 嵌套；知识通过 Dataset (顶层) → Collection (文件集合) → Data/Chunk (向量段) 三级组织；但 Dataset 绑定到 teamId 而非角色 |
| schema version 标记 (非内容版本) | [FastGPT GitHub schema.ts](https://github.com/labring/FastGPT/blob/main/packages/service/core/dataset/schema.ts) | Dataset schema 有 `updateTime` 字段（无版本号）；Collection 有 `createTime`/`updateTime`；知识结构依赖 MongoDB ObjectId 而非显式版本追踪 |
| 单点搜索测试 + 应用评估 (非门禁) | [FastGPT GitHub README](https://github.com/labring/FastGPT/blob/main/README.md) | README 功能列表明确列出 "知识库单点搜索测试" 和 "应用评测" 为核心功能；但两者是调试/验证工具，不是 draft→test→published 发布门禁 |
| iframe 分享 + OpenAPI | [FastGPT GitHub README](https://github.com/labring/FastGPT/blob/main/README.md) | README 列出 "completions 接口 (chat 模式对齐 GPT 接口)"、"知识库 CRUD"、"对话 CRUD"、"自动化 OpenAPI 接口" |

#### Open WebUI

| 判断项 | 证据来源 | 证据要点 |
|---|---|---|
| Knowledge + KnowledgeFile + AccessGrants (强, 无版本追踪) | [Open WebUI GitHub knowledge.py](https://github.com/open-webui/open-webui/blob/main/backend/open_webui/models/knowledge.py) | `Knowledge` ORM 模型包含 `id`, `user_id`, `name`, `description`, `meta`, `created_at`, `updated_at`；`KnowledgeFile` ORM 模型包含 `id`, `knowledge_id` (FK→knowledge.id), `file_id` (FK→file.id), `user_id`, `created_at`, `updated_at`，有 `uq_knowledge_file_knowledge_file` 唯一约束；`KnowledgeModel` Pydantic 模型包含 `access_grants: list[AccessGrantModel]` 字段实现访问控制；无版本追踪字段 |
| Model(id/name/base_model/params/meta) | [Open WebUI GitHub](https://github.com/open-webui/open-webui) | 角色定义通过 Model 对象承载，Model 为 flat 结构（id + name + base_model + params + meta），无分层定义 |
| Community hub + Pipeline + RBAC | [Open WebUI GitHub knowledge.py](https://github.com/open-webui/open-webui/blob/main/backend/open_webui/models/knowledge.py) | `AccessGrants` 支持按 resource_type='knowledge' 的 read/write 权限控制，支持用户组级授权；`search_knowledge_bases` 方法集成 `has_permission_filter` 实现权限过滤 |

#### Microsoft Agent Framework (MAF) / Copilot Studio

| 判断项 | 证据来源 | 证据要点 |
|---|---|---|
| 声明式 Agent YAML | [MAF GitHub README](https://github.com/microsoft/agent-framework/blob/main/README.md) + [FoundryAgent.yaml](https://github.com/microsoft/agent-framework/blob/main/declarative-agents/agent-samples/foundry/FoundryAgent.yaml) + [AzureOpenAI.yaml](https://github.com/microsoft/agent-framework/blob/main/declarative-agents/agent-samples/azure/AzureOpenAI.yaml) | README 明确列出 "Declarative Agents: Define agents using YAML for faster setup and versioning"；`FoundryAgent.yaml` 示例展示 `kind: Prompt`, `name`, `description`, `instructions`, `model` (id/options/connection) 结构；declarative-agents 目录包含 agent-samples (foundry/azure/openai) 和 workflow-samples (CustomerSupport/DeepResearch/Marketing) |
| Foundry 托管 | [MAF GitHub README](https://github.com/microsoft/agent-framework/blob/main/README.md) + [Foundry hosted agents 目录](https://github.com/microsoft/agent-framework/tree/main/python/samples/04-hosting/foundry-hosted-agents) | README 列出 "Foundry Hosted Agents (new): Deploy and host your agents to Foundry-hosted infrastructure with just 2 additional lines of code"；FoundryChatClient 通过 AzureCliCredential + project_endpoint + model 配置连接 Foundry 托管服务 |
| A2A 兼容 | [MAF GitHub A2A samples](https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/02-agents/A2A) + [Agent_With_A2A sample](https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/02-agents/AgentProviders/Agent_With_A2A) | .NET samples 目录包含 A2A 子目录：`A2AAgent_AsFunctionTools`, `A2AAgent_PollingForTaskCompletion`, `A2AAgent_ProtocolSelection`, `A2AAgent_StreamReconnection`；Agent 可配置 A2A 协议与其他 Agent 交互 |
| Agent handoff | [MAF GitHub README](https://github.com/microsoft/agent-framework/blob/main/README.md) | Orchestration Patterns 支持 "sequential, concurrent, handoff, and group collaboration patterns"；workflow samples 展示 handoff 模式 |

#### Coze / Dify / 百炼

| 判断项 | 证据来源 | 证据要点 |
|---|---|---|
| Coze: 知识库挂载 (无版本, 无角色专属边界) | [Coze Python SDK bots/__init__.py](https://github.com/coze-dev/coze-py/blob/main/cozepy/bots/__init__.py) + [Coze bot_create.py 示例](https://github.com/coze-dev/coze-py/blob/main/examples/bot_create.py) | `BotKnowledge` Pydantic 模型包含 `dataset_ids: List[str]` 和 `auto_call: bool`、`search_strategy: int`；知识库通过 dataset_ids 挂载到 Bot，是全局知识库引用而非角色专属绑定；无版本追踪字段 |
| Coze: API 发布 + Bot 分发 | [Coze Python SDK bot_publish.py](https://github.com/coze-dev/coze-py/blob/main/examples/bot_publish.py) + [Coze SDK README](https://github.com/coze-dev/coze-py/blob/main/README.md) | SDK 提供 `coze.bots.create`, `coze.bots.publish`, `coze.bots.retrieve` 方法；`PublishStatus` 枚举支持 `published_online`, `published_draft`, `unpublished_draft`；Bot 通过 API/chat 接口分发 |
| Coze: name + prompt + plugins (flat) | [Coze Python SDK bots/__init__.py](https://github.com/coze-dev/coze-py/blob/main/cozepy/bots/__init__.py) | `BotPromptInfo` 包含 `prompt: str`；`BotModelInfo` 包含 `model_id`, `temperature`, `max_tokens` 等；`PluginIDList` 通过 plugin_id 挂载；角色定义为 flat prompt + plugins 组合，无分层结构 |
| Dify: 知识库挂载 (无版本, 无角色专属边界) | [Dify GitHub dataset.py](https://github.com/langgenius/dify/blob/main/api/models/dataset.py) + [Dify README](https://github.com/langgenius/dify/blob/main/README.md) | `Dataset` ORM 模型绑定 `tenant_id` (组织级) 而非角色级；`Document` 模型通过 `dataset_id` FK 关联；知识通过 workflow 的 knowledge-retrieval 节点挂载到应用，而非角色专属绑定；无版本追踪 |
| 百炼: 知识库挂载 + Bot 分发 | [阿里云百炼帮助文档](https://help.aliyun.com/zh/model-studio/) | 百炼 (Model Studio) 提供知识库管理 + Agent 应用创建 + API 发布功能，知识库为全局组织级资源，Agent/Bot 通过 prompt + 知识库引用 + 工具挂载组合定义，无角色版本追踪 |

#### 核心判断证据

| 判断 | 证据要点 |
|---|---|
| "市场不缺 Agent Builder，缺角色资产治理产品" | 以上 6 类竞品的核心交互均围绕"创建一个应用/Bot/Agent"：CrewAI 以 Crew + Flow 为编排单位、OpenPersona 以 persona pack 为运行单位、FastGPT 以应用(App)为分发单位、Open WebUI 以 Model 为聊天对象、Coze/Dify 以 Bot/App 为分发单位、MAF 以 Agent+Workflow 为生产单位。在当前抽样竞品中，角色/Agent 均为运行时配置，而非被治理的企业资产——无分类/所有者/适用场景/可见范围/使用权限等资产治理属性 |

### 2.5 virtual-actor 的差异化定位

| 差异维度 | 竞品现状 | virtual-actor 已建能力 | 差异空间 |
|---|---|---|---|
| 版本状态机 | 无竞品有完整状态机；OpenPersona 有 Fork/Lineage 推导追踪但无状态机（证据：§2.4 OpenPersona 证据链） | draft/test/published/archived + 不可覆写版本 | **相对优势**：在当前抽样竞品中，唯一具备完整版本状态机和不可覆写机制的方案；需扩展为资产治理 |
| 知识版本追溯 | 当前抽样竞品均不支持知识内容版本追踪；CrewAI/FastGPT/Open WebUI 均无版本字段（证据：§2.4 各竞品证据链） | KnowledgeRef + ValidatedKnowledgeVersion | **相对优势**：在当前抽样竞品中，唯一将知识版本与角色版本绑定的方案；需扩展过期检测和边界声明 |
| 质量门禁 | 当前抽样竞品的测试均为调试性质而非发布门禁（证据：§2.4 各竞品质量验证行） | 发布前测试记录检查 | **相对优势**：在当前抽样竞品中，唯一将测试结果作为发布前置条件的方案；需扩展评分门禁和确认人 |
| 角色结构化定义 | 多为 flat prompt（CrewAI YAML 3字段、FastGPT/Coze flat prompt，证据：§2.4 各竞品证据链）；OpenPersona 有 4 层 Soul 但侧重行为约束而非企业治理 | 5 层 EAV 字段模型 | **相对优势**：在当前抽样竞品中，唯一采用多层结构化定义模型；需补 knowledge_boundary 全链路和 capability_level 标注 |
| 资产治理属性 | 当前抽样竞品均未将角色作为企业资产治理（证据：§2.4 各竞品证据链 — 无分类/所有者/业务域字段） | 无 | **缺口**，需补分类、所有者、适用场景 |
| 正式使用入口 | 当前抽样竞品均只有调试/测试入口，无正式使用记录区分（证据：§2.4 各竞品质量验证行） | 只有测试台 | **缺口**，需补使用台和使用记录 |
| 被其他系统调用 | CrewAI 有 A2A 协议和 Agent Repository（证据：§2.4 CrewAI 证据链）；MAF 有 A2A 兼容（证据：§2.4 MAF 证据链）；其余为 API 直连或分享链接 | 管理侧 API | **缺口**，需补消费侧入口设计；同时需关注 A2A 互操作方向 |

**结论：virtual-actor 在版本治理、知识追溯和质量门禁上相比所分析竞品具有结构性优势（完整状态机 + 不可覆写版本 + 发布门禁），但在资产治理属性、正式使用入口和被系统调用三个维度存在缺口。CrewAI 的 A2A 和 Agent Repository 以及 MAF 的 A2A 兼容性是未来互操作的关键参考。v0.4 应优先补这三个缺口。**

---

## 3. 集团企业"角色资产产品"的真实需求

### 3.1 目标用户分层

| 用户层 | 角色 | 核心需求 | 使用方式 |
|---|---|---|---|
| 角色管理者 | 知识运营 / AI 产品经理 / 部门负责人 | 创建、配置、测试、发布、维护角色资产 | 创建 / 编辑 / 测试 / 发布流程 |
| 角色使用者 | 一线员工 / 业务人员 / 管理层 | 选择已发布角色进行问答、分析、获取专业建议 | 使用台 / 资产目录 |
| 业务系统集成者 | IT / 产品 / 平台团队 | 让角色资产被业务流程或决策产品调用 | API / 嵌入 / 事件通知 |
| 角色治理者 | 合规 / 风控 / 管理层 | 监督角色资产的质量、边界、权限和生命周期 | 治理看板 / 审计 |

### 3.2 典型场景与商业价值

| 场景 | 问题 | 角色资产如何解决 | 商业价值 |
|---|---|---|---|
| 专家经验分散 | 专业判断依赖个人，人员变动导致知识流失 | 角色绑定特定领域知识库，经验被固化为可复用资产 | 降低知识流失风险，提高复用率 |
| 业务决策缺多视角 | 单一视角导致决策盲区 | 多角色（财务/法务/风控/业务）提供结构化多视角建议 | 提升决策质量，降低风险 |
| 制度和流程查询难 | 制度文档分散、更新频繁、查询耗时 | 制度专家角色绑定制度知识库，实时检索和解释 | 降低制度查询成本，提高合规性 |
| 角色质量无法验证 | AI 回复准确性无法保证 | 测试 + 评分 + 发布门禁形成质量闭环 | 提升信任度，降低幻觉风险 |
| 角色资产无法追溯 | 不知道角色基于什么知识、什么版本、谁发布的 | 版本追溯 + 知识版本追溯 + 发布确认人 | 支撑审计和合规要求 |

### 3.3 用户场景推导（从场景到 Scope 的推导链）

以下 4 个集团企业真实用户场景推导出 v0.4 Scope In 的各项需求。每个场景包含用户角色、任务、痛点、角色资产参与方式、输入输出和成功标准。

#### 场景 SC-01：部门负责人创建并发布经营分析角色

- **用户**：集团财务部负责人（角色管理者）
- **任务**：创建一个经营分析角色，绑定经营分析知识库，测试其准确性后发布给全集团使用
- **当前痛点**：角色创建后只有"测试台"，发布后仍需在测试页操作；角色没有分类和所有者信息，其他部门不知道这个角色属于谁、覆盖什么业务域；角色无法声明"我知道什么 / 我不知道什么"
- **角色资产参与**：
  - 创建时填写：分类（行业专家）、所有者（财务部负责人）、适用业务域（经营分析）、可见范围（公开）、knowledge_boundary（"仅覆盖集团经营分析口径，不含下属子公司独立核算数据"、capability_boundary 已有基础入口需语义强化）
  - 测试后发布：进入"使用台"而非继续停留在测试页
- **输入**：角色配置 + 知识库 + 边界声明
- **输出**：带治理属性的已发布角色 + 正式使用入口
- **成功标准**：
  1. 角色有分类、所有者、业务域、可见范围信息 → **推导出 DD-01**
  2. 创建时可填写 knowledge_boundary → **推导出 DD-02（knowledge_boundary 部分）**
  3. capability_boundary 在详情页有资产化语义展示（如"本角色能力边界：仅提供分析建议，不做经营决策"）→ **推导出 DD-02（capability_boundary 强化部分）**
  4. 发布后进入使用台，产生正式使用记录 → **推导出 DD-03**
  5. 角色可标注能力层级（A1 问答建议）→ **推导出 DD-05**

#### 场景 SC-02：一线业务人员使用已发布的制度顾问角色

- **用户**：集团一线业务人员（角色使用者）
- **任务**：在日常工作中查询制度条款、理解合规要求、获取操作指引
- **当前痛点**：已发布的角色只能在测试页操作，使用记录和测试记录混在一起，无法区分"正式使用"和"质量验证"；不知道角色基于哪个版本的制度知识
- **角色资产参与**：
  - 在"使用台"选择已发布的制度顾问角色
  - 使用时自动冻结 role_version_id，确保基于发布时的版本回答
  - 产生 usage_record（使用者、查询、回复、时间、role_version_id）
- **输入**：用户自然语言问题
- **输出**：基于特定版本知识的结构化回答 + 使用记录
- **成功标准**：
  1. 使用台与测试台可区分 → **推导出 DD-03**
  2. usage_record 冻结 role_version_id → **推导出 DD-03（usage_records 版本冻结）**
  3. 使用记录与测试记录在 UI 和数据层面区分 → **推导出 DD-03**

#### 场景 SC-03：合规部门追溯角色资产的知识来源和版本

- **用户**：合规部门审计人员（角色治理者）
- **任务**：追溯某个制度顾问角色当前使用的知识版本，确认其是否基于最新的制度文档
- **当前痛点**：角色详情页展示英文枚举值，中文用户难以理解；历史版本只能看版本号列表，无法查看版本内容差异
- **角色资产参与**：
  - 在角色详情页查看：所有者、维护人、分类、可见范围、knowledge_boundary
  - 查看 capability_level（当前能力层级 A1）
  - 查看历史版本列表和版本内容差异
  - 状态、层级等枚举显示中文
- **输入**：角色 ID
- **输出**：角色治理信息 + 知识版本追溯 + 版本演进历史
- **成功标准**：
  1. 详情页展示资产治理属性 → **推导出 DD-01**
  2. knowledge_boundary 可展示 → **推导出 DD-02**
  3. capability_level 可展示 → **推导出 DD-05**
  4. 历史版本详情可查看 → **推导出 DD-07**
  5. 枚举显示中文 → **推导出 DD-08**

#### 场景 SC-04：IT 平台团队评估角色资产的外部调用方案

- **用户**：集团 IT 平台团队（业务系统集成者）
- **任务**：评估已发布的角色资产如何被决策产品或其他业务系统调用
- **当前痛点**：只有管理侧内部 API，无面向消费方的产品入口；不知道角色发现、版本冻结、知识追溯如何传递给消费方
- **角色资产参与**：
  - 参考消费侧 API 设计说明文档
  - 了解角色发现、版本冻结、知识追溯、调用拓扑建议
- **输入**：当前管理侧 API + v0.4 设计说明文档
- **输出**：消费侧调用方案设计文档（REST API / MCP / 本地镜像建议）
- **成功标准**：
  1. 消费侧 API 设计说明文档完成 → **推导出 DD-04**
  2. 文档不改变已有接口，只提建议 → **Scope 约束：不新增公共契约**

#### 场景到 Scope 推导汇总

| 场景 | 推导出的 DD 项 | 说明 |
|---|---|---|
| SC-01 | DD-01, DD-02, DD-03, DD-05 | 角色管理者创建和发布角色的全流程需求 |
| SC-02 | DD-03 | 角色使用者正式使用角色的需求 |
| SC-03 | DD-01, DD-02, DD-05, DD-07, DD-08 | 角色治理者追溯和审计的需求 |
| SC-04 | DD-04 | 业务系统集成者评估调用方案的需求 |

未被场景推导出的 DD 项：

| DD 项 | 是否被推导 | 说明 |
|---|---|---|
| DD-06（模板库） | 未被上述 4 个场景推导 | 模板库未被真实用户场景推导，已移出 v0.4 Scope In；后续版本补足场景后重新评估 |
| DD-07（历史版本详情） | 被 SC-03 推导 | 治理追溯场景需要查看版本演进 |
| DD-08（枚举中文映射） | 被 SC-03 推导 | 合规审计人员需要中文界面 |

### 3.4 商业价值判断

角色资产产品的核心价值不是"创建更多 AI 聊天入口"，而是：

1. **把分散的专家经验固化为可治理的企业资产。**
2. **让决策过程可以获取结构化的多视角专业输入。**
3. **让 AI 角色的质量、边界和来源可以被验证和追溯。**
4. **让角色资产可以被授权、分发和复用，而不是只在创建者手中。**

---

## 4. 角色作为资产的属性、治理要求和生命周期

### 4.1 资产属性模型

基于竞品缺口和 v0.3 已建能力，角色资产应具备以下 8 组属性：

| 属性组 | v0.3 已覆盖 | v0.4 需补充 | 说明 |
|---|---|---|---|
| A1 身份 | name + bio + tags + avatar | 补适用业务域、角色分类 | 角色是谁、属于什么领域 |
| A2 专业边界 | L2 心智字段 (已有 schema) | 补 knowledge_boundary 全链路（schema/API/UI/详情展示）；capability_boundary 已有基础入口，做资产化展示和语义强化 | 角色负责什么、不负责什么 |
| A3 知识边界 | KnowledgeRef + ValidatedKnowledgeVersion | 补 knowledge_boundary schema/API/UI/详情展示；补知识过期检测 | 角色知道什么、不知道什么 |
| A4 能力边界 | L4 capability_boundary (schema/API/UI/详情页已有) | capability_boundary 已有基础入口，做资产化展示和语义强化；补 capability_level (A1/A2/A3) 标注 | 角色能做什么、不能做什么 |
| A5 模型配置 | ModelBinding | 不变 | 使用什么模型、参数和成本 |
| A6 质量证据 | test_runs + rating + publish_confirmed_by | 补评分门禁、质量状态聚合展示 | 角色质量是否经过验证 |
| A7 使用方式 | 无 | 补可见范围、使用入口、消费侧调用说明 | 谁能看、谁能用、怎么调用 |
| A8 治理信息 | 无 | 补资产所有者、维护人、归档策略 | 资产归属、维护责任、生命周期策略 |

### 4.2 治理要求

| 治理要求 | 说明 | v0.4 建议 |
|---|---|---|
| 发布门禁 | 角色发布前必须通过质量验证 | v0.3 已有测试记录检查；v0.4 补评分门禁 |
| 版本不可覆写 | 已发布版本不可被修改 | v0.3 已实现 |
| 知识版本追溯 | 发布时快照知识版本 | v0.3 已实现；v0.4 补过期检测 |
| 边界声明 | 角色必须声明知识边界和能力边界 | knowledge_boundary 全链路缺失（schema/API/UI/前端类型），v0.4 需补全链路；capability_boundary 全链路已存在，可做资产化展示和语义强化 |
| 所有者归属 | 角色资产有明确的所有者和维护人 | v0.4 新增 |
| 使用范围 | 角色发布后谁能看、谁能用 | v0.4 新增 |
| 归档策略 | 角色不再使用时如何归档 | v0.3 已有 archived 状态；v0.4 补归档说明 |

### 4.3 生命周期

v0.3 已实现的 4 状态机 (draft → test → published → archived) 在当前抽样竞品中具有相对优势（完整状态机 + 不可覆写版本），不需要增加额外状态。v0.4 应保持此状态机，但补充：

1. `is_deprecated` 标记的 UI 展示和业务语义（已过时但仍可查）。
2. 发布前的评分门禁（最低评分要求或确认人要求）。
3. 归档原因记录和归档后可见范围。

---

## 5. 从问答到执行的能力分层、风险边界和 v0.4 建议

### 5.1 三层能力模型

| 层级 | 能力 | 示例 | 风险等级 | 治理要求 | 是否适合 v0.4 |
|---|---|---|---|---|---|
| A1 问答建议 | 基于知识回答、分析、总结、提出建议 | 经营分析、制度问答、风险提示 | 低-中 (幻觉、边界不清) | 知识边界声明 + 质量验证 | **适合**，v0.3 已覆盖核心 |
| A2 生成产物 | 生成报告、方案、会议纪要、检查清单 | 复盘报告、整改清单、项目周报 | 中 (需人工确认、格式控制) | 产物确认流程 + 格式约束 + 责任声明 | **适合定义模型，谨慎实现** |
| A3 执行动作 | 调用工具或系统完成任务 | 创建工单、发起审批、更新状态 | 高 (权限、审计、失败影响、责任归属) | 工具权限 + 执行确认 + 操作日志 + 失败回滚 + 责任边界 | **不适合 v0.4 实现** |

### 5.2 v0.4 执行能力建议

1. **v0.4 不实现 A3 执行动作。** A3 涉及其他系统读写，必须先有公共契约或跨项目边界裁决。
2. **v0.4 定义 A1/A2/A3 能力模型和边界。** 在角色 L4 层标注当前角色处于哪个能力层级，在 UI 展示能力边界声明。
3. **A2 生成产物的实现留到后续版本评估。** v0.4 可以在 design-delta 中设计 A2 的产物确认流程和格式约束模型，但不进入实现。
4. **如果 A3 涉及决策产品或其他系统调用，只提出建议，不直接改接口。**

### 5.3 角色协作能力

| 协作模式 | 说明 | v0.4 建议 |
|---|---|---|
| independent | 角色独立运行，不被委派 | 已有 schema 字段，补 UI 入口 |
| delegatable | 角色可被其他角色或系统委派任务 | 只定义概念，不实现委派机制 |
| consult-only | 角色只提供咨询建议，不做决策 | 已有 schema 字段，补 UI 入口 |

---

## 6. 角色资产被员工、管理者、业务系统或决策产品使用的方式

### 6.1 四种使用方式

| 使用方式 | 当前状态 | v0.4 建议 | 优先级 |
|---|---|---|---|
| 人直接使用 | 只有测试台 | 升级为"使用台"，区分测试和使用记录 | **P0 — v0.4 必做** |
| 模板化复用 | 已有 4 个硬编码模板 | 保留但降为配套能力，不作为主线 | **P2 — 配套** |
| 嵌入业务流程 | 无 | 只做入口设计，不实现嵌入机制 | **P1 — 设计先行** |
| 被其他系统调用 | 只有管理侧 API | 补消费侧 API 说明文档，不改变接口 | **P1 — 设计先行** |

### 6.2 使用台 vs 测试台

当前 v0.3 的"测试台"混用了两个场景：验证角色质量（测试）和正式使用角色（使用）。v0.4 应区分：

| 维度 | 测试台 | 使用台 |
|---|---|---|
| 目的 | 验证角色质量，决定是否发布 | 正式使用已发布角色获取专业建议 |
| 可用条件 | 角色处于 test 状态 | 角色处于 published 状态 |
| 记录类型 | test_runs (测试记录) | usage_records (使用记录, v0.4 新概念) |
| 评分 | 人工评分 (1-5 星) | 使用反馈 (可选) |
| 对发布的影响 | 测试评分影响发布门禁 | 使用记录不影响发布门禁 |
| 谁使用 | 角色管理者 / 测试人员 | 角色使用者 (一线员工 / 管理层) |

### 6.3 被决策产品或其他系统调用

当前角色产品已有面向管理侧的 API (GET /role-assets, GET /role-versions/{id})。决策产品集成草案 §8 已提议了消费侧 API 路径，但明确标注为"消费侧建议范围，不是已冻结契约"。

v0.4 建议：

1. **不改变现有 API 接口。**
2. **产出一份消费侧 API 设计说明文档**，描述已发布角色如何被外部系统发现、选择和调用，包含：
   - 已发布角色列表获取方式
   - 角色 version_id 冻结和回放机制
   - 知识版本追溯如何传递给消费方
   - 调用拓扑建议 (REST API 直连 / MCP / 本地镜像) — 只提建议，不裁决
3. **如果消费侧设计涉及公共契约变更，必须先上提裁决，不直接实现。**

---

## 7. v0.4.0 推荐 Scope In / Scope Out、优先级、风险和验收标准

### 7.1 推荐主线定位

```text
v0.4.0 角色资产化与使用入口
```

主线不是"模板库版本"或"AI 创建版本"，而是把角色从配置对象升级为企业资产，并补上正式使用入口。

### 7.2 Scope In

| ID | 范围项 | 优先级 | 说明 |
|---|---|---|---|
| DD-01 | 角色资产治理属性 | P0 | 补资产分类、所有者/维护人、适用业务域、可见范围 |
| DD-02 | 边界声明填写入口 | P0 | 补 knowledge_boundary 和 capability_boundary 的 UI 填写和详情展示 |
| DD-03 | 正式使用台 | P0 | 区分测试台和使用台，published 角色进入使用台，产生使用记录 |
| DD-04 | 消费侧 API 设计说明 | P1 | 产出文档，不改变接口，描述角色资产如何被外部系统调用 |
| DD-05 | 执行能力模型定义 | P1 | 定义 A1/A2/A3 层级模型和边界，在 L4 标注能力层级，不实现 A2/A3 |
| DD-06 | 角色模板库 | 已移出 v0.4 Scope In | 未被真实用户场景推导，后续版本补足场景后重新评估 |
| DD-07 | 历史版本详情入口 | P2 | 低风险体验补齐 |
| DD-08 | 详情页枚举中文映射 | P2 | 低风险体验补齐 |

### 7.3 Scope Out

| 排除项 | 说明 |
|---|---|
| A3 执行动作的实现 | 风险高，需跨项目裁决，v0.4 不进入 |
| 决策产品集成实现 | 需另行立项和治理确认，不混入角色产品迭代 |
| 公共契约变更 | v0.4 不新增或修改公共契约字段，消费侧设计只提建议 |
| 跨项目读写边界变更 | 不改变知识平台当前依赖边界 |
| AI 辅助填充角色配置 | 当前不纳入，可作为后续版本候选 |
| 多角色协作编排 | 只定义概念，不实现委派或编排机制 |
| RBAC / 多租户 / SaaS | v0.3 Scope Out 继续生效 |

### 7.4 优先级与风险

| 优先级 | 范围项 | 风险 | 缓解措施 |
|---|---|---|---|
| P0 | 资产治理属性 | 低风险，补信息架构字段和 UI | 新增 schema 字段和 UI 组件，不改变已有模型 |
| P0 | 边界声明入口 | 低风险，暴露已有 schema 字段 | 不新增 schema，只补 UI 入口 |
| P0 | 正式使用台 | 中风险，区分 test/usage 记录 | 新增 usage_records 概念和 UI 路由，不改变 test_runs |
| P1 | 消费侧 API 说明 | 低风险，纯文档产出 | 不改接口，只提建议 |
| P1 | 执行能力模型定义 | 低风险，概念层定义 | 只补 L4 能力层级标注，不实现执行机制 |
| P2 | 模板库 | 低风险 | 保留现有硬编码模板，暂不扩展为动态模板库 |
| P2 | 版本详情 / 中文映射 | 极低风险 | 纯前端补齐 |

### 7.5 验收标准

| 标准 | 说明 |
|---|---|
| 1. Dossier 一致 | scope.md、design-delta.md、traceability.md 与研究结论一致 |
| 2. 资产治理属性可填写和展示 | 角色创建/编辑页和详情页支持分类、所有者、适用业务域、可见范围 |
| 3. 边界声明可填写和展示 | 角色创建/编辑页和详情页支持 knowledge_boundary 和 capability_boundary |
| 4. 使用台可用 | published 角色可在使用台被选择和使用，使用记录与测试记录区分 |
| 5. 消费侧 API 说明完成 | 文档覆盖角色发现、版本冻结、知识追溯和调用拓扑建议 |
| 6. 执行能力模型定义完成 | L4 层标注能力层级 (A1/A2/A3)，UI 展示能力边界 |
| 7. 质量闸门通过 | iteration-guard.py + markdownlint + pytest + frontend build |
| 8. 程序化场景链覆盖 | DD-01 至 DD-08 各有对应 U 和 H 场景链 |
| 9. 不越界 | 不新增公共契约、不实现 A3、不混入决策产品集成 |

### 7.6 停止条件

1. 资产治理属性、边界声明和使用台的实现偏离 design-delta，必须先回写 dossier。
2. 如果使用台需要新增读写接口或改变已有 API 路径，必须先回写 dossier。
3. 如果消费侧设计触发公共契约裁决要求，必须停止相关实现并上提。
4. 如果执行能力定义涉及工具权限或跨系统调用设计，必须先上提裁决。
5. 不得把 v0.4 任何 mock/stub/fixture 描述为真实集成证据。

---

## 8. 待裁决项

| 裁决项 | 说明 | 建议 |
|---|---|---|
| "角色资产"是否纳入公共对象 | 如果上位治理要求角色资产成为跨项目公共对象，v0.4 需调整字段设计 | 建议先作为角色产品内部概念，后续视裁决扩展 |
| 消费侧调用拓扑 | REST API 直连 / MCP / 本地镜像 | 建议先按 REST API 设计，后续视裁决调整 |
| 使用记录是否需要审计日志 | 如果合规要求使用行为可追溯 | 建议先在 usage_records 中记录使用者、时间和查询，后续视合规要求扩展 |
| A2 生成产物是否在后续版本实现 | 产物确认流程和格式约束模型 | 建议后续版本单独立项评估 |
| AI 辅助填充是否在后续版本纳入 | 降低角色创建门槛 | 建议后续版本作为 P2 配套能力评估 |
