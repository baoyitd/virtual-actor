# v0.4.0 规划方复审记录

> 版本：v0.4.0
> 复审日期：2026-05-25
> 复审角色：规划方 / 审核方
> 复审对象：`research-conclusion.md`、`scope.md`、`design-delta.md`、`traceability.md`
> 结论：有差距，补齐后再进入实现

## 1. 总体结论

当前研究方向成立，主线“角色资产化与使用入口”基本合理，但前置研究和本地事实核对还不够坚实，暂不批准直接进入实现。

本轮可继续推进“研究结论修订 + Scope 冻结补强”，完成后再提交规划方复审。复审通过前，不得进入功能代码开发，不得升级 Formal Status，不得将 v0.4.0 表述为已进入实现或可交付版本。

## 2. 已复核通过的质量命令

以下命令已由规划方复跑：

```bash
npm run lint:md
python3 scripts/iteration-guard.py --repo-root . --mode release
./venv/bin/python -m pytest tests -q
cd frontend && npm run build
```

结果：

| 项 | 结果 |
|---|---|
| Markdown lint | PASS，0 errors |
| iteration guard | PASS |
| pytest | PASS，38 passed, 8 warnings |
| frontend build | PASS |

说明：以上结果只证明当前仓库未破坏格式、guard、测试和构建；不代表研究结论已经足够支撑进入实现。

## 3. 主要问题

### P0-1 竞品与市场结论证据链不足

`research-conclusion.md` 对竞品下了较强判断，例如“市场不缺 Agent Builder，缺角色资产治理产品”“版本生命周期是最大缺口”“virtual-actor 已领先竞品”等，但文档内缺少引用来源、调研样本依据和逐项证据。

要求：

1. 每个核心判断必须补官方文档、公开资料或明确观察依据。
2. 将“领先竞品”等绝对表述改成分维度、基于证据的表述。
3. 对 CrewAI、Microsoft Agent Framework、Dify、Coze、Salesforce Agentforce 等产品的知识、工作流、API、Actions、A2A 等能力进行重新核对。

### P0-2 本地能力复盘存在事实错误

当前文档称 `knowledge_boundary` 和 `capability_boundary` “已有 schema 但创建页未暴露”，该说法不准确。

当前本地事实：

1. `RoleCreate`、`RoleUpdate`、`RoleDetail` 中已有 `capability_boundary`。
2. 前端创建 / 编辑页已暴露 `capability_boundary`。
3. 详情页已展示 `capability_boundary`。
4. `knowledge_boundary` 当前不在 `RoleCreate`、`RoleUpdate`、`RoleDetail` schema 中，也未在前端暴露。

要求：

1. 修正 `research-conclusion.md`、`scope.md`、`design-delta.md` 和 `traceability.md` 中相关事实描述。
2. 将缺口调整为：`knowledge_boundary` 缺 schema/API/UI；`capability_boundary` 已有基础入口，但可做资产化展示和语义强化。

### P0-3 Scope 从研究跳到实现清单，用户场景推导不足

当前 `scope.md` 直接列出 DD-01 到 DD-08，包括新增字段、使用台、usage_records、版本详情、模板库等。但还没有从集团企业真实用户场景逐步推导这些实现项。

要求：

1. 先定义 3-5 个集团企业真实用户场景。
2. 对每个场景写清：用户是谁、要完成什么任务、当前痛点、角色资产如何参与、输入输出是什么、成功标准是什么。
3. 再从场景推导 Scope In / Scope Out，不能从功能清单反推场景。

### P1-1 使用台和 usage_records 设计不够完整

`DD-03 使用台 + usage_records` 实际是产品和数据模型新增，不只是 UI 补齐。当前设计只写“记录使用者、查询、回复和时间”，不足以指导实现。

要求：

1. 明确 usage record 是否冻结 `role_version_id`。
2. 明确是否记录知识来源、分数、LLM 输出、失败记录和使用反馈。
3. 明确使用台与测试台的权限、入口、记录语义和验收边界。
4. 如果新增读写 API，必须先回写 dossier。

### P1-2 资产治理字段过早定死

`category / owner / maintainer / business_domain / visibility` 是合理候选，但当前缺少字段来源、枚举、默认值、展示位置、筛选方式和权限语义说明。

要求：

1. 明确这些字段是“展示与筛选属性”，不暗含 RBAC 或多租户权限能力。
2. 明确字段枚举和默认值。
3. 明确这些字段是否进入版本快照。

### P1-3 v0.4 测试计划尚未同步

