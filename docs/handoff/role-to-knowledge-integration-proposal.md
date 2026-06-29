# 角色产品 → 知识平台 集成方案

> 版本：v0.5.1 | 日期：2026-06-26
> 发起方：角色产品（Virtual Actor）
> 接收方：知识平台（Knowledge Workbench）
> 状态：**已切换至 Knowledge Workbench 公共契约接口，端到端联调通过**
>
> 更新说明（v0.3 → v0.5.1）：
> - 接口对接点从 Open WebUI 直连切换到 Knowledge Workbench 公共契约接口（`/api/public/*`）
> - Open WebUI 退为知识平台内部执行适配层，角色产品不再直接调用
> - retrieve/route 从 package 路径下移出为独立运行态端点
> - retrieve 新增 `knowledge_object_ids` 参数支持文档级范围过滤
> - alpha 阶段无 auth，移除 Open WebUI 遗留配置（KNOWLEDGE_API_TOKEN 等）
> - 裁决依据：`adjudication-knowledge-interface-ownership-change-2026-06-17.md`

---

## 一、v0.5.1 接口总览

| 接口 | 端点 | 方法 | 用途 |
|------|------|------|------|
| 知识包列表 | `/api/public/packages` | GET | 知识包列表 + 健康检查 |
| 结构化元数据 | `/api/public/packages/{package_id}/manifest` | GET | 知识包文档列表（含 tier/doc_role/evidence_type） |
| 版本标识 + 健康状态 | `/api/public/packages/{package_id}/status` | GET | 版本标识（version_id / git commit hash） |
| 问题路由 | `/api/public/route` | POST | 判断问题类型（Q0-Q6），越界返回 refused |
| 检索 | `/api/public/retrieve` | POST | 知识检索（支持 knowledge_object_ids scope 过滤） |

---

## 二、5 项接口契约（v0.5.1）

### 接口 1：知识包列表

| 属性 | v0.5.1 契约 |
|------|-------------|
| **用途** | 知识包列表浏览 + 健康检查（HTTP 200 即可达） |
| **调用** | `GET /api/public/packages` |
| **返回** | `[{"package_id": "eve", "name": "10-Areas/eve", "document_count": 51, ...}, ...]` |
| **auth** | alpha 阶段无 auth |

### 接口 2：结构化元数据（manifest）

| 属性 | v0.5.1 契约 |
|------|-------------|
| **用途** | 角色创建/编辑时浏览可绑定知识文档，获取分层元数据 |
| **调用** | `GET /api/public/packages/{package_id}/manifest` |
| **注意** | `package_id` 可能是中文（如 `快消品行业知识`），URL 中需做 `urllib.parse.quote` percent-encode |
| **返回** | `{"documents": [{"knowledge_object_id": "10-Areas/eve/...", "title": "...", "tier": "P1", "doc_role": "...", "evidence_type": "...", ...}, ...]}` |

### 接口 3：版本标识 + 健康状态

| 属性 | v0.5.1 契约 |
|------|-------------|
| **用途** | 角色发布时获取知识库版本快照 |
| **调用** | `GET /api/public/packages/{package_id}/status` |
| **返回** | `{"version_id": "fafecb7e4b17519c06e7dd2e65ee8865619bf3ff", ...}` |
| **版本标识格式** | git commit hash（40 位），与 v0.3 的 `knowledge_version_id` 语义一致 |

### 接口 4：问题路由

| 属性 | v0.5.1 契约 |
|------|-------------|
| **用途** | 判断问题类型（Q0-Q6），Q0 越界返回 `refused: true` |
| **调用** | `POST /api/public/route` |
| **请求体** | `{"question": "...", "knowledge_object_ids": ["doc1", "doc2"]}`（knowledge_object_ids 可选） |
| **返回** | `{"q_type": "Q1", "refused": false, ...}` 或 `{"refused": true, "refusal_reason": "..."}` |

### 接口 5：知识检索（retrieve）

| 属性 | v0.5.1 契约 |
|------|-------------|
| **用途** | 角色对话运行时检索相关片段，注入 LLM prompt |
| **调用** | `POST /api/public/retrieve` |
| **请求体** | `{"question": "...", "knowledge_object_ids": ["doc1", "doc2"]}` |
| **scope 过滤** | `knowledge_object_ids` 传入时仅在这些文档内检索；不传时全量检索（兼容模式） |
| **越界处理** | 简化模式下先执行路由，Q0 越界返回 `{"refused": true, "refusal_reason": "..."}`；角色产品映射为 `boundary_blocked` 状态 |
| **返回** | `{"hits": [{"knowledge_object_id": "...", "snippet": "...", "title": "...", "score": 0.85, "tier": "P1", "doc_role": "...", "evidence_type": "...", "source_reference": "...", ...}, ...]}` |
| **检索引擎** | 当前使用确定性字符级评分器（Open WebUI 向量检索适配器未实现）；已知偏差：检索命中精度不足，无法支撑生产级语义检索 |

---

## 三、关键约定

### 3.1 knowledge_object_id 格式

- 格式为 Vault 相对路径（如 `10-Areas/eve/master/l6/product-combinations/decision-closed-loop/STARTUP-PROMPT.md`），含根前缀和 `.md` 后缀
- 与知识平台存储格式一致，无需转换
- 正式消费字段统一为顶层 `knowledge_object_id`

