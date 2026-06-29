# virtual-actor 项目规则

> 适用项目：`virtual-actor`
> 定位：本项目的项目级流程与治理规则入口文档，不替代活跃版本 dossier、活跃交付证据或版本真源。
> 建立日期：2026-05-28
> 来源：整合 product-iteration-control.md、rule-changelog.md、issue-and-optimization-log.md、scope.md §6/§8、design-delta.md §5、acceptance-review-framework.md、consume-api-design.md、business-output-templates-and-status-rules.md、traceability.md、planning-response、mvp-requirements-consensus、dd10-spec 等文档中的规则项
> 规则变更记录：见 `rule-changelog.md`（R-001~R-002）；问题台账：见 `issue-and-optimization-log.md`（IO-001~IO-005）

---

## 使用边界与启动顺序

### 本文件的职责边界

- 本文件只定义项目级流程规则、治理红线、状态口径和通用执行要求。
- 本文件不是当前产品范围、交互设计、实现增量、测试范围或交付状态的唯一真源。
- 活跃版本的产品真源始终以 `docs/iterations/current.txt` 指向的版本 dossier 和该版本 README 中列出的 Current Source of Truth 为准。
- 若本文件与活跃版本 dossier 表述不一致，先核对是否为规则层 vs 版本层差异；若仍冲突，停止默认实现并上提规划方裁决。

### 每次新对话的强制读取顺序

1. 先读 `docs/process/project-rules.md`，建立项目级流程和治理边界（含 P 章代码实现红线）。
2. 再读 `docs/handoff/project-handoff-to-codebuddy-2026-06-24.md`，确认项目交接状态与技术注意事项。
3. 再读 `docs/iterations/current.txt`，确认当前活跃版本。
4. 再读活跃版本 `scope.md`（作为版本入口）、`design-delta.md`、`implementation-notes.md`、`traceability.md`，确认当前版本的范围、冻结边界、设计增量和追溯关系。若该版本目录有 `README.md`，优先以 README 列出的 Current Source of Truth 清单为准。
5. 最后读 `delivery/` 下的交付与验收真源文件：`release-notes.md`、`known-issues.md`、`test-results.md`、`portfolio-sync.md`。

### 禁止误用

- 不得把“已加载 `project-rules.md`”表述成“已掌握当前活跃版本全部真源”。
- 不得只读取本文件就进入设计、实现、验收表述或状态升级判断。
- 不得用项目级规则入口替代活跃版本 dossier 的具体产品定义。

---

## A. 设计先行与流程规则

### A-01 设计先行：不在设计未收口时直接编码

进入实现前必须完成 scope.md、design-delta.md、测试用例草案。设计未收口时不得直接编码。

**来源**：scope.md §6-1、product-iteration-control.md §3-2

### A-02 设计冻结后不得自行改变关键交互

设计冻结后，不得自行改变关键交互、信息架构、流程顺序或验收语义。偏差需提交偏差说明并经规划方/终审方确认。

**来源**：scope.md §6-11、§8-1、design-delta.md §5-9、planning-response §3.6-1

### A-03 复审/整改/裁决等外部输入是设计输入，不是已收口设计规格

收到复审退回整改要求、规划方裁决或终审方意见后，必须先回写 design-delta.md、scope.md、traceability.md 等设计文档，再进入代码实现。"先改代码后补文档"不属于设计先行流程。

**来源**：R-002 (2026-05-28)、IO-005、product-iteration-control.md §3-4

### A-04 实现中发现设计变更时先回写 dossier

实现中出现 scope 扩大、接口新增、字段不足、页面路径变化时，先回写 dossier 再继续实现。

**来源**：product-iteration-control.md §3-3

### A-05 UI/UX 硬约束：进入实现前必须完成原型和冻结记录

进入实现前必须完成 UI/UX 原型、用户任务流、场景走查、验收点、Human 检查清单和设计冻结记录。不允许"文档/API 先行、UI 后补"。

**来源**：scope.md §6-10、design-delta.md §5-9、planning-response §3.6

### A-06 论证从本质出发，不为已有成果找理由

讨论任何设计或实现的合理性时，必须从事物本质、项目目标、用户场景和价值出发推导结论，不得以"已经这样做了"、"代码里已经有了"、"之前就是这样设计的"作为辩护理由。已有成果可以被推翻，只要本质论证不支持它。

**来源**：R-003 (2026-06-17)

### A-07 收到指令后先反馈理解、异议、优化，不默认执行