`delivery/test-plan.md` 和 `delivery/test-cases.md` 当前仍是 `v0.3.0-commercial-trial`。在进入实现前，必须补 v0.4 草案。

要求：

1. 补 v0.4 的 `delivery/test-plan.md` 和 `delivery/test-cases.md` 草案。
2. 至少覆盖 US-06 到 US-10。
3. 明确哪些是自动化测试、程序化 UI、人工手动冒烟、文档验收。

## 4. 推荐的 Scope 收敛方向

当前主线“角色资产化与使用入口”可以保留，但建议先收敛 P0。

推荐 P0：

1. 角色资产治理属性的最小闭环。
2. `knowledge_boundary` 的 schema/API/UI/详情展示。
3. 使用台最小闭环。
4. 使用记录冻结 `role_version_id`。

建议 P1 / P2：

1. 消费侧 API 设计说明。
2. 执行能力模型定义。
3. 模板库。
4. 历史版本详情入口。
5. 枚举中文映射。

建议暂不纳入：

1. A3 执行动作。
2. 决策产品集成实现。
3. 公共契约变更。
4. RBAC / 多租户 / SaaS。

## 5. 下一步要求

工作方下一步应先补一轮“研究结论修订”，不要写功能代码。

必须完成：

1. 补竞品分析来源和证据。
2. 修正本地能力事实错误。
3. 从 3-5 个集团企业真实用户场景推导 Scope。
4. 收敛 P0 范围。
5. 补 v0.4 的 `delivery/test-plan.md` 和 `delivery/test-cases.md` 草案。

完成后交回规划方复审。复审通过后，再决定是否进入实现。

## 6. 复审结论

结论：有差距，补齐后再进入实现。

当前不批准进入功能实现。

## 7. 第二轮复审补充（基于 2026-05-25 后续修订稿）

### 7.1 当前有效结论

工作方已补第一轮复审提出的 5 项前置材料，但第二轮复核后，当前 dossier 仍未达到“批准进入实现”的标准。

当前有效结论维持不变：

```text
有差距，补齐后再进入实现
```

复审通过前：

1. 不得进入功能代码开发。
2. 不得把 v0.4.0 表述为已进入实现。
3. 不得升级 Formal Status。

### 7.2 本轮未收口问题

#### P0-4 `usage_records` 类型设计仍与当前项目主模型不一致

`design-delta.md` 将 `usage_records.id`、`role_asset_id`、`role_version_id` 设计为 `Integer`，但当前项目 `RoleAsset.id` 与 `RoleVersion.id` 已明确使用 `String(36)` UUID。

证据：

1. `docs/iterations/v0.4.0/design-delta.md` 第 94-96 行
2. `app/models/role_asset.py` 第 15-17 行
3. `app/models/role_version.py` 第 15-17 行

要求：

1. `usage_records` 的主键和外键类型必须与现有 UUID 口径一致。
2. 若仍想改成整数主键，必须先说明为什么要偏离现有全局模型规则，再决定是否允许进入实现。

#### P0-5 `capability_level` 设计仍不完整，无法直接指导实现

当前文档只写了 `RoleCreate / RoleUpdate` 新增 `capability_level`，但未定义：

1. 它是资产级属性还是版本级属性。
2. 是否进入版本快照。
3. 详情读取路径是否包含 `RoleDetail`。
4. 对外读取是否进入 `RoleVersionPublicResponse`。
5. 如果它属于 L4 字段，如何进入当前 EAV 存储与回读链路。

证据：

1. `docs/iterations/v0.4.0/design-delta.md` 第 118-120 行只定义了创建/更新写入口
2. `docs/iterations/v0.4.0/scope.md` 第 93 行把它列为核心场景链成功标准
3. `delivery/test-cases-v0.4.md` 第 111-120 行已开始按“可写可读可展示”编制测试
4. `app/schemas/role.py` 第 34-66 行与第 96-125 行可作为当前 schema 边界事实基线

要求：

1. 明确 `capability_level` 的归属层级与版本语义。
2. 明确 schema、持久化、回读、UI 展示、测试五段链路。
3. 若设计未收口，不得继续把它保留为可实现项。

#### P1-4 竞品与差异化表述仍有绝对化过度声明

虽然补了证据链，但文中仍保留“唯一具备”“已领先市场”等过强表述，超出了当前样本与证据能支撑的力度。

证据：

1. `docs/iterations/v0.4.0/research-conclusion.md` 第 139-142 行
2. `docs/iterations/v0.4.0/design-delta.md` 第 11 行

要求：

