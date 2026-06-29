# 角色产品 → 知识平台：retrieve 执行机制共识确认

> 版本：v1.0 | 日期：2026-06-29
> 发起方：角色产品（Virtual Actor）
> 接收方：知识平台（Knowledge Workbench）
> 目的：正式确认 retrieve 执行机制从共识约定的"委托 Open WebUI 向量检索"变更为"混合检索"，请知识平台确认后双方共同上提组合层
> 性质：公共契约执行方案变更共识确认
> 前置文档：
> - 原共识约定：`role-to-knowledge-consensus-confirmation-2026-06-17.md` §1.3（retrieve 行为规则，简化模式检索执行依赖 Open WebUI 向量检索）
> - 风险反馈：`role-to-knowledge-execution-risk-feedback-2026-06-17.md`（角色产品反馈检索执行机制偏离共识）
> - 状态更新回复：`knowledge-to-role-handoff-status-update-2026-06-29.md` §三（知识平台确认 Open WebUI 适配器已实现，retrieve 为混合检索，Q4 不单方面判定是否走共识流程）
> - 角色产品回复：`role-to-knowledge-handoff-status-update-reply-2026-06-29.md` §2.4（角色产品决定走共识流程）

---

## 一、共识事项

### 1.1 retrieve 执行机制变更

**原共识约定**（`role-to-knowledge-consensus-confirmation-2026-06-17.md` §1.3）：

> 简化模式：检索执行依赖 Open WebUI 向量检索。

**实际实现**（`scripts/protocol/retrieval.py` `_do_search`，第 313-324 行）：

retrieve 为混合检索，执行链路：

1. `_owui_search(question, docs)` — 调 Open WebUI `POST /api/v1/retrieval/query/collection` 做向量检索，返回 hits 标记 `execution_engine="open_webui"`
2. `_deterministic_search(question, docs)` — 字符级评分，返回 hits 标记 `execution_engine="deterministic"`
3. 合并：open_webui hits + deterministic 补充最多 2 条（去重，按 `knowledge_object_id` 去重）
4. 按 score 降序取 top 5
5. fallback：open_webui 返回空时直接用 deterministic 结果

**变更内容**：从"纯 Open WebUI 向量检索"变更为"混合检索（open_webui 向量检索为主 + deterministic 确定性评分补充 + fallback）"。

**角色产品确认**：06-29 联调验证通过（详见 `role-to-knowledge-handoff-status-update-reply-2026-06-29.md` §2.1），语义匹配能力恢复，scoped 范围过滤无泄漏，检索质量满足"可靠结论"目标。

---

### 1.2 `execution_engine` 字段属性

**定义**：retrieve 响应中 `hits[].execution_engine` 字段标注每条命中的来源检索引擎。

**属性**：
- **诊断字段，不纳入公共契约消费必填字段**
- 消费方（角色产品）可读取此字段用于诊断和日志，但不依赖此字段进行业务逻辑判断
- 知识平台可在后续版本中调整引擎策略（如增加 rerank 引擎），`execution_engine` 取值范围可能扩展，不构成公共契约 breaking change
- 角色产品当前 `knowledge_platform.py` retrieve 方法未映射此字段到 sources 列表，不影响消费功能

**角色产品立场**：认可此字段为诊断字段，不作为公共契约消费必填。

---

### 1.3 fallback 行为

**场景**：Open WebUI 服务不可用或返回空结果时。

**实际行为**（`retrieval.py` 第 317-318 行）：

```python
if not owui_hits:
    return det_hits
```

- Open WebUI 返回空（服务不可用、无命中、异常等）时，直接使用 deterministic 结果
- 此时检索质量下降（字符匹配，无语义能力），仅维持接口可用性
- 消费方无感知 fallback 发生（除非检查 `execution_engine` 字段全部为 `deterministic`）

**角色产品确认**：认可此 fallback 行为。在 Open WebUI 不可用时维持可用性优于直接报错，检索质量下降作为运行态风险接受。

---

## 二、不涉及公共契约变更的确认

本共识确认的是 retrieve **内部执行机制**的变更，不涉及公共契约接口的外部契约变更：

| 维度 | 是否变更 | 说明 |
|------|---------|------|
| retrieve 端点路径 | 否 | 仍为 `POST /api/public/retrieve` |
| retrieve 请求体 | 否 | 仍为 `{"question": "...", "knowledge_object_ids": [...]}` |
| retrieve 响应结构 | 否 | 仍为 `{"hits": [...], "refused": ...}` |
| hits 字段集 | 否 | 含 knowledge_object_id/title/tier/score/snippet 等已有字段 |
| 新增公共字段 | 否 | `execution_engine` 为诊断字段，不纳入公共契约消费必填 |
| knowledge_object_id 格式 | 否 | 仍为 Vault 相对路径 |
| scope 过滤行为 | 否 | knowledge_object_ids 传入时限定范围，不传时全量 |

**结论**：本共识不新增、不修改、不删除已冻结的公共契约字段。retrieve 执行机制变更为知识平台内部实现变更，消费方无感知。

---

## 三、需要知识平台确认的事项

1. **§1.1 retrieve 执行机制变更**：确认混合检索的执行链路描述与 `retrieval.py` 实际实现一致？
2. **§1.2 `execution_engine` 字段属性**：确认此字段为诊断字段，不纳入公共契约消费必填？确认后续引擎策略调整不构成公共契约 breaking change？
3. **§1.3 fallback 行为**：确认 Open WebUI 不可用时直接使用 deterministic 结果，消费方无感知（除非检查 execution_engine）？
4. **§二 不涉及公共契约变更**：确认本共识不新增/不修改/不删除已冻结的公共契约字段？

---

## 四、共识完成后的下一步

1. 双方确认全部事项后，共识完成
2. 如双方均认为此变更属于内部执行机制变更、不涉及公共契约字段变更，则无需上提组合层裁决，共识文档本身即为闭合依据
3. 如任一方认为涉及公共契约变更，则共同上提组合层裁决
4. 共识完成后，角色产品更新 v0.5.1 dossier 中 retrieve 执行机制相关表述为"混合检索（已共识确认）"

---

## 五、角色产品立场

1. 角色产品认可混合检索作为 retrieve 的最终执行方案，06-29 联调验证通过。
2. 角色产品认为此变更为知识平台内部执行机制变更，不涉及公共契约字段变更，倾向于"无需上提组合层裁决，共识文档即为闭合依据"。
3. 最终是否上提由双方共识决定，角色产品不单方面判定。