收到指令或讨论内容后，处理顺序为：(1) 反馈理解——复述理解到的内容确认无偏差；(2) 提出异议——如有疑问或认为存在问题先指出；(3) 提出优化方案——如看到更好路径给出建议；(4) 得到确认后再执行。不得走"收到→执行"的单向流程。

**来源**：R-003 (2026-06-17)

### A-08 不得把候选需求写成已承诺交付

候选需求不得表述为已承诺交付。发布说明写了某项能力"已支持"但没有实现和证据映射时，不得对外表述为已完成。

**来源**：scope.md §6-2、traceability.md 规则-3

### A-09 UI调整与设计变更的判定边界

设计冻结后，对前端界面的改动按以下标准判定是否需要走设计变更流程：

**不需要走流程（纯UI调整）**：颜色、间距、字体、圆角、图标选择、文案微调（不影响语义）、hover/focus等视觉反馈、组件内部视觉优化——**不改变用户完成任务的步骤数和方式**。

**需要走设计变更流程（设计变更）**：

1. **信息架构变化**：section 顺序调整、信息密度变化（如从展开卡片改为折叠行）、移除或新增信息展示区域
2. **核心动作位置变化**：主要操作按钮（如发布、生成、保存）在页面中的位置改变
3. **交互元素增减**：新增或移除按钮、入口、表单字段
4. **任务流程变化**：改变用户完成某个任务的步骤

**判定原则**：用户完成任务的方式是否发生了变化。变化了就是设计变更，不变就是纯UI调整。

**判定责任**：遇到不确定的情况，默认按"设计变更"处理，由产品方确认是否可简化——不得自行判断为"UI调整"跳过流程。

**来源**：A-02 补充细则（2026-06-17）

### A-10 不自行把已确认的产品本质降级为较弱交付

不得因执行难度、工程工作量或短期交付压力反向驱动改变产品本质目标。实现分批不得改变产品方向。

**来源**：scope.md §6-3、design-delta.md §5-8、mvp-consensus §1-2/§5、planning-response §1-5/§6

### A-11 外部反馈不默认执行，先形成方案共识

收到用户、审核方、规划方或任何外部方的反馈、意见、建议、调整要求时，不得默认执行。处理顺序为：(1) 理解——复述反馈核心内容；(2) 总结——梳理反馈涉及的范围和影响；(3) 反馈——提出评估意见（合适/不合适/需调整）和方案；(4) 与用户共识——用户确认方案后再执行。

**来源**：用户补充（2026-06-26），与 A-07 互补——A-07 约束所有指令的处理方式，A-11 专门约束外部反馈的处理方式

---

## B. 状态与版本控制规则

### B-01 Formal Status 只使用 4 个值

对外只使用 `Draft`、`Self-Tested`、`User-Acceptance-Candidate`、`Accepted`。其他表述只能作为范围说明，不能替代 Formal Status。

**来源**：product-iteration-control.md §1

### B-02 未通过质量门禁前不得越级表述

未通过质量门禁前，不得把版本表述为 `User-Acceptance-Candidate`、`Accepted` 或上线完成。Self-Tested 不是复审豁免；运行态复查失败时声明证据视为无效。

**来源**：product-iteration-control.md §3-5、acceptance-review §4.2

### B-03 每个版本必须有独立 dossier

每个版本必须有 `docs/iterations/<version>/` 下的 scope.md、design-delta.md、implementation-notes.md、traceability.md。新版本先初始化 dossier 并确认 current.txt 指向当前活跃版本。

**来源**：product-iteration-control.md §2-§3-1

### B-04 dossier 各文件最低要求

- scope.md 写清 Scope In/Out、核心用户场景、非目标和停止条件
- design-delta.md 只写增量设计，不重写全量产品说明
- implementation-notes.md 记录偏差、原因、用户影响和补测要求
- traceability.md 把场景、设计、实现、测试证据和发布口径串起来

**来源**：product-iteration-control.md §2

### B-05 版本快照不可追溯修改

已 published 版本快照不得追溯修改。已 published 角色的 output_type/output_schema/capability_level/applicable_scenarios 不得直接覆写，需提示创建新版本。

**来源**：design-delta.md §3.7-1、version-snapshot §4.1-2、dd10-spec §4.2-3

### B-06 usage_records 必须冻结 role_version_id

usage_records 冻结的 role_version_id 不可变更。当前版本不记录 LLM 输出元数据（model_name/token usage/latency）和失败记录。当前版本不实现使用反馈评分。