1. 统一改为“在当前抽样竞品和已核对证据范围内，具有相对优势”之类的表述。
2. 禁止把当前调研样本外推成“唯一”“所有竞品”“市场已验证领先”等结论。

#### P1-5 `DD-06 角色模板库` 仍被保留在 Scope In 与验收口径中

当前研究文档已明确写出：模板库未被 SC-01 至 SC-04 推导，不构成主线场景需求；但 scope、traceability、test-plan 仍把它保留在 Scope In、US-11 和验收标准中。

证据：

1. `docs/iterations/v0.4.0/research-conclusion.md` 第 255 行
2. `docs/iterations/v0.4.0/scope.md` 第 27、94、117 行
3. `docs/iterations/v0.4.0/traceability.md` 第 18 行
4. `delivery/test-plan-v0.4.md` 第 16 行

要求：

1. 如果模板库不属于本轮真实场景推导结果，应移出 Scope In、验收标准和测试承诺。
2. 如坚持保留，必须补充真实业务场景、商业价值和成功标准，不能只因“已有硬编码模板”而占据本轮范围。

#### P1-6 `delivery/test-plan-v0.4.md` 仍有遗留错误引用

`delivery/test-plan-v0.4.md` 的“文档验收”仍写 `US-09, US-04`，明显残留旧编号，说明 dossier 尚未完全收口。

证据：

1. `delivery/test-plan-v0.4.md` 第 36 行

要求：

1. 修正遗留编号。
2. 全面复核 `scope.md`、`traceability.md`、`test-plan-v0.4.md`、`test-cases-v0.4.md` 的编号一致性。

### 7.3 工作方下一步要求

工作方下一步仍应先修 dossier，不写功能代码。

必须补齐：

1. 修正 `usage_records` 主键/外键类型与现有 UUID 模型的一致性。
2. 收口 `capability_level` 的资产级 / 版本级归属、schema 读写路径和版本语义。
3. 去除竞品分析中的绝对化结论。
4. 将 `DD-06 角色模板库` 移出本轮承诺，或补足真实场景推导后再保留。
5. 修正 `delivery/test-plan-v0.4.md` 的遗留 `US-04` 编号，并复核全套 dossier 一致性。

完成后再交回规划方复审。

## 8. 第三轮复审结论（基于修订后二次提交）

### 8.1 复核结果

本轮针对前述 5 个阻塞项的修订已完成，复核通过。

已确认：

1. `usage_records` 主键与外键类型已统一为 `String(36)` UUID，与现有 `RoleAsset.id`、`RoleVersion.id` 口径一致。
2. `capability_level` 已明确为**版本级属性**，并补齐 schema 写入口、schema 读入口、EAV 持久化、版本快照、前端类型、UI 写入口、UI 读入口以及对外响应排除说明。
3. 竞品差异化表述已收敛到“当前抽样竞品 / 已核对证据范围”口径。
4. `DD-06 角色模板库` 已移出本轮 `Scope In`、追溯矩阵、验收标准和测试承诺。
5. `delivery/test-plan-v0.4.md` 的遗留 `US-04` 编号已修正，当前 dossier 编号一致。

### 8.2 质量门禁复核

本轮复核已重新执行以下命令：

```bash
npm run lint:md
python3 scripts/iteration-guard.py --repo-root . --mode release
./venv/bin/python -m pytest tests -q
cd frontend && npm run build
```

结果：

| 项 | 结果 |
|---|---|
| Markdown lint | PASS，0 errors |
| iteration guard | PASS |
| pytest | PASS，38 passed，8 warnings |
| frontend build | PASS |

说明：当前通过结果证明 dossier 与现有仓库状态未冲突，且基础质量闸门未被破坏。

### 8.3 当前结论

结论更新为：

```text
规划通过，可进入实现
```

允许进入 v0.4.0 功能实现。

同时保持以下约束：

1. `Formal Status` 仍为 `Draft`，不得因规划通过而升级为 `Self-Tested`、`User-Acceptance-Candidate` 或 `Accepted`。
2. 实现过程中如新增接口、改变公共对象、调整读写边界、扩大 Scope In，必须先回写 dossier 再继续。
3. 不得把知识平台当前 Accepted 范围表述为长期冻结公共契约版本。
4. 不得混入决策产品集成实现或 A3 执行动作。

### 8.4 非阻塞建议

建议在进入代码实现前，把 `capability_level` 的“**不进入 `RoleVersionPublicResponse`**”补一条显式测试用例，避免后续开发时无意扩大对外响应范围。该建议不阻塞进入实现。
