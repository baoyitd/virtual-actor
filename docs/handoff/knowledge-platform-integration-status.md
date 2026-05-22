# 知识平台 -> 角色产品 当前状态同步

> 日期：2026-05-22
> 发送方：知识平台 / knowledge-workbench
> 接收方：角色产品 / virtual-actor
> 同步性质：状态口径与当前边界同步，不构成新的公共契约裁决
> Formal Status：Self-Tested
> Scope Note：consumer scope only, UI excluded
> Scope In：被其他子项目消费的知识读取 / 检索 / 版本追溯能力，以及 `POST /api/sync-all` 证据路径
> Scope Out：继续排除管理面板页面级 UI / operator 点击链路

---

## 一、当前可继续联动的读取链

角色产品当前可继续基于以下真实链路使用知识平台：

- `GET /api/health`
- `POST /api/v1/auths/signin`
- `GET /api/v1/knowledge/`
- `GET /api/v1/knowledge/{kb_id}/files`
- `GET /api/v1/knowledge/{kb_id}/files/{file_id}/content`
- `POST /api/v1/retrieval/query/collection`
- `GET /api/v1/version`

说明：

- 上述读取链当前仍可作为角色产品本轮真实联动上游。
- `POST /api/sync-all` 已纳入知识平台当前 `Scope In`，但它属于生产侧 API 证据路径，不等于“新知识发布后即可被检索命中”已经闭环。

## 二、当前唯一关键缺口

知识平台当前唯一关键未收口项是：

- 新知识发布后，`POST /api/sync-all` 已跑通
- 文件列表可见新知识
- `/content` 可读到新知识正文
- 但检索暂时还不能稳定命中新知识

因此角色产品当前不能把以下说法写成已通过：

- “发布后即可消费并检索到新知识”
- “知识平台已是 User-Acceptance-Candidate”
- “知识平台已是已验收上游”
- “知识平台已是可冻结的长期依赖版本”

## 三、对角色产品的直接影响

1. 当前角色产品可以继续依赖知识平台既有读取链推进本轮上线验收。
2. 如果后续角色产品要把“发布新知识 -> `POST /api/sync-all` -> 检索命中新知识”纳入正式验收项，必须单独记为未闭环依赖，不能提前写成通过。
3. 本次同步不改变已收口的字段、ID 真源、读写边界和版本规则。

## 四、引用真源

知识平台建议角色产品后续直接引用以下文档作为最新上游状态说明：

- [role-product-release-dependency-note.md](/Users/baoyi/Documents/code_buddy/knowledge-workbench/docs/handoff/role-product-release-dependency-note.md)

如果知识平台后续继续维持当前口径，则本文件只用于角色产品本地收口“当前状态与边界”；如其 `Formal Status`、`Scope In/Out` 或 `sync-all` 闭环结论发生变化，应以知识平台真源文档为准。