**来源**：design-delta.md §3.3、consume-api-design §5

### B-07 使用台与测试台完全分离

使用记录和测试记录在 UI 和数据层面完全区分：不同页面、不同数据表、不同 API。使用台 UI 仅对 published 角色显示入口。

**来源**：design-delta.md §3.3、test-desk-upgrade §3.1.5

---

## C. 证据与验收规则

### C-01 不得把 mock/stub/fixture 描述为真实集成证据

mock、stub、static fixture、manual fixture 或代码走查不得被描述为 `real integration`。证据高于口头声明。

**来源**：scope.md §6-8/§3-10/§8-5、product-iteration-control.md §4-4、acceptance-review §2-6

### C-02 交付证据必须基于真实运行态

真实运行态高于仓库态。"代码看起来已修复"不得替代"当前服务已生效"。证据标注必须与真实情况一致，不得以代码走查标 PASS。

**来源**：acceptance-review §2-2、IO-005 处理说明

### C-03 运行态验收标准高于仓库态

当前实际验收环境运行版本是标准。仓库代码状态不得替代运行态验证。工程通过 ≠ 验收通过。

**来源**：acceptance-review §2-1/2

### C-04 验收前必须运行 iteration-guard.py

验收前运行 iteration-guard.py，核对 delivery/、portfolio-sync.md 和当前 dossier 是否一致。

**来源**：product-iteration-control.md §3

### C-05 交付前人工冒烟 + 偏差清单

交付前必须完成人工冒烟（覆盖高风险核心用户路径），记录操作人、时间、环境、步骤、预期/实际/结果。无偏差清单 = 设计一致性检查未完成。

**来源**：scope.md §7-10、task-flows §5.4、planning-response §3.6

### C-06 新增高风险场景时先补追溯关系

新增高风险场景时必须先补追溯关系再开始实现。修复 P1 问题时必须补对应回归用例。

**来源**：traceability.md 规则-1/2

---

## D. 不降级与不移出规则

### D-01 DD-14 决策产品集成的范围口径

决策产品集成已正式暂缓至独立后续计划（见 v0.5.1 release-notes），不在当前版本验收范围内。后续启动时需另开 dossier。在决策产品集成独立计划完成前，不得声明决策产品集成已通过。若外部配合延期则记录为外部阻塞，不得自动降级为"角色产品侧就绪"。

**来源**：scope.md §2-DD-14/§6-6/§7-5/§9、design-delta.md §5-4、traceability.md 规则-5、planning-response §2.1/§6、acceptance-review §4.2-3/§5-2、v0.5.1 release-notes

### D-02 DD-16 不得降级为 4 状态

6 状态（success/insufficient_context/insufficient_knowledge/boundary_blocked/system_failed/undefined）固定交付，不得降级为 4 状态验收。保守判定策略允许但不移除交付语义。

**来源**：scope.md §2-DD-16/§6-7/§7-7、design-delta.md §5-5、traceability.md 规则-6、planning-response §3.2、acceptance-review §5-4

### D-03 不得把产品本质降级为较弱交付

与 A-10 互为补充：实现分批不得改变产品方向。MVP 主链路（AI 创建→资产治理→测试发布→统一消费→运营证据）不得在设计层面缩减。

**来源**：scope.md §6-3、mvp-consensus §5

---

## E. 公共契约与边界规则

### E-01 不新增或修改跨项目公共契约（角色产品内部候选接口除外）

角色产品内部候选接口不等同于冻结跨项目公共契约。consume API、boundary_status/status 字段、业务输出 Schema、角色资产概念——如需跨项目稳定依赖，必须上提公共契约裁决。

**来源**：scope.md §6-4、design-delta.md §5-1~4/§6、consume-api-design §8、business-output §5、planning-response §2.2

### E-02 不得把知识平台 Accepted 表述为长期冻结公共契约

知识平台当前 Accepted 仅覆盖当前范围，不得被误写成长期冻结或稳定可冻结公共契约版本。

**来源**：scope.md §6-9、design-delta.md §5-7、product-iteration-control.md §4 相关、IO-003

### E-03 portfolio-sync.md 必须标注接口候选状态

portfolio-sync.md 必须把 Interface Delta 标注为候选或待裁决状态，不得写为 Accepted 公共契约。

**来源**：consume-api-design §8-4、planning-response §2.2-4

### E-04 消费触发公共契约裁决时必须停止并上提

统一消费 API 触发公共契约裁决要求时，必须停止相关实现并上提。

