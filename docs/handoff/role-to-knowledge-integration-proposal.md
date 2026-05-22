# 角色产品 → 知识平台 集成方案（v0.3 — MVP 就绪）

> 版本：v0.3 | 日期：2026-05-14
> 发起方：角色产品（Virtual Actor）
> 接收方：知识平台（Knowledge Workbench）
> 状态：**协商闭环，双边确认联调条件已完全具备，无剩余缺口**
>
> 更新说明（v0.2 → v0.3）：
> - 纳入知识平台 v1.1 可实现性反馈：接口 3 bug 修正、接口 4 已实现
> - Lead 裁决落地：knowledge_object_id = 文件路径型，knowledge_version_id = 40 位 Git hash
> - 角色产品待确认项从 3 → 2 项（knowledge_id 格式已由 lead 裁决解决）

---

## 一、v0.3 可接现性总览

| 接口 | 知识平台 v1.1 判定 | v0.3 状态 |
|------|-----------|---------|
| 接口 1：知识对象列表查询 | Open WebUI 替代方案就绪 | ✅ 已就绪 |
| 接口 2：知识内容获取 | 轻量代理接口新增 | ✅ 可实现 |
| 接口 3：知识检索（RAG） | Chat API bug 已修正，RAG 验证通过 | ✅ 已就绪 |
| 接口 4：知识版本标识 | `GET /api/v1/version` 已实现 | ✅ 已就绪 |

---

## 二、4 项接口契约（v0.3）

### 接口 1：知识对象列表查询 ✅

| 属性 | v0.3 契约 |
|------|----------|
| **用途** | 角色创建/编辑时浏览可绑定知识条目 |
| **调用** | `GET /api/v1/knowledge/` → `GET /api/v1/knowledge/{kb_id}/files` |
| **字段映射** | `id`（UUID）→ knowledge_object_id 的真源路径需知识平台提供映射 |

### 接口 2：知识内容获取 🔧

| 属性 | v0.3 契约 |
|------|----------|
| **用途** | 角色绑定时获取 Markdown 原文 |
| **调用** | `GET /api/v1/knowledge/{kb_id}/files/{file_id}/content` |
| **优先级** | MVP 可后置 |

### 接口 3：知识检索（RAG）✅

| 属性 | v0.3 契约 |
|------|----------|
| **用途** | 角色对话运行时检索相关片段，注入 LLM prompt |
| **调用** | `POST /api/chat/completions`（带知识库上下文）→ deepseek-v4 → 答案+来源 |
| **状态** | Open WebUI `socket/main.py:902` 的 `request_info.get('chat_id', '').startswith(...)` bug 已改为 `(request_info.get('chat_id') or '').startswith(...)`，RAG 端到端验证通过 |

### 接口 4：知识版本标识 ✅

| 属性 | v0.3 契约 |
|------|----------|
| **用途** | 角色发布时获取知识库版本快照 |
| **调用** | `GET http://localhost:3000/api/v1/version` |
| **返回** | `{ commit_hash: "ba280c293c5775fae52cf39cd5fd69368bae022e", timestamp: "2026-05-14T05:58:14Z", source: "knowledge-platform" }` |

---

## 三、Lead 裁决对集成契约的影响

Lead 项目 2026-05-14 裁决事项 3（`validated_knowledge_versions` 最小结构）直接影响知识平台与角色产品的 ID 规范：

> `knowledge_object_id` 与 `knowledge_version_id` 的命名与语义真源，归知识平台 owner。

知识平台据此定义：

| 标识 | 格式 | 示例 | 说明 |
|------|------|------|------|
| `knowledge_object_id` | 文件路径型（相对 vault 根） | `eve/master/core-thesis` | 与真源路径直接对应 |
| `knowledge_version_id` | 40 位 Git commit hash | `ba280c293c5775fae52cf39cd5fd69368bae022e` | 天然不可变，来自 `/api/v1/version` |

