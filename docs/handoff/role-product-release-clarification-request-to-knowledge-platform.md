# 角色产品 -> 知识平台 上线验收前澄清清单

> 日期：2026-05-21
> 发起方：角色产品 / virtual-actor
> 接收方：知识平台 / knowledge-workbench
> 目的：为角色产品本轮上线验收收口运行语义与验收前提，不申请新增公共契约或冻结长期依赖版本

---

## 一、背景

角色产品已阅读知识平台提供的上线依赖说明：

- [role-product-release-dependency-note.md](/Users/baoyi/Documents/code_buddy/knowledge-workbench/docs/handoff/role-product-release-dependency-note.md)

角色产品接受以下口径：

- 知识平台 v1.3 当前可作为**稳定可用上游 / 稳定验收态上游**
- 当前**不表述为公共契约已冻结的长期依赖版本**
- 本轮可依赖知识列表、知识内容读取、RAG 检索、版本快照这四项能力推进上线验收

对应回复已收到：

- [role-product-release-clarification-response.md](/Users/baoyi/Documents/code_buddy/knowledge-workbench/docs/handoff/role-product-release-clarification-response.md)

当前这 4 项运行语义已收口，可作为角色产品本轮上线验收执行依据。

---

## 二、需要澄清的事项

### 1. 文件级绑定与检索范围的关系

角色产品当前保存的是文件级 `knowledge_object_id`，但实际检索使用的是：

- `POST /api/v1/retrieval/query/collection`

需要知识平台明确当前推荐口径：

- 方案 A：绑定文件仅用于展示与发布追溯，检索范围仍按整个知识库 collection 执行
- 方案 B：检索应仅覆盖已绑定文件，知识平台当前已支持对应过滤方式

如果是方案 B，请明确：

- 当前可用的过滤参数或调用方式
- 返回来源字段如何与已绑定文件一一对应

如果当前仍是方案 A，也请明确，便于角色产品在上线材料中准确描述“绑定”与“检索”的关系。

### 2. `knowledge_object_id` 的权威真源字段

角色产品上线验收需要稳定持久化 `knowledge_object_id`。

当前角色产品兼容读取方式为：

- `meta.knowledge_object_id`
- `meta.path`
- `item.knowledge_object_id`
- `item.path`

需要知识平台明确：

- 在 `GET /api/v1/knowledge/{kb_id}/files` 响应中，哪个字段是角色产品应持久化的正式 `knowledge_object_id`
- 在 `GET /api/v1/knowledge/{kb_id}/files/{file_id}/content` 响应中，是否也返回同一权威字段

目标是把当前“兼容归一化”收口为一个明确真源字段，降低后续歧义。

### 3. 内容读取对 `file_id` 的依赖方式

知识平台已确认内容读取接口可依赖：

- `GET /api/v1/knowledge/{kb_id}/files/{file_id}/content`

但角色产品当前绑定关系正式持久化的是：

- `knowledge_object_id`
- `knowledge_version_id`

并未将 `file_id` 作为正式绑定字段持久化。

需要知识平台明确推荐做法：

- 方案 A：角色产品需要读取内容时，先通过列表接口按 `knowledge_object_id` 反查 `file_id`
- 方案 B：角色产品可在内部运行态保存 `file_id` 作为非公共引用

如果允许采用方案 B，也请明确这是否仅属于运行态实现细节，而不是新增公共字段。

### 4. 上线验收时的健康检查与鉴权推荐口径

知识平台说明中同时提到了：

- `GET /api/v1/version`
- `GET http://localhost:3099/api/health`

需要明确角色产品在上线验收与部署验收中，应该以哪个接口作为“上游可用”的主要判据。

同时需要明确当前推荐鉴权口径：

- 固定 Bearer token
- 邮箱密码自动刷新 token

这会直接影响角色产品的：

- Docker Compose 环境变量模板
- 部署说明
- 真实联调与上线验收步骤

---

## 三、角色产品当前默认处理

在收到进一步澄清前，角色产品当前实现会按以下临时口径工作：

- 知识绑定持久化 `knowledge_object_id` 与 `knowledge_version_id`
- 检索默认走知识库 collection 级调用，不把“文件已绑定”直接等同于“仅检索该文件”
- 内容读取能力视为上游可依赖，但暂未将其纳入角色产品正式用户主路径
- 健康检查仍以 `GET /api/v1/version` 为基础连通性判断

以上仅为当前上线验收前的临时实现口径，不应被解读为知识平台长期冻结契约。

---

## 四、希望知识平台返回的形式

建议知识平台直接按以下格式回复，便于角色产品同步更新上线材料与验收脚本：

1. 文件级绑定与检索范围：选择方案 A 或 B；若为 B，补充调用方式
2. `knowledge_object_id` 真源字段：给出唯一正式字段名
3. 内容读取与 `file_id`：选择方案 A 或 B，并说明 `file_id` 是否可作为运行态引用
4. 健康检查与鉴权：给出上线验收推荐判据与推荐认证方式

---

## 五、说明

本清单的目标是收口**上线验收语义**，不是发起新的公共契约扩展，不涉及：

- 新增公共对象
- 新增公共字段
- 修改上位已裁决读写边界
- 将知识平台声明为长期冻结依赖版本