**来源**：scope.md §8-2

---

## F. 止损与停止条件

### F-01 实现偏离冻结设计时必须提交偏差说明

实现偏离冻结设计（关键交互、信息架构、流程顺序、验收语义）时必须提交偏差说明并经规划方/终审方确认。

**来源**：scope.md §8-1

### F-02 需要新增/修改公共契约时必须停止实现

需要新增或修改公共契约、跨项目依赖边界、读写边界、版本规则时，必须停止默认实现并上提。

**来源**：product-iteration-control.md §4-1、scope.md §8-2

### F-03 决策产品集成发现公共契约问题时必须上提

决策产品集成（已暂缓至独立后续计划）启动后，若过程中发现公共契约、读写边界或版本规则问题，必须上提治理裁决。

**来源**：scope.md §8-3

### F-04 执行能力定义涉及工具权限时必须先上提裁决

执行能力定义涉及工具权限或跨系统调用设计时，必须先上提裁决。

**来源**：scope.md §8-4

### F-05 真实集成能力低于发布说明时必须停止

真实集成能力低于 release notes 或 portfolio-sync 的表述时必须停止。

**来源**：product-iteration-control.md §4-2

### F-06 人工冒烟缺失但版本表述为已验收时必须停止

人工手动冒烟缺失但版本被表述为已验收或可交付时必须停止。

**来源**：product-iteration-control.md §4-3

### F-07 决策产品集成不得混入角色产品+知识平台验收

决策产品集成被混入当前角色产品 + 知识平台验收范围时必须停止。

**来源**：product-iteration-control.md §4-5

---

## G. Scope Out 规则（当前不实现）

### G-01 不实现 A3 执行动作

A3 执行动作的实现风险高，需跨项目裁决。UI 标注"当前不实现 A3 执行机制"。

**来源**：scope.md §3-1/§6-5、design-delta.md §3.4/§5-3

### G-02 不实现 RBAC / 多租户 / SaaS

RBAC / 多租户 / SaaS 继续生效 v0.3 Scope Out。资产治理属性（分类、可见范围等）仅展示与筛选，不暗含 RBAC 或访问控制能力。当前版本不基于 visibility 实现任何访问控制逻辑。

**来源**：scope.md §3-2、design-delta.md §3.1

### G-03 不实现角色模板库

角色模板库不作为当前版本验收项。

**来源**：scope.md §3-3

### G-04 不实现多角色协作编排

只定义概念，不实现委派或编排机制。

**来源**：scope.md §3-4

### G-05 不实现消费权限校验（基于 visibility）

需公共契约裁决，当前版本不实现。

**来源**：scope.md §3-5

### G-06 不实现消费侧 API 版本化（/v1/ 前缀）

当前版本不实现。

**来源**：scope.md §3-6

### G-07 不实现流式输出（SSE/WebSocket）

当前版本不实现。

**来源**：scope.md §3-7

### G-08 不实现 MCP/A2A 协议适配

当前版本不实现。

**来源**：scope.md §3-8

### G-09 不实现自定义字段配置 UI

自定义字段配置 UI 为后续增强。当前版本不支持自定义 Schema。

**来源**：scope.md §3-9、business-output §1.7、dd10-spec §2.1

---

## H. 数据与字段规则

### H-01 资产级属性不进入版本快照

category、owner、maintainer、business_domain、visibility 为 RoleAsset 级属性，不进入版本快照，不随版本内容保存。如上位治理要求纳入公共对象或赋予权限语义，必须先上提裁决。

**来源**：design-delta.md §3.1

### H-02 capability_level 是版本级属性，进入版本快照

capability_level 随 RoleVersionField EAV 存储，版本发布时一并冻结。默认 A1。v0.4 不纳入 RoleVersionPublicResponse（消费侧 API 不暴露内部能力层级标注）。

**来源**：design-delta.md §3.4

### H-03 applicable_scenarios / output_type / output_schema 进入版本快照

applicable_scenarios (L1_IDENTITY)、output_type (L5_CONFIG)、output_schema (L5_CONFIG) 进入版本快照。

**来源**：design-delta.md §3.6

### H-04 creation_source 是资产级属性，不进入版本快照

creation_source（manual/ai_assisted）为 RoleAsset 级属性。AI 草案保存时必须自动标记为 ai_assisted。

**来源**：design-delta.md §3.1、dd10-spec §4.1

### H-05 已 published 角色下次发布前必须补填 output_type/output_schema

