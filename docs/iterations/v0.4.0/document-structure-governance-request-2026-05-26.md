# v0.4.0 文档结构治理要求

> 日期：2026-05-26
> 状态：待处理
> 触发原因：v0.4 设计期文档数量快速增加，研究、共识、反馈、P0 材料、审核意见和正式 dossier 混放，已影响真源识别和实现阶段口径稳定。

## 1. 当前结论

当前 v0.4 文档结构存在治理风险，但不阻断工作方正在处理的上一轮 P0 材料评审意见。

处理顺序：

1. 工作方先完成 `p0-materials-review-2026-05-26.md` 中列出的阻塞项修复。
2. 阻塞项修复后，再处理本文档要求的文档结构治理。
3. 文档结构治理完成前，不应进入设计冻结或代码实现。

## 2. 主要问题

1. `docs/iterations/v0.4.0/` 下混放研究、共识、反馈、规划回应、P0 材料、审核意见和正式 dossier 文件。
2. 工作方难以判断哪些文件是当前有效真源，哪些是过程稿，哪些已被替代。
3. `delivery/test-plan-v0.4.md` 和 `delivery/test-cases-v0.4.md` 仍保留旧口径。
4. `docs/handoff/` 中存在 v0.4 当前复审转发材料，但 handoff 不应作为版本内真源。
5. v0.3 Accepted 交付证据与 v0.4 Draft 设计材料同层存放，容易被误用。

## 3. 治理目标

1. 明确 v0.4 当前 Formal Status 和是否可进入实现。
2. 明确当前真源文件清单。
3. 明确仅供参考文件和已被替代文件。
4. 明确当前阻塞项和下一步流程。
5. 降低实现阶段误读旧口径、绕过设计冻结或误用 v0.3 证据的风险。

## 4. 必须完成的整理动作

### 4.1 新增 v0.4 README

在 `docs/iterations/v0.4.0/README.md` 新增版本文档索引。

必须包含：

1. 当前 Formal Status。
2. 当前是否允许进入实现。
3. 当前阻塞项。
4. 当前真源清单。
5. 必读文件清单。
6. 仅供参考文件清单。
7. 已废弃或被替代文件清单。
8. 下一步流程。

### 4.2 标注文档状态

所有 v0.4 关键文档必须能被识别为以下状态之一：

1. Current Source of Truth。
2. Active Review Material。
3. Superseded。
4. Historical Reference。
5. Handoff Only。

### 4.3 处理旧口径测试文档

`delivery/test-plan-v0.4.md` 和 `delivery/test-cases-v0.4.md` 当前仍保留旧范围，在正式回写前必须标注：

```text
Superseded / Not current source of truth
```

修订后需覆盖当前 `US-06` 至 `US-21`，并删除旧口径：

1. “DD-04 不新增接口”。
2. “决策产品不纳入”。
3. “只覆盖 US-06、US-07、US-08、US-09、US-10、US-12、US-13”。

### 4.4 明确 handoff 边界

`docs/handoff/` 仅用于对外同步或转发说明，不作为 v0.4 版本内真源。

v0.4 真源判断应以 iteration dossier 下的 README、scope、design-delta、traceability、审核意见和 P0 材料为准。

### 4.5 建议目录分层

建议后续整理为：

```text
docs/iterations/v0.4.0/
  README.md
  scope.md
  design-delta.md
  traceability.md
  implementation-notes.md
  research/
  requirements/
  design/
  review/
  p0-materials/
  archive/
```

该分层可以分步执行；如短期不移动文件，必须先在 README 中完成归类。

## 5. 验收标准

文档结构治理完成后，应能回答：

1. v0.4 当前能否进入实现。
2. 当前必须按哪些文件实现。
3. 哪些文件已经被替代，不能作为实现依据。
4. 当前还有哪些阻塞项。
5. delivery 中哪些证据属于 v0.3，哪些属于 v0.4。
6. handoff 文件是否只作为转发材料，而不是版本真源。

## 6. 当前不要求立即处理

本文档是后续治理要求。工作方当前优先级仍是修复 `p0-materials-review-2026-05-26.md` 中的 P0/P1 阻塞项。

阻塞项修复完成后，再处理本文档。
