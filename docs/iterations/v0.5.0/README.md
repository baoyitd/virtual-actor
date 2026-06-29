# v0.5.0 文档结构治理索引

> 版本：v0.5.0 | 日期：2026-06-11 | Formal Status：Self-Tested
> 用途：v0.5 唯一入口索引，明确当前需求真源、输入边界和进入实现前的冻结要求

---

## 当前状态

| 维度 | 状态 |
|---|---|
| Formal Status | Self-Tested |
| Design Freeze Status | Effective（2026-06-10 终审确认） |
| 是否允许代码实现 | 是 |
| 当前真源 | 本索引 + 下方 Current Source of Truth |
| 当前需求主线 | 角色定义层重构（含 `L3` 数据能力、`L4` 输出方式 + 运行配置）+ 消费契约独立 + 外部复用准备 + 创建编辑降门槛 |
| 基线版本 | `v0.4.0` 已有实现与交付基线，作为本轮产品和工程参考 |

## Current Source of Truth

以下文件构成 v0.5 当前有效需求真源。未列入的材料不得替代本轮阶段口径。

### 1. 需求与范围

| 文件 | 内容 | 优先级 |
|---|---|---|
| `requirements-analysis.md` | 已完成 2026-06-09 用户逐项复审的需求分析结论 | P0 |
| `scope.md` | 与需求分析同步后的 v0.5 范围、场景链、非目标和阶段退出标准 | P0 |
| `requirements-checklist.md` | 需求清单 + 边界清单，供后续设计评审和工作方核对使用 | P0 |
| `design-delta.md` | 已按最新 `L3/L4` 需求共识同步后的设计增量真源 | P0 |
| `traceability.md` | 已按最新需求共识同步后的需求-设计-测试追溯矩阵 | P0 |

### 2. UI/UX 与设计管理

| 文件 | 内容 | 说明 |
|---|---|---|
| `task-flows-acceptance-and-design-freeze.md` | 核心任务流、验收点、Human 检查清单、设计冻结规则 | 已同步 |
| `ui-ux-wireframes.md` | 关键页面低保真线框 | 已同步 |
| `high-fidelity-prototype-scope.md` | 设计冻结前必须补齐的高保真原型范围与评审要求 | 已同步 |
| `prototype/v0.5-hifi/` | v0.5 高保真静态原型 | 已完成终审确认，作为冻结版高保真原型 |

### 3. 测试计划

| 文件 | 内容 | 说明 |
|---|---|---|
| `/delivery/test-plan-v0.5.md` | v0.5 测试范围、测试类型、质量门禁 | 已同步 |
| `/delivery/test-cases-v0.5.md` | v0.5 详细测试用例 | 已同步 |
| `/delivery/test-results-v0.5.md` | v0.5 工作方预检结果 | 已同步 |
| `/delivery/tester-handoff-v0.5.md` | v0.5 测试方交接说明 | 已同步 |

### 4. 实施管理

| 文件 | 内容 | 说明 |
|---|---|---|
| `implementation-plan.md` | v0.5 实施拆分、批次顺序、进入下一批条件、并行治理线 | 当前实现准备与排期基线 |
| `implementation-notes.md` | 设计冻结后的偏差记录与关键落地说明 | 偏差管理入口 |

## 当前实现阶段判断

截至 `2026-06-11`：

1. `v0.5.0` 代码主链路已实现，工作方预检已完成。
2. 当前已补齐自动化测试、程序化浏览器烟测、工作方预检材料，以及测试方本地独立复核结果。
3. 测试方已确认：平台内主链路、运行效果、浏览器 / Human UI 基本过关。
4. `Codex` 代表环境已完成隔离 fresh session 安装与真实调用验证。
5. `Dify` 代表环境已通过本地真实环境完成 `Tool package` 导入、真实调用和平台侧 `usage_record` / `role_version_id` / `status` / `boundary_status` 对账闭合。
6. `Formal Status` 已升级为 `Self-Tested`，当前可进入最终用户测试；但 `v0.3.0-commercial-trial` 仍是唯一 `Accepted` 对外交付基线。

## 本轮设计焦点

当前版本已冻结并实现两个核心判断：

> **第一，把上位项目对“角色由哪些部分组成”的逻辑框架吸收到当前 `RoleAsset + RoleVersion` 产品模型中。**
>
> **第二，把合适的已发布角色版本变成可被外部 AI 环境稳定复用的供给物。**

这意味着：

1. 当前要加强的是角色资产本身，而不是额外新增一层“定义包中心”或“输入对象管理中心”。
2. 当前要优先回答的是“角色规格如何更完整、更易填写、更可发布、更可复用”。
3. 当前要同时回答“平台如何把已发布角色版本稳定供给给外部 AI 环境复用”。
4. 当前角色新建 / 编辑体验必须同步降门槛，不能把新增 requirement 继续堆到长瀑布表单上。
5. 外部分发形态、动作执行治理等议题，仍可继续讨论，但不应反向驱动本轮先把产品做重。

## 外部设计输入

以下文件是本轮设计输入，但不是平台内部真源，不得直接当实现规格照搬：

| 文件 | 角色 |
|---|---|
| 上游 `va-platform-role-asset-validation-handoff.md` | 验证型 handoff 主文档 |
| 上游 `role-asset-framework.md` | 角色资产定义、职责簇边界 |
| 上游 `ai-agent-capability-design-sop.md` | 六类资产与角色设计包方法 |
| 上游 `terminology-standard.md` | 术语边界 |
| `docs/iterations/v0.4.0/README.md` 与 v0.4 真源 | 当前实现与产品基线 |

## 执行要求

1. 上游 handoff 当前仍是验证型输入，不等于平台必须新增一个一等对象。
2. 平台当前核心对象仍是 `RoleAsset + RoleVersion`；v0.5 优先在这个骨架上吸收角色构成框架。
3. 若设计开始显著走向“额外新增定义包中心 / 翻译工作台 / 独立输入层对象”，必须先停下复审。
4. 六类资产的吸收应优先复用现有知识绑定、模型绑定、测试与版本机制，而不是默认拆成六套新子系统。
5. “负责什么 / 不负责什么”不作为本轮单独 requirement 回灌进产品结构。
6. 外部供给形态当前只先收口 `Tool package` 与 `Skill package`，并建立在现有 `consume API` 之上。
7. 角色新建 / 编辑交互重设计属于本轮 P0 requirement，不能被降级为纯视觉换肤。
8. 当前文档、原型与测试真源已通过 Design Freeze 终审，后续实现必须按冻结口径推进。
9. 若后续再调整 `L3 / L4 / 数据资产管理 / 外供说明` 口径，必须先回写真源文档，再继续原型评审。
10. 当前已允许进入代码实现准备与实现；但未登记偏差、未回写真源的设计变更不得直接落入实现。

## 下一步流程

```text
上游新输入进入
  -> v0.5 requirements-analysis
  -> v0.5 scope
  -> 回写同步 design / traceability / UI / tests
  -> 用户逐项设计评审
  -> 高保真原型继续校准
  -> Design Freeze Status = Effective
  -> 进入代码实现与自测
  -> 工作方预检
  -> 测试方独立复核
  -> Codex 代表环境真实验证已闭合
  -> Dify 代表环境真实验证已闭合
  -> Formal Status = Self-Tested
  -> 用户测试 / 验收
```