已 published 角色下次发布新版本前必须补填 output_type/output_schema。output_type 发布前必填（4 合法枚举值之一），output_schema 发布前必填（非空合法 JSON）。

**来源**：design-delta.md §3.7-5、version-snapshot §2.4/§4.2

### H-06 Legacy 角色限制

缺少 output_type/output_schema 的已 published 角色（v0.3 遗留）：

- 不得进入资产市场正式消费路径、Dify 消费、决策产品消费
- 仅可在使用台被 human 消费（caller_type: human），结果必须标注降级提示
- Dify/决策产品调用 consume API 时返回 HTTP 400，不得返回 fallback success + 空 structured_result
- 资产市场展示遗留角色时标注"需要升级"，不提供试用和消费入口

**来源**：version-snapshot §4.3、consume-api-design §7.1

### H-07 缺失 capability_level 时的拒绝规则

缺失 capability_level 的角色：human 按 A1 处理；agent_platform/decision_product 应拒绝（HTTP 400）。

**来源**：consume-api-design §7.1、implementation-notes D-6A

---

## I. 消费 API 规则

### I-01 每次消费必须返回治理外壳

HTTP 200 时必须返回固定治理外壳（answer, role_id, role_version_id, usage_record_id, created_at, sources, boundary_status, output_type, structured_result, status, status_reason）。

**来源**：consume-api-design §4.1

### I-02 6 状态判定与 boundary_status 联动规则

| status | boundary_status 要求 |
|---|---|
| success | 两个维度不得为 out_of_scope |
| boundary_blocked | 至少一个维度为 out_of_scope |
| insufficient_context | 两个维度为 within_boundary |
| insufficient_knowledge | knowledge 为 near_boundary/within_boundary，capability 为 within_boundary |
| system_failed / undefined | 两个维度为 not_applicable |

保守判定策略：LLM 置信不足时优先降入 undefined。near_boundary 注释 ≠ 越界，answer 必须告知结果局限。

**来源**：business-output §3.2/§3.3、consume-api-design §4.3

### I-03 HTTP 状态码与治理外壳的关系

- HTTP 200：返回治理外壳 + 生成 usage_record + 计入 6 状态统计（status 可为任何 6 状态含 boundary_blocked/system_failed）
- HTTP 400/403/404：不返回治理外壳、不生成 usage_record、不计入 6 状态统计
- HTTP 500：未捕获异常，系统无法生成治理外壳，不计入 6 状态统计，应单独计入"服务可用性异常"

**来源**：consume-api-design §7

### I-04 消费版本归属校验

consume 传入 role_version_id 时必须校验：版本归属（role_version_id 必须属于 role_id）和可消费状态（is_deprecated 为 False）。不满足时返回 HTTP 400，不返回治理外壳、不生成 usage_record。

**来源**：consume-api-design §3.2、implementation-notes D-12A

### I-05 请求级 output_type 可覆盖版本配置

ConsumeRequest.output_type 为可选字段；不填时使用角色版本配置的默认 output_type；传值时使用请求指定值。

**来源**：consume-api-design §3.1、implementation-notes D-12B

### I-06 非 success 状态的消费方处理规则

非 success 不得被消费方当作正常业务结论继续流转。undefined 是兜底和复查信号，不得长期大量使用。每次消费必须返回 status 和 status_reason。

**来源**：consume-api-design §4.3

### I-07 test-consume 是内部接口，不纳入公共契约边界

test-consume 接口不得直接调用 consume API 消费 test 版本角色。consume API 只允许 published 版本。test-consume 不等于公共契约接口。

**来源**：test-desk-upgrade §2.1

### I-08 Dify 消费证明不得泛化为"所有开放平台已支持"

Dify 集成验证只证明"一个开放 Agent 平台可以消费 published 角色资产"，不得推论为所有开放平台均已支持。

**来源**：consume-api-design §8-5

---

## J. 业务输出与模板规则

### J-01 4 内置模板字段定义是 v0.4 内部设计定义

模板字段定义、boundary_status 枚举值、联动规则均为 v0.4 角色产品内部设计定义，不等于冻结跨项目公共契约。消费方如需稳定依赖字段结构或枚举值，必须上提公共契约裁决。

**来源**：business-output §5

### J-02 references 是所有模板必填项

所有模板的 references 必填——消费输出必须有可追溯证据，这是治理基线。references 为空数组违反模板必填约束。

**来源**：business-output §1.6-3

### J-03 structured_result 不合规时不得标 success

