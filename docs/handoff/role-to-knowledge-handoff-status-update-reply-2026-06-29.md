# 角色产品 → 知识平台：handoff 状态更新回复

> 版本：v1.0 | 日期：2026-06-29
> 发起方：角色产品（Virtual Actor）
> 接收方：知识平台（Knowledge Workbench）
> 目的：回复知识平台 06-29 状态更新，确认两项 handoff 闭合状态，反馈检索质量联调结果，回复 Q4 共识决定
> 前置文档：
> - 知识平台回复：`knowledge-to-role-handoff-status-update-2026-06-29.md`
> - 文档1原反馈：`role-to-knowledge-chinese-package-manifest-404-2026-06-24.md`
> - 文档2原反馈：`role-to-knowledge-execution-risk-feedback-2026-06-17.md`

---

## 一、文档1闭合确认：中文 package_id manifest 端点 404

### 1.1 收到确认

角色产品确认收到知识平台的修复回同步。关于知识平台询问"06-24 回同步文档 `knowledge-to-role-chinese-package-manifest-fix-2026-06-24.md` 是否在角色产品侧收到"——该文档在知识平台项目目录下（`knowledge-workbench/docs/handoff/`），属于跨项目 handoff 的正常机制，双方各自维护各自的 `docs/handoff/` 目录。角色产品侧通过项目交接文档（`project-handoff-to-codebuddy-2026-06-24.md` §9.3）知晓该文件存在，但文件本身未同步到角色产品仓库。这不是同步链路问题，是跨项目 handoff 机制的正常表现。

### 1.2 当前状态

角色产品 06-29 实测确认：

```
快消品行业知识: manifest=200 status=200
复星旅文知识库: manifest=200 status=200
```

知识目录浏览和 tier 统计已恢复正常。角色产品侧 `urllib.parse.quote` 编码适配继续保留（编码是 URL 合法性要求，与 404 修复无关）。

### 1.3 闭合判定

**文档1已闭合。** 知识平台 06-24 修复，角色产品 06-29 实测确认。

---

## 二、文档2闭合确认：Open WebUI 适配器执行风险反馈

### 2.1 联调验证结果

角色产品 06-29 对混合检索进行了 3 个维度的联调验证，全部通过：

| 测试项 | 验证方式 | 结果 |
|--------|---------|------|
| 混合检索引擎确认 | `POST /api/public/retrieve` 全量检索 | PASS — 5 hits 中 3 条 `execution_engine=open_webui` + 2 条 `execution_engine=deterministic` |
| 语义匹配能力 | 问题"促销策略如何影响动销"全量检索 | PASS — open_webui 命中快消品行业知识文档（42-渠道结构与分销、44-消费者行为与FMOT、43-费用管理与ROI），语义匹配有效 |
| scoped 范围过滤 | 5 篇绑定文档做 scope 检索 | PASS — 4 hits 全部在范围内，0 条泄漏；混合引擎（2 deterministic + 2 open_webui） |
| 端到端 consume | test-consume 快消行业业务分析专家角色 | PASS — status=success，boundary=within_boundary，5 sources 全 P1，回答专业有知识引用 |

### 2.2 联调结论

混合检索与 06-17 反馈时的纯确定性评分器有质变——open_webui 向量检索能做语义匹配，scoped 范围过滤无泄漏，端到端 consume 质量满足"可靠结论"目标。v0.5.1 dossier 中"检索质量回退"已知偏差已消除，dossier 文档已更新。

### 2.3 Q1-Q4 回应确认

知识平台对 06-17 提出的 4 个问题逐条回应，角色产品确认收到并表示认可：

- **Q1**（为什么步骤3没执行就发可联调通知）：认可知识平台的坦诚说明。06-17 的事实无辩护，06-23 已完成适配器实现。
- **Q2**（适配器实现计划）：确认已完成，无后续计划项。
- **Q3**（确定性评分器是否可替代向量检索）：确认当前是混合检索（向量主 + 确定性补充 + fallback），不是替代关系。角色产品 06-29 联调验证后认可检索质量。
- **Q4**（两阶段方案是否应回到共识流程）：见下节。

### 2.4 Q4 决定：走共识流程

角色产品决定**走共识流程**正式确认 retrieve 执行机制变更。

理由：
1. retrieve 执行机制从共识约定的"委托 Open WebUI 向量检索"变为"混合检索（open_webui 主 + deterministic 补充 + fallback）"，属于执行方案变更。
2. 按 A-02（设计冻结后不得自行改变关键交互）和 E-01（公共契约变更须上提裁决）规则，执行方案变更应正式确认。
3. 知识平台也不单方面判定，双方就此达成共识后正式回复，符合"先反馈再执行"原则。

共识范围：
- 确认 retrieve 执行机制为混合检索（open_webui 向量检索为主 + deterministic 确定性评分补充 + fallback）
- 确认 `execution_engine` 字段为诊断字段，不纳入公共契约消费必填字段
- 确认 Open WebUI 不可用时 fallback 为纯确定性，质量下降仅维持可用性

角色产品将在 `docs/handoff/` 发起共识确认文档，请知识平台确认后双方共同上提组合层。

### 2.5 闭合判定

**文档2已闭合。** Open WebUI 适配器已实现，06-29 联调验证通过，4 个问题已回应，Q4 决定走共识流程。后续共识确认作为新事项处理，不再挂在此文档下。

---

## 三、角色产品侧文档更新说明

角色产品已同步更新以下 v0.5.1 dossier 文档：

| 文件 | 更新内容 |
|------|---------|
| `delivery/test-results.md` | 新增"混合检索联调验证（2026-06-29）"小节，记录 5 项测试结果 |
| `delivery/release-notes.md` | 当前限制中"检索质量回退"更新为"混合检索已验证通过"；"中文包名404"更新为"已修复"；下一步更新 |
| `docs/iterations/v0.5.1/implementation-notes.md` | 偏差记录处理状态更新为"已解决"；代码切换授权路径补充 06-23 适配器实现和 06-29 联调通过 |

---

## 四、下一步

1. 角色产品发起 retrieve 执行机制共识确认文档（近期）
2. 知识平台确认共识内容
3. 双方共同上提组合层裁决（如需）
4. 两项裁决（接口归属 + retrieve/route 结构）仍在组合层流程中，角色产品侧代码已切换/适配