### 3.2 knowledge_version_id 格式

- 格式为 40 位 Git commit hash（如 `fafecb7e4b17519c06e7dd2e65ee8865619bf3ff`）
- 来自 `/api/public/packages/{package_id}/status` 的 `version_id` 字段

### 3.3 package_id 注意事项

- `package_id` 可能是中文（如 `快消品行业知识`、`复星旅文知识库`），URL 中需做 percent-encode
- `package_id` 不参与 retrieve/route 的运行态范围定义——检索范围由 `knowledge_object_ids` 决定
- 已知缺陷：中文 `package_id` 的 manifest/status 端点返回 404（已反馈知识平台 2026-06-24，待修复）

### 3.4 alpha 阶段无 auth

所有 `/api/public/*` 端点 alpha 阶段无需认证。已从配置中移除 Open WebUI 遗留的 `KNOWLEDGE_API_TOKEN`、`KNOWLEDGE_AUTH_EMAIL`、`KNOWLEDGE_AUTH_PASSWORD`。

---

## 四、配置对齐

| 配置项 | 值 | 文件 |
|--------|-----|------|
| `KNOWLEDGE_API_BASE` | `http://localhost:3099` | `.env` / `.env.example` / `config.py` / `docker-compose.yml` |
| `KNOWLEDGE_DEFAULT_PACKAGE_ID` | `eve` | 同上 |
| auth 字段 | 无 | 已移除 |

---

## 五、角色产品侧实现

### 5.1 对接服务

`app/services/knowledge_platform.py` — `KnowledgePlatformService` 封装全部 5 项接口调用。

### 5.2 kb_id 解析逻辑

`resolve_runtime_kb_id_from_bases` 负责将 `kb_id` 解析为知识平台的 `package_id`：
1. 精确匹配 package_id
2. 按 name 匹配
3. 从 `knowledge_object_id` 路径反推
4. 默认包（`eve`）

`_hydrate_runtime_kb_ids` 在读取时做内存解析，**不落库**（历史教训：之前会 flush 落库导致数据污染）。

### 5.3 retrieve scope 过滤

角色消费时，`consume_service.py` 调用 retrieve 并传入角色绑定的 `knowledge_object_ids`，确保只检索角色绑定的文档。未绑定的文档不参与检索。

### 5.4 检索结果结构适配

retrieve 返回的 hits 含 `tier`/`doc_role`/`evidence_type`/`source_reference` 分层元数据。`consume_service.py` 将这些字段映射到 sources 列表，角色回答中可区分制度级与参考级引用。

### 5.5 越界拒答处理

retrieve 简化模式返回 `refused: true` 时，`consume_service.py` 映射为角色的 `boundary_blocked` 状态。

---

## 六、已知偏差

| 偏差 | 影响 | 处理 |
|------|------|------|
| retrieve 使用确定性评分器，Open WebUI 向量检索适配器未实现 | 检索命中精度不足，无法支撑生产级语义检索 | 已上提反馈，Open WebUI 适配器就绪后需重新联调验证检索质量 |
| 中文 package_id manifest/status 404 | 知识目录浏览和 tier 统计受限；不影响 retrieve/route 检索 | 已反馈知识平台 2026-06-24，待修复 |

---

## 七、联调验证结果

| 验证项 | 结果 | 证据 |
|--------|------|------|
| 知识包列表 | PASS | `GET /api/public/packages` HTTP 200，返回 7 个知识包 |
| 知识目录（eve） | PASS | 51 文档，koid 格式 `10-Areas/eve/master/*.md` |
| 版本标识 | PASS | `version_id=fafecb7e4b17519c06e7dd2e65ee8865619bf3ff` |
| retrieve 全量 | PASS | 5 chunks，koid 字段完整 |
| retrieve scoped | PASS | 1 chunk，无范围泄漏 |
| retrieve 空 scope | PASS | 0 chunks |
| route 端点 | PASS | Q1 → P1 |
| 端到端 consume | PASS | status=success，知识检索+LLM 全链路通过 |

详见 `delivery/test-results.md`。

---

## 八、裁决待闭合事项

| 事项 | 状态 |
|------|------|
| 知识平台接口归属变更 | 双边共识已达成（2026-06-17），v0.5.1 已完成代码切换；裁决仍在组合层流程中 |
| retrieve/route 端点结构调整 + knowledge_object_ids | 双边共识已达成（2026-06-23），v0.5.1 已完成代码适配；裁决仍在组合层流程中 |
| knowledge_object_id 全局唯一性 | 待知识平台最终确认 |

外部项目如需稳定依赖上述接口，必须单独完成公共契约裁决。

---

## 附录：知识平台 API 端点速查

| 接口 | 端点 | 方法 |
|------|------|------|
| 知识包列表 | `localhost:3099/api/public/packages` | GET |
| 结构化元数据 | `localhost:3099/api/public/packages/{package_id}/manifest` | GET |
| 版本标识 + 健康状态 | `localhost:3099/api/public/packages/{package_id}/status` | GET |
| 问题路由 | `localhost:3099/api/public/route` | POST |
| 检索 | `localhost:3099/api/public/retrieve` | POST |