配置了 output_type/output_schema 的角色，成功态的 structured_result 必须满足模板要求。不合模板的结果应降级为 undefined + 标注合规性错误，不应按 success 态提交。

**来源**：implementation-notes D-11A

### J-04 非 success 时 structured_result 可为空对象

非 success 时 structured_result 可为空对象 `{}`，但 answer 和 status_reason 必须解释原因。

**来源**：business-output §1.6-4

### J-05 必填字段必须存在且类型正确；可选字段不得用空字符串替代

必填字段必须存在且类型正确。可选字段如角色知识不足以填写可省略，但不得用空字符串替代。

**来源**：business-output §1.6-2

---

## K. AI 链路规则

### K-01 AI 模型名不得硬编码在业务代码中

涉及独立 AI 链路时，模型选择至少必须做到服务端可配置。AI 推荐（AI_RECOMMEND_MODEL/TEMPERATURE/MAX_TOKENS）和 AI 创建（AI_CREATE_MODEL/TEMPERATURE/MAX_TOKENS）通过 6 个独立环境变量配置。角色测试/consume 路径使用 model_binding 机制（每角色独立配置），与 AI 链路配置无关。

**状态**：已实现——`config.py` 已有 `AI_CREATE_MODEL` / `AI_RECOMMEND_MODEL` 等环境变量，代码通过 `settings.` 引用，不再硬编码。

**来源**：IO-004（已关闭）、design-delta.md §3.4b

### K-02 AI 生成草案必须人确认后才入库

AI 生成角色草案，人确认后才保存为 draft。AI 提供测试和运营建议，但不得绕过发布门禁。AI 可推荐角色或改进方向，但不得自行修改已 published 资产。

**来源**：mvp-consensus §6、dd10-spec §4.1

### K-03 AI 推荐 output_type 含 A3 关键词时不得推荐

用户意图含"执行/操作/动作/流程执行/自动化"关键词时，不推荐 output_type（v0.4 无 A3 角色），提示用户意图超出 v0.4 范围。

**来源**：dd10-spec §2.2

### K-04 AI 推荐池准入条件

published 角色须同时具备 output_type + business_domain + applicable_scenarios(≥1) + bio(≥5 字符) 才能进入 AI 推荐候选池。不满足的角色仍在市场列表可见，但不参与 AI 推荐。

**来源**：design-delta.md §3.4a

### K-05 AI 推荐四阶段引擎规则

1. Phase 1 准入过滤
2. Phase 2 非 LLM 候选召回（关键词+多维召回，取前 10）
3. Phase 3 单次 LLM judge/rerank（同时完成意图分析+候选评分）
4. Phase 4 阈值过滤 + 保守拒绝（score < 0.5 拒绝；is_out_of_scope 整批拒绝；LLM 失败保守拒绝 → service_error，不放宽推荐）

推荐结果分 4 类：matched/no_match/out_of_scope/service_error。no_match 记录 OpsSignal；out_of_scope 和 service_error 不记录 OpsSignal。

**来源**：design-delta.md §3.4a、scope.md §2-DD-13

### K-06 creation_source 在 AI 草案保存时必须自动标记 ai_assisted

AI 草案流程保存时 creation_source 必须自动标记为 ai_assisted，不得走默认 manual。

**来源**：design-delta.md §3.1、dd10-spec §4.1、implementation-notes D-4A

---

## L. 复审与验收框架规则

### L-01 工程通过 ≠ 验收通过

自动化测试、build、部署通过只赋予更高层复审资格，不等于验收通过。

**来源**：acceptance-review §2-1

### L-02 运行态 > 仓库态

当前实际验收环境运行版本是标准。"仓库代码看起来已修复"不得替代"当前服务已生效"。

**来源**：acceptance-review §2-2

### L-03 证据 > 口头声明

所有"已支持"、"已通过"、"已集成"、"真实集成"声明必须有真实证据。mock/stub/fixture/代码走查不得冒充真实证据。

**来源**：acceptance-review §2-3/6

### L-04 价值 > 功能清单

复审不以"多少页面/接口"为核心，以"是否证明对应价值"为核心。

**来源**：acceptance-review §2-4

### L-05 冻结设计不得被实现阶段单方面降级

实现与设计不一致时先视为偏差，再判定是否允许。不得在实现中自行把冻结设计降级为较弱交付。

**来源**：acceptance-review §2-5

### L-06 复审结论类型严格定义

复审结论类型（工程退回/产品退回/价值证明不足/可进入用户测试/可进入终审验收）各有严格允许表述用词，不得越级表述。

