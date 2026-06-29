# 公共契约裁决上提：retrieve/route 端点结构调整 + knowledge_object_ids 参数

> 版本：v1.0 | 日期：2026-06-23
> 发起方：角色产品（Virtual Actor）+ 知识平台（Knowledge Workbench）联合上提
> 接收方：组合层 / Lead 项目
> 目的：申请公共契约裁决——retrieve/route 从 package 路径下移出为独立端点，retrieve 新增 knowledge_object_ids 参数支持文档级范围过滤
> 性质：跨项目公共契约变更
> 共识基线：`role-to-knowledge-retrieve-scope-consensus-2026-06-22.md`（角色产品共识确认）+ `handoff-knowledge-retrieve-scope-uniqueness-confirm.zh-CN.md`（知识平台唯一性确认）+ `knowledge-to-role-koid-format-confirmation-2026-06-23.md`（格式确认）

---

## 一、裁决事项

**申请裁决**：retrieve 和 route 从 package 路径下移出为独立端点，retrieve 新增 knowledge_object_ids 参数支持文档级范围过滤。

### 变更内容

| 维度 | 变更前 | 变更后 |
|------|--------|--------|
| retrieve 路径 | `POST /api/packages/{package_id}/retrieve` | `POST /api/retrieve` |
| route 路径 | `POST /api/packages/{package_id}/route` | `POST /api/route` |
| 检索范围限定 | package_id（包级别） | knowledge_object_ids（文档级，可跨包） |
| 管理端点 | 不变 | 不变（packages/manifest/status 仍在 package 路径下） |

---

## 二、裁决理由（从项目目标推导）

### 2.1 角色产品的核心价值

角色产品的核心价值是"角色基于**专属知识**给出可靠结论"。"专属"意味着角色只引用自己绑定的文档，不引用未绑定的知识。

### 2.2 当前架构的问题

当前 retrieve API 的最小粒度是 package（知识包），没有到 document（文档）级别。角色绑定了知识包内的部分文档（通过 knowledge_refs 记录 knowledge_object_id），但 retrieve 检索整个 package，返回了角色未绑定的文档命中结果。

实际影响：角色消费时 LLM 引用了 `core-thesis.md` 等未绑定文档的内容，角色的"专属知识"边界被破坏。

### 2.3 变更后的价值

retrieve 新增 knowledge_object_ids 参数后：

- 角色消费时只检索绑定的文档，未绑定的文档不参与检索
- 越界判断（route Q0）与检索范围一致
- 角色的"专属知识"边界得到保障

### 2.4 双边共识

角色产品与知识平台已通过多轮文档交换达成完整共识：

1. API 结构调整：route/retrieve 移出 package 路径为独立端点
2. retrieve 请求结构：knowledge_object_ids + allowed_tiers
3. retrieve 行为规则：简化模式（含 Q0 越界拒答）+ 显式模式
4. route 行为：knowledge_object_ids 可选，路由判断仍基于关键词
5. knowledge_object_id 全局唯一性：由包名前缀保证
6. knowledge_object_id 格式：Vault 相对路径，双方一致，无需适配

---

## 三、变更影响范围

### 3.1 角色产品侧影响

| 影响项 | 说明 | 性质 |
|--------|------|------|
| `knowledge_platform.py` | retrieve/route 端点路径变更 + 传入 knowledge_object_ids | 代码改动，裁决落地后执行 |
| `consume_service.py` | retrieve 调用时传入角色的 knowledge_object_ids | 代码改动，裁决落地后执行 |
| `knowledge_object_id` 存储 | 格式不变（Vault 相对路径，双方一致） | 无需改动 |

### 3.2 知识平台侧影响

| 影响项 | 说明 | 性质 |
|--------|------|------|
| retrieve/route 端点 | 从 package 路径下移出为独立端点 | 代码改动，知识平台侧执行 |
| retrieve 请求处理 | 支持 knowledge_object_ids 参数，限定检索范围 | 代码改动，知识平台侧执行 |
| 管理端点 | 不变 | 无影响 |

### 3.3 不受影响的部分

| 不受影响项 | 说明 |
|------------|------|
| `GET /api/packages` | 管理端点，不变 |
| `GET /api/packages/{id}/manifest` | 管理端点，不变 |
| `GET /api/packages/{id}/status` | 管理端点，不变 |
| 角色产品自身数据模型 | knowledge_refs 表结构不变 |
| 角色产品消费 API 外部接口 | consume API 不变（消费方无感知） |
| knowledge_object_id 格式 | Vault 相对路径，双方一致 |

---

## 四、需要裁决确认的事项

| # | 裁决项 | 申请确认 |
|---|--------|---------|
| 1 | retrieve/route 端点结构调整 | 确认 retrieve 和 route 从 `POST /api/packages/{package_id}/*` 移出为 `POST /api/*` 独立端点 |
| 2 | retrieve 新增 knowledge_object_ids 参数 | 确认 retrieve 请求支持 knowledge_object_ids，传入时只在这些文档内检索；不传时检索全部（向后兼容） |
| 3 | 检索范围限定方式 | 确认检索范围只由 knowledge_object_ids 决定，不并行支持 package_id |

---

## 五、裁决落地后的执行计划

### 5.1 角色产品侧

| 步骤 | 内容 |
|------|------|
| 1 | 写回 dossier：端点变更写入 v0.5.1 design-delta.md |
| 2 | 代码适配：`knowledge_platform.py` retrieve/route 端点路径变更 + 传入 knowledge_object_ids |
| 3 | `consume_service.py`：retrieve 调用时传入角色的 knowledge_object_ids |
| 4 | 联调验证：验证检索结果只包含角色绑定的文档 |
| 5 | 质量门禁：pytest / frontend build / markdownlint / iteration-guard |

### 5.2 知识平台侧

| 步骤 | 内容 | 依赖 |
|------|------|------|
| 1 | retrieve/route 端点移出 package 路径 | 无 |
| 2 | retrieve 支持 knowledge_object_ids 参数 | 步骤1 |
| 3 | 内部测试 | 步骤2 |
| 4 | 通知角色产品可联调 | 步骤3 + 裁决落地 |

知识平台侧步骤1-3不依赖裁决落地，可与裁决并行。

---

## 六、附件

| 附件 | 说明 |
|------|------|
| `role-to-knowledge-retrieve-scope-filter-gap-2026-06-22.md` | 角色产品需求 |
| `handoff-knowledge-retrieve-scope-solution.zh-CN.md` | 知识平台方案 |
| `role-to-knowledge-retrieve-scope-consensus-2026-06-22.md` | 角色产品共识确认 |
| `handoff-knowledge-retrieve-scope-uniqueness-confirm.zh-CN.md` | 知识平台唯一性确认 |
| `knowledge-to-role-koid-format-confirmation-2026-06-23.md` | 知识平台格式确认 |
