# 角色产品 → 知识平台 retrieve 范围过滤方案共识确认

> 版本：v1.0 | 日期：2026-06-22
> 发起方：角色产品（Virtual Actor）
> 接收方：知识平台（Knowledge Workbench）
> 目的：确认知识平台提出的 retrieve 范围过滤方案，标注一项待确认事项，请知识平台回应后完成共识
> 前置文档：`role-to-knowledge-retrieve-scope-filter-gap-2026-06-22.md`（角色产品需求）→ `handoff-knowledge-retrieve-scope-solution.zh-CN.md`（知识平台方案）

---

## 一、已共识事项

### 1.1 API 结构调整

route 和 retrieve 从 package 路径下移出为独立端点：

| 调整前 | 调整后 |
|--------|--------|
| `POST /api/packages/{package_id}/route` | `POST /api/route` |
| `POST /api/packages/{package_id}/retrieve` | `POST /api/retrieve` |

管理端点保持不变。检索范围由 knowledge_object_ids 决定，不由 URL 路径的 package_id 限定。

角色产品认同。

### 1.2 retrieve 请求结构

```json
{
  "question": "...",
  "knowledge_object_ids": ["doc1", "doc2"],
  "allowed_tiers": null
}
```

- knowledge_object_ids 传入时只在这些文档内检索；不传时检索全部（向后兼容）
- allowed_tiers 不传时走简化模式（内部自动路由）；传时走显式模式

角色产品认同。

### 1.3 retrieve 行为规则

简化模式：

1. 先执行路由（Q0-Q6）
2. Q0 越界 → 返回 refused
3. 传入 knowledge_object_ids 时，在文档子集内检索；子集内无命中 → 返回空 hits（证据不足，非越界）
4. 不传 knowledge_object_ids 时，检索全部已加载文档

显式模式：

1. 不执行内部路由
2. 在 knowledge_object_ids 子集内按 allowed_tiers 检索
3. 调用方自行负责越界判断

角色产品认同。两层分离合理：route 判断领域级边界（问题是否属于这个知识领域），retrieve 返回空 hits 体现文档级覆盖不足（问题属于领域但绑定文档未覆盖）。

### 1.4 route 行为

route 接受 knowledge_object_ids 作为上下文信息，路由判断仍基于关键词规则。knowledge_object_ids 在 route 中可选，供未来扩展。

角色产品认同。

---

## 二、待知识平台确认的事项

### knowledge_object_id 全局唯一性

角色产品的需求是：knowledge_object_id 必须全局唯一，不能因为跨包而产生重名歧义。

当前角色产品存储的 knowledge_object_id 来自 manifest 的 relative_path。如果多包场景下不同包存在相同 relative_path 的文档，retrieve 传入 knowledge_object_ids 时会产生歧义。

需要知识平台确认：knowledge_object_id 是否保证全局唯一？如果是，通过什么机制保证（包名前缀、UUID、或其他）？

---

## 三、共识完成后的下一步

1. 双方确认全部事项（含第二节）后，共识完成
2. 双方共同上提组合层裁决（公共契约变更：route/retrieve 端点结构调整 + knowledge_object_ids 参数）
3. 裁决落地后角色产品启动代码适配（endpoint 变更 + knowledge_object_ids 传参）
4. 裁决落地前角色产品不改代码