**来源**：acceptance-review §4.1

### L-07 决策产品集成与 Dify 消费证明的验收口径

决策产品集成已正式暂缓至独立后续计划（见 D-01），不在当前版本验收范围内。DD-15 Dify 消费证明要求真实消费和 usage_record 对账证据，不得口头替代。当前版本已验证 consume 全链路 + Skill 包下载 + 外部调用通过（见 test-results.md），但 Dify 平台真实消费对账证据的闭合状态待确认。

**来源**：acceptance-review §4.2-3、§5-2/3、v0.5.1 release-notes、v0.5.1 test-results.md

### L-08 结构化输出审查关注"可消费性"

结构化输出审查不只看字段是否存在，而是看消费方能否稳定消费。UI/UX 审查不只看页面是否存在，而是看用户能否独立完成任务。

**来源**：acceptance-review §5-5/6

### L-09 复审发现设计本身无法支撑价值判断时必须退回 dossier

复审发现当前设计本身无法支撑价值判断时，必须退回 dossier 补设计收口，不得默认在实现侧修改。

**来源**：acceptance-review §7-2

---

## M. 数据迁移规则（已完成，保留作为历史参考）

> 以下规则对应 v0.3 → v0.4 数据迁移，迁移已完成。规则保留作为历史参考，不再活跃约束当前版本。M-02（已 published 版本快照不追溯修改）作为通用原则仍有效，对应 B-05。

### M-01 迁移不得破坏 v0.3 现有角色数据完整性（已完成）

迁移后系统必须仍能正常运行所有 v0.3 功能。

**来源**：version-snapshot §4.1

### M-02 已 published 版本快照不追溯修改（通用原则，仍有效）

已 published 角色版本快照不得追溯修改。

**来源**：version-snapshot §4.1-2、design-delta.md §3.7-1

### M-03 新字段有合理默认值，不强制回填（已完成）

capability_level 批量设为 A1；creation_source 批量设为 manual；output_type/output_schema/applicable_scenarios 不批量回填。

**来源**：design-delta.md §3.7-2~4

---

## N. 质量命令

### N-01 项目质量命令序列

```bash
npm run lint:md
vale delivery docs portfolio-sync.md
python3 scripts/iteration-guard.py --repo-root . --mode release
./venv/bin/python -m pytest tests -q
python3 -m compileall app
cd frontend && npm run build
```

前三项为迭代控制与文档质量闸门；后三项为产品实现质量闸门。

**来源**：product-iteration-control.md §5

### N-02 本轮不启用 pre-commit hook

显式命令和手动执行优先；等流程稳定后再决定是否添加 pre-commit。

**来源**：quality-toolchain §3

---

## O. 文档治理规则

### O-01 阻塞项必须先修复，再进入文档治理

文档结构治理必须在阻塞项修复后、设计冻结或编码实现前完成。

**来源**：document-structure-governance §1

### O-02 关键文档必须标注定位标签

所有 v0.4 关键文档必须标注为以下之一：Current Source of Truth / Active Review Material / Superseded / Historical Reference / Handoff Only。

**来源**：document-structure-governance §4.2

### O-03 docs/handoff/ 不得作为版本真源

docs/handoff/ 只用于外部同步或转发，不得作为 v0.4 版本真源。v0.4 真源判定必须基于 iteration dossier README、scope、design-delta、traceability、复审意见和 P0 材料。

**来源**：document-structure-governance §4.4

### O-04 旧口径表述必须在文档修订时删除

修订后的测试文档必须删除旧口径表述（如"DD-04 不新增接口"、"决策产品未纳入"、"只覆盖 US-06~US-13"）。

**来源**：document-structure-governance §4.3

---

## P. 代码实现红线

> 来源：`docs/handoff/project-handoff-to-codebuddy-2026-06-24.md` 第九章"注意事项"。这些是项目迭代中用真实踩坑教训换来的技术约束，每次涉及相关代码时必须先查此表。

### P-01 不得让 `_hydrate_runtime_kb_ids` 执行 flush 落库

`_hydrate_runtime_kb_ids` 负责在读取时将 `kb_id` 内存解析为知识平台 `package_id`，**仅做内存解析，不落库**。之前曾因 flush 落库导致 DB 中 `kb_id` 被静默改写，污染历史数据。

**来源**：handoff §9.1-1

### P-02 不得去掉 `list_documents` 中的 `urllib.parse.quote`