> ⚠️ **与 v0.2 差异**：v0.2 用的 Open WebUI UUID 不再作为 knowledge_object_id，改为文件路径型。角色产品在 `knowledge_refs` 中需存储文件路径型 ID。

---

## 四、MVP 最小可行集

| 接口 | MVP 优先级 | 状态 | 备注 |
|------|----------|------|------|
| 接口 1 列表查询 | 阻断 | ✅ 已就绪 | 字段映射需双方对齐（UUID → 路径型 ID） |
| 接口 3 RAG 检索 | 阻断 | ✅ 已就绪 | Chat API bug 已修正 |
| 接口 4 版本标识 | 阻断 | ✅ 已就绪 | `GET /api/v1/version` 已实现 |
| 接口 2 内容获取 | 可后置 | ✅ 可实现 | 轻量代理接口待新增 |

> 三项阻断接口全部就绪，**角色产品立即可启动与知识平台的联调**。

---

## 五、角色产品确认

### 5.1 ✅ 接受 knowledge_object_id = 文件路径型

不再使用 Open WebUI UUID，改为知识平台定义的路径型 ID（`eve/master/core-thesis`）。角色产品 `knowledge_refs` 字段按此格式存储。

### 5.2 ✅ 接受接口 4 挂在 Open WebUI 域名下

版本查询端点 `GET http://localhost:3000/api/v1/version`，角色产品无异议。

### 5.3 ✅ 接受首期 Open WebUI 路线

首期联调直接对接 Open WebUI API（`localhost:3000`），待 Phase 6 Dify 就绪后可选迁移。

---

## 六、角色产品侧 knowledge_refs 与 validated_knowledge_versions 格式（v0.3 收口）

### 6.1 knowledge_refs

```json
{
  "knowledge_object_id": "eve/master/core-thesis",
  "knowledge_version_id": "ba280c293c5775fae52cf39cd5fd69368bae022e",
  "title": "核心总纲",
  "type": "thesis",
  "knowledge_source": "knowledge-platform",
  "bound_at": "2026-05-14T10:00:00Z"
}
```

| 字段 | 来源 | 真源归属 |
|------|------|---------|
| `knowledge_object_id` | 知识平台定义（文件路径型） | 知识平台 owner |
| `knowledge_version_id` | `/api/v1/version` 返回的 commit_hash | 知识平台 owner |
| `title` | Open WebUI meta.title | 知识平台 |
| `type` | Open WebUI meta.type | 知识平台 |

### 6.2 validated_knowledge_versions（对齐上位裁决）

```json
{
  "knowledge_object_id": "eve/master/core-thesis",
  "knowledge_version_id": "ba280c293c5775fae52cf39cd5fd69368bae022e"
}
```

> 对齐上位裁决的最小追溯结构：两个字段，真源归知识平台 owner。

---

## 七、联调状态

| 接口 | 状态 | 角色产品可调时间 |
|------|------|---------------|
| 接口 1 | ✅ 已就绪 | 立即可调（需确认 UUID→路径型 ID 映射方案） |
| 接口 3 | ✅ 已就绪 | 立即可调 |
| 接口 4 | ✅ 已就绪 | 立即可调 |
| 接口 2 | ✅ 可实现 | 后续版本 |

---

## 八、待 lead 裁决事项

| 裁决事项 | 当前双边状态 |
|---------|-----------|
| 主 API 入口选型（Open WebUI vs Dify） | 首期双边已接受 Open WebUI，属局部实现选择 |

---

## 附录：知识平台 API 端点速查

| 接口 | 端点 | 方法 |
|------|------|------|
| 接口 1 | `localhost:3000/api/v1/knowledge/{kb_id}/files` | GET |
| 接口 2 | `localhost:3000/api/v1/knowledge/{kb_id}/files/{file_id}/content` | GET |
| 接口 3 | `localhost:3000/api/chat/completions` | POST |
| 接口 4 | `localhost:3000/api/v1/version` | GET |