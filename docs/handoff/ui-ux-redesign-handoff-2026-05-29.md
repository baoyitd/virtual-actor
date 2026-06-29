# UI/UX 重构工作包交接说明（2026-05-29）

> 项目：`virtual-actor`
> 用途：交给新的工作方承担当前产品的整体 UI/UE/UX 重构优化
> 定位：`Handoff Only`，用于交接和转发，不替代活跃版本真源

## 1. 任务性质

当前产品已经具备基本能力链路，但用户对现有 UI/UE/UX 整体不满意。问题不是单点样式或单页 bug，而是整体产品体感仍偏“后台配置感”，没有充分体现“企业数字角色资产运营平台”的商业化产品气质，也没有足够稳地支撑中国企业用户独立完成关键任务。

这次交接给你的不是“把几个页面美化一下”，而是一项独立的设计工作包：

1. 先完整理解当前产品定位、核心链路、已冻结边界和真实运行态现状。
2. 基于真实页面与真实用户任务，做整体 UI/UE/UX 重构方案。
3. 先出设计包并经复审确认，再进入实现。

## 2. 当前版本状态与版本处理要求

当前活跃版本：

```text
版本：v0.4.0
Formal Status：Self-Tested
Design Freeze Status：Effective
活跃指针：/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/current.txt
```

这意味着：

1. `v0.4.0` 现有设计已经被冻结，不能把整体 UI/UE/UX 重构当成“直接改实现细节”处理。
2. 如果你的方案会改变信息架构、关键页面布局、主流程顺序、关键交互或验收语义，必须先按新设计工作包推进，再决定归入 `v0.4.x` 还是新开版本。
3. 未经规划方确认，不要直接覆写当前 `v0.4.0` 真源文档，把你的新方案写成“当前已确认版本设计”。

版本判断要求：

| 情况 | 建议 |
|---|---|
| 只是视觉润色、文案优化、组件统一，不改页面结构和关键流程 | 可评估按 `v0.4.x` 补强处理 |
| 涉及全局导航、页面信息架构、AI 创建流程、知识绑定方式、资产市场/使用台/看板整体重做 | 通常应评估按新迭代处理 |

以上只是判断口径示例，不是预设结论。你需要基于影响范围自行判断这次工作更适合归入 `v0.4.x` 还是新版本，并写明理由。

## 3. 你必须先读的文件

先按以下顺序阅读，不要跳过：

### 3.1 项目级规则

```text
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/process/project-rules.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/current.txt
```

### 3.2 当前活跃版本真源

```text
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/README.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/scope.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/design-delta.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/traceability.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/ui-ux-wireframes.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/task-flows-acceptance-and-design-freeze.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/implementation-notes.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/acceptance-review-framework.md
```

### 3.3 如需核对当前实现边界，可参考的前端代码入口

```text
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/App.tsx
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/components/Layout.tsx
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/pages/RoleList.tsx
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/pages/RoleDetail.tsx
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/pages/RoleEdit.tsx
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/pages/RoleTest.tsx
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/pages/UsageDesk.tsx
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/pages/Marketplace.tsx
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/pages/Dashboard.tsx
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/pages/RoleVersions.tsx
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/components/StructuredResultDisplay.tsx
/Users/baoyi/Documents/code_buddy/virtual-actor/frontend/src/index.css
```

上述代码入口用于帮助你理解“当前已经做了什么、哪些地方可复用、哪些地方存在实现约束”，不是要求你按现有页面结构做局部修补。

## 4. 当前本地运行态入口

当前本地服务可达：

```text
URL: http://127.0.0.1:8000/
Health: GET /health -> {"status":"ok","service":"virtual-actor","version":"0.4.0"}
登录账号：admin
登录密码：admin123
```

如你能直接访问当前服务，优先跑真实页面完成现状审计。

如你无法直接访问当前服务，则改为使用以下现状参考包辅助理解：