知识平台 `package_id` 可能是中文（如 `快消品行业知识`），URL 中必须做 percent-encode。去掉 `quote` 会导致中文包名请求返回 404。

**来源**：handoff §9.1-2

### P-03 不得在前端硬编码知识库偏好

前端不得硬编码知识库 ID 或路径偏好（如 `10-Areas/eve`），应信任后端返回的 `knowledge_object_id` 和 `package_id`。

**来源**：handoff §9.1-3

### P-04 export 检查的是已发布版本的说明卡，不是草稿

外供包生成时检查的是**已发布版本**的说明卡状态，不是当前草稿版本。不得在外供包生成时检查草稿版本的说明卡。

**来源**：handoff §9.1-4

### P-05 `prototype/` 目录不再维护

`prototype/` 仅保留为迁移参考，生产入口是 React 前端（FastAPI 根路径托管 `frontend/dist`）。不得在 `prototype/` 中做新功能开发。

**来源**：handoff §9.1-5

### P-06 后端改代码后必须手动重启

uvicorn 未开 `--reload`，修改后端代码后不会自动生效，必须手动重启服务。开发时注意这一点，避免"改了代码但没生效"的误判。

**来源**：handoff §9.2-1

### P-07 `.env` 优先级高于 `config.py` 默认值

修改 `config.py` 默认值但 `.env` 未同步修改时，运行时仍使用 `.env` 的值。修改配置时必须同步检查 `.env` 和 `.env.example`。

**来源**：handoff §9.2-2

### P-08 说明卡 stale 不一定是用户改了东西

说明卡 `source_hash` 不匹配（stale）不一定是用户修改了角色定义，知识平台迁移、`kb_id` 修复等底层变更也会导致 hash 不匹配。排查 stale 时先确认是否为底层变更引起。

**来源**：handoff §9.2-3

### P-09 已发布版本说明卡与草稿版本说明卡是分开的

在 02 页保存的是当前版本的说明卡，export 检查的是已发布版本的说明卡。两者独立存储，不得混用。修改角色定义后需到 02 页重新保存说明卡，已发布版本的说明卡不受影响。

**来源**：handoff §9.2-4

### P-10 知识平台协作遵循"先反馈再执行"原则

与知识平台（Knowledge Workbench）的所有协作通过 `docs/handoff/` 目录交换文档，遵循"先反馈再执行"原则。不得在未通过 handoff 文档同步的情况下单方面变更接口消费方式或口径。

**来源**：handoff §9.3、governance-understanding §开发红线-跨项目接口变更

---

## 规则变更索引

| ID | 日期 | 变更摘要 |
|---|---|---|
| R-001 | 2026-05-22 | 建立迭代控制机制、版本 dossier、iteration guard、文档质量闸门 |
| R-002 | 2026-05-28 | 复审/整改/裁决等外部输入是设计输入，不是已收口设计规格（DD-13 整改违规教训） |
| R-003 | 2026-06-17 | 论证从本质出发不为已有成果找理由 + 收到指令先反馈理解异议优化不默认执行 |
| R-004 | 2026-06-17 | 新增 A-09 UI调整与设计变更的判定边界规则 |
| R-005 | 2026-06-26 | 新增 P 章代码实现红线（P-01~P-10），将 handoff 技术注意事项纳入正式规则体系；更新强制读取顺序适配当前版本 |
| R-006 | 2026-06-26 | 规则体系适配 v0.5.1：修复 A 章编号冲突（第二个 A-07→A-10）；新增 A-11 外部反馈不默认执行规则；D-01/F-03/L-07 适配 DD-14 暂缓状态；G 章"v0.4"改为"当前版本"；M 章标记为已完成；强制读取顺序修复重复读取；K-01 标注已实现并关闭 IO-004 |

## 问题台账索引

| ID | 日期 | 类型 | 摘要 | 状态 |
|---|---|---|---|---|
| IO-001 | 2026-05-22 | 流程缺口 | 配置页缺少字段说明等导致多轮返工 | Open |
| IO-002 | 2026-05-22 | 交付证据缺口 | 验证/冒烟/portfolio-sync 口径不同步 | Closed |
| IO-003 | 2026-05-22 | 集成口径风险 | 知识平台 Accepted 被误写为长期冻结 | Closed |
| IO-004 | 2026-05-28 | 设计/运营缺口 | AI 模型名硬编码 | Closed |
| IO-005 | 2026-05-28 | 流程违规 | DD-13 整改未先回写设计 | Closed |