```text
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/handoff/ui-ux-current-ui-reference-2026-05-29.md
```

其中的截图和说明只用于帮助你理解“当前产品长什么样、问题大致在哪里”，**不是**让你引用现有样式、布局、交互或页面骨架。你的新方案仍应优先基于项目定位、产品目标、PRD/真源设计和用户任务本质来重做。

## 5. 当前页面与路由清单

当前正式前端入口是 React，由 FastAPI 托管。主要路由如下：

| 路由 | 页面 | 代码文件 | 当前职责 |
|---|---|---|---|
| `/` | 角色资产列表 | `RoleList.tsx` | 列表、筛选、入口分发 |
| `/roles/:id` | 角色详情 | `RoleDetail.tsx` | 资产详情、状态和操作入口 |
| `/roles/:id/edit` | 角色编辑 | `RoleEdit.tsx` | 手动创建、AI 创建、业务配置、知识绑定 |
| `/roles/:id/test` | 测试台 | `RoleTest.tsx` | 测试、评分、历史 |
| `/roles/:id/use` | 使用台 | `UsageDesk.tsx` | published 角色消费结果 |
| `/roles/:id/versions` | 版本列表/详情 | `RoleVersions.tsx` | 历史版本查看 |
| `/create` | 新建角色 | `RoleEdit.tsx` | 创建入口 |
| `/marketplace` | 资产市场 | `Marketplace.tsx` | 业务发现、AI 推荐、试用入口 |
| `/dashboard` | 运营看板 | `Dashboard.tsx` | 运营数据总览 |

全局布局入口：

| 文件 | 当前职责 |
|---|---|
| `Layout.tsx` | 侧边导航、品牌区、用户区 |
| `App.tsx` | 登录、路由、鉴权切换 |

## 6. 本次重构要解决的核心问题

请把以下问题当成核心任务，而不是“可选优化”：

1. **整体产品气质不足**：现状仍偏工具后台，不够稳重，不够商务，不够像中国企业内部会长期使用的产品。
2. **全局视觉语言不统一**：登录、列表、表单、市场、结果页、看板之间还没有形成足够统一的品牌感、层级感和组件规范。
3. **角色创建/编辑认知负担仍偏高**：虽然已补字段解释和模板，但整体仍是较重的表单型体验，用户仍需要理解很多配置项，AI 原生感不够强。
4. **知识绑定在大规模内容下的体验仍是重点风险**：需要从信息架构、筛选、目录浏览、批量选择、回显和理解成本角度整体优化，而不是只看“能选”。
5. **资产市场的业务发现感还不够强**：当前已有场景卡片和 AI 推荐，但“发现角色资产”的产品表现力仍偏弱，缺少足够明确的业务入口和消费信心建立。
6. **测试台/使用台的结果表达需要持续加强**：用户需要快速读懂 status、boundary、structured_result、sources，而不是“有数据但看起来仍偏技术化”。
7. **运营看板的商业表达仍不足**：现状更像统计页，不够像帮助运营方判断“资产是否被创建、使用、信任、淘汰、补齐”的经营界面。
8. **跨页面操作节奏需要重新收口**：创建、保存、发布、返回、取消、继续编辑、进入测试/使用等动作需要更稳定、更符合 human 习惯。

以上 8 点是当前交接方已经识别出的核心问题，不要求你沿用完全相同的问题分类。如果你认为存在更本质的上层问题，可以重新归纳，但不能绕开这些问题所对应的真实缺口。

## 7. 设计目标

你输出的新方案，必须同时满足以下目标：

1. 面向中国企业用户，风格稳重、商务、专业，不做泛互联网娱乐化设计。
2. 桌面优先，兼容平板宽度；信息密度适中，可长期操作。
3. 用户在没有口头指导的前提下，能独立完成关键任务。
4. 体验上应体现“AI 原生产品”，不是“传统后台表单 + 局部 AI 按钮”。
5. 要体现“企业数字角色资产运营平台”的定位，而不是普通角色配置工具。

## 8. 你不能改变的边界

以下内容不是这次 UI/UX 重构可以自行改掉的：

1. 核心主链路仍是：`AI 创建 -> 资产治理 -> 测试发布 -> 统一消费 -> 运营证据`
2. `DD-14` 决策产品真实集成不得被降级或移出
3. `DD-16` 的 6 状态和 `boundary_status` 语义不得自行改写
4. 4 类业务输出模板、版本快照规则、发布不可覆写规则不得自行改写
5. `visibility` 等治理字段不带权限语义，不得自行扩成访问控制
6. `prototype/` 不是正式验收入口，正式入口仍是 React
7. 知识平台必须是真实集成，不得引入 mock/stub/fixture 冒充
8. `A3` 执行动作仍不纳入本轮默认实现

如果你认为上述边界本身需要调整，不能直接改设计或写代码，必须先回传质疑和理由。

## 9. 你必须提交的设计产物

在进入实现前，至少覆盖以下 8 类内容。具体交付形式可以等价替换为文档、原型、线框图、注释页面或汇报材料：

1. **当前运行态 UI/UX 审计**
   - 覆盖全部关键页面
   - 不是只列 bug，要说明“为什么不满足当前产品定位和用户任务”
   - 需区分 P0/P1/P2
2. **版本处理建议**
   - 明确建议按 `v0.4.x` 还是新版本处理
   - 说明理由和影响范围
3. **新的信息架构与导航方案**
   - 页面分组、入口关系、主导航、次导航、关键跳转路径
4. **全局视觉系统提案**
   - 配色方向、字体/字重层级、卡片/表格/表单/标签/弹窗/空态/错误态/加载态规范
5. **关键页面线框图或原型**
   - 至少覆盖：登录、角色列表、角色详情、角色创建/编辑、知识绑定、测试台、使用台、资产市场、运营看板
6. **交互与文案策略**
   - 字段说明、示例写法、按钮顺序、确认弹窗、错误恢复、AI 生成内容标识、长文本阅读策略
7. **实现切分方案**
   - 哪些属于 P0 本轮必须做
   - 哪些属于 P1/P2 可后续迭代
8. **dossier 回写计划**
   - 如果采用你的方案，需要更新哪些真源文件、哪些测试和验收材料

## 10. 输出位置要求

在方案未通过前，不要直接把新方案写进当前 `v0.4.0` 真源。

建议输出方式：

1. 先在 `docs/handoff/` 或新的提案文档中提交审计和设计提案
2. 经过复审确认后，再决定：
   - 若只是补强：回写到对应新子版本 dossier
   - 若是整体重构：新开版本 dossier，再回写设计真源

## 11. 工作方式要求

请按以下方式推进：

1. 先读真源，再看运行态，再看代码，不要反过来。
2. 先做问题抽象和设计收口，不要直接开始编码。
3. 如果你对当前定位、边界、设计冻结或版本划分有不同意见，可以提出质疑。
4. 但提出质疑时，必须给出完整理由、影响范围和替代方案，不能只说“建议改”。
5. 本轮是共创完善，不是机械执行；但也不是自由发挥，必须尊重现有真源和治理边界。
6. 不要把当前页面当成“应该被优化的基础稿”。如果你判断当前方案本身就不成立，应直接回到产品目标和用户任务本质重做。

## 12. 交付底线

这次交接的目标，不是做出一套“更好看”的界面，而是要产出一套能支撑后续实现、能减少返工、能让用户真正更容易使用的设计方案。

如果你的方案不能清晰回答以下问题，就不算完成：

1. 用户为什么会更容易完成任务？
2. 为什么这套体验更符合中国企业的商务使用场景？
3. 为什么它更能体现“角色资产运营平台”的产品定位？
4. 为什么它不会再次在实现阶段大幅漂移？
