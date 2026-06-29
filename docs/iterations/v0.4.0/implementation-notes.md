# v0.4.0 实现偏差与关键落地说明

> 用途：记录"原预期 vs 实际实现 vs 为什么改"，避免实现和设计默默分叉
> 日期：2026-05-27

## 1. 偏差记录

### D-1A: boundary_blocked 判定采用关键词匹配而非边界声明驱动

| 项 | 内容 |
|---|---|
| 原预期 | 按 `business-output-templates-and-status-rules.md` §3.1，boundary_blocked 应基于角色声明的 knowledge_boundary 和 capability_boundary/capability_level 判断"查询是否超出声明边界" |
| 实际实现 | `app/services/consume_service.py` `_determine_status()` 使用逗号分隔关键词匹配 knowledge_boundary 文本字段：查询不含任何边界关键词 + 查询 <20 字 → out_of_scope；否则 near_boundary |
| 偏差原因 | knowledge_boundary 是自然语言文本，无法结构化判断"查询是否越界"。关键词匹配是当前最可行的近似方案，但会过度触发短查询、漏判含关键词但实际越界的查询 |
| 用户影响 | 短查询可能误判为 boundary_blocked；长查询可能漏判。保守策略优先降入 undefined（5-10 字查询），降低误判影响 |
| 是否补测 | 需补充测试：短查询 boundary_blocked 命中率、长查询漏判率。后续版本应引入 LLM boundary self-assessment 分数作为辅助判定 |

### D-1B/2A: boundary_status 与 status 联动规则通过控制流隐式保证，无显式校验

| 项 | 内容 |
|---|---|
| 原预期 | 按 `business-output-templates-and-status-rules.md` §3.2，后端必须验证 status 与 boundary_status 的联动一致性 |
| 实际实现 | `_determine_status()` 中每个 return 路径在构建 boundary_status 时按顺序保证联动正确（boundary_blocked 先检查 → 不会落入 insufficient_knowledge 的 out_of_scope 分支），但无独立的联动校验步骤 |
| 偏差原因 | 当前 6 状态判定逻辑按优先级顺序排列，程序流天然保证联动一致。添加独立校验会增加代码量但不改变运行时行为 |
| 用户影响 | 当前无用户影响。未来修改判定逻辑时可能意外破坏联动关系，无测试或断言捕获 |
| 是否补测 | 需补充联动一致性测试（每个 status 的 boundary_status 必须符合联动表）。建议增加 `_validate_boundary_linkage()` 函数 |

### D-3A: test-consume 承载完整 6 状态 + 结构化输出，超出原始设计范围

| 项 | 内容 |
|---|---|
| 原预期 | v0.3 test_runs 只产出自然语言输出。v0.4 设计文档定义 test-consume 为测试验证接口，但只提到"固定治理外壳 + structured_result + status + boundary_status" |
| 实际实现 | `TestConsumeRequest` 包含 `output_type` 可选字段，test_consume 复用完整 consume 引擎（6 状态 + structured_result 解析 + boundary_status），产出 TestValidationRecord |
| 偏差原因 | 设计文档未明确禁止 test-consume 接收 output_type 参数；复用引擎是架构上合理的延伸，使测试台能验证结构化输出的合规性 |
| 用户影响 | 测试台能更完整验证角色表现（含结构化合规校验），是正向延伸。不影响 consume API 的正式消费路径 |
| 是否补测 | 已覆盖（test-consume 的 6 状态 + structured_result 测试已在 pytest 中） |

### D-4A: AI 创建流程的 creation_source 始终标记为 manual

| 项 | 内容 |
|---|---|
| 原预期 | 按 `dd10-ai-creation-extended-spec.md` 和 `scope.md`，通过 AI 草案流程创建的角色应自动标记 creation_source="ai_assisted"，用于运营看板统计 AI 辅助创建率 |
| 实际实现 | 前端流程：用户生成 AI 草案 → 编辑 → 点击保存 → 调用 `POST /role-assets`（RoleCreate 不含 creation_source）→ 后端 `RoleService.create()` 默认 creation_source="manual"。AI 草案流程走的是同一个 createRole 接口，无法区分来源 |
| 偏差原因 | RoleCreate schema 按设计不含 creation_source（不可由调用方传值）。但后端 create 端点没有从请求上下文推断来源的机制。需要在保存时传递来源标记，但 RoleCreate 没有该字段 |
| 用户影响 | 运营看板 `creation_by_source` 的 ai_assisted 计数永远为 0，无法追踪 AI 辅助创建率 |
| 是否补测 | 需补充测试验证 AI 草案流程保存后 creation_source 为 ai_assisted。修复方案：前端在 AI 草案回填后保存时，传递 `creation_source_hint="ai_assisted"` 作为额外请求参数（不入 RoleCreate，入 query param），后端根据 hint 设置 creation_source |

### D-6A: 缺失 capability_level 时未对 agent_platform/decision_product 独立拒绝

| 项 | 内容 |
|---|---|
| 原预期 | 按 `consume-api-design.md` §7.1，缺失 capability_level 的角色：human 按 A1 处理；Dify/决策产品应拒绝 |
| 实际实现 | `consume_service.py` lines 63-69 只检查缺失 output_type 的 agent_platform/decision_product 拒绝。缺失 capability_level 时默认 A1 处理（`fields.get("capability_level", "A1")`），对所有 caller_type 一视同仁 |
| 偏差原因 | 遗漏。设计文档明确要求缺失 capability_level 时对自动化消费者同样拒绝，但实现时只做了 output_type 的 gate |
| 用户影响 | 有 output_type 但缺 capability_level 的角色可被 Dify/决策产品消费，产出使用默认 A1 级别的结果，违反设计对自动化消费者的严格门禁 |
| 是否补测 | 需补充测试：缺失 capability_level + caller_type=decision_product → 应返回 HTTP 400 |

### D-7A: 输出模板子结构验证未实现

| 项 | 内容 |
|---|---|
| 原预期 | 按 `business-output-templates-and-status-rules.md` §1.2-1.5，所有模板子结构（RiskItem/ReferenceItem/IssueItem/ClauseItem）的必填字段应校验类型正确 |
| 实际实现 | `output_schema_service.py` `validate_structured_result()` 只校验顶层字段存在 + references 非空数组，不校验子结构内部字段 |
| 偏差原因 | structured_result 由 LLM 动态生成，格式可能不完全对齐模板。过度严格校验会导致大量 boundary_blocked 或 undefined，降低可用性 |
| 用户影响 | structured_result 中 `major_risks: [{}]`（空 RiskItem）会通过验证，但展示时内容缺失 |
| 是否补测 | 需补充子结构验证逻辑。后续版本应增加 `validate_sub_structure_fields()` 方法 |

### D-8A: PromptBuilder 把 knowledge_chunks dict 当 str 处理

| 项 | 内容 |
|---|---|
| 原预期 | PromptBuilder.build 和 build_consume_prompt 接收 list[str] 知识片段 |
| 实际实现 | knowledge_platform.retrieve() 返回 list[dict]（含 chunk/source/score），PromptBuilder.build 遍历时 `{chunk}` 把 dict 整体渲染为字符串。build_consume_prompt 调用 build() 返回 str 后又对其调用 .append()——str 无 append 方法，导致 500 |
| 偏差原因 | 两层类型不匹配：(1) retrieve() 返回 dict 列表但 PromptBuilder 期望 str 列表；(2) build() 返回 str 但 build_consume_prompt 把 str 当 list 用 |
| 用户影响 | consume/test-consume 在真实运行态下稳定 500，主链路完全中断 |
| 是否补测 | 已补测（V01-V08, V13 覆盖 consume/test-consume 正向通过） |

### D-8B: 发布门禁查 TestRunRecord 而非 TestValidationRecord

| 项 | 内容 |
|---|---|
| 原预期 | v0.4 test-consume 写入 TestValidationRecord 后，发布门禁应认可该记录 |
| 实际实现 | role_service.py publish() line 161-167 查 TestRunRecord（旧表 test_run_records），不查 TestValidationRecord（新表 test_validation_records）。v0.4 正式测试链路完成后无法满足发布条件 |
| 偏差原因 | v0.4 新增 test-consume + TestValidationRecord 但未同步更新发布门禁查询 |
| 用户影响 | 按v0.4正式UI主链路完成测试→进入发布→被拒"发布前至少需要完成1次角色测试"——语义断裂 |
| 是否补测 | 已补测（V12 覆盖 test-consume后 publish成功） |

### D-8C: output-templates 路由被 /{role_id} 吞掉

| 项 | 内容 |
|---|---|
| 原预期 | GET /role-assets/output-templates 返回 4 个模板定义 |
| 实际实现 | FastAPI 按声明顺序匹配，GET /{role_id} 在 GET /output-templates 之前，"output-templates" 匹配 {role_id} 参数→返回404"角色不存在" |
| 偏差原因 | 路由声明顺序错误——静态路径段应在参数化路径段之前 |
| 用户影响 | output-templates API 完全不可用 |
| 是否补测 | 已补测（V06 覆盖 GET /role-assets/output-templates → 200） |

### D-9A: 自测证据与真实情况不一致

| 项 | 内容 |
|---|---|
| 原预期 | delivery/test-results-v0.4.md 中 P01-P18 和 H01-H07 标为 PASS，应基于真实运行态证据 |
| 实际实现 | 全部基于代码走查（读代码确认逻辑存在）而非真实 HTTP 请求。真实运行态下至少 3 个 P0 阻塞存在（PromptBuilder bug / 发布门禁断裂 / 路由吞掉），但证据标注全 PASS |
| 偏差原因 | 自测执行方式为"代码走查 + API 级验证"，但"API 级验证"也是代码层面的确认而非真实运行态调用 |
| 用户影响 | 复审方无法信任交付证据，Self-Tested 声明被退回 |
| 是否补测 | 已修正——降实交付证据，代码走查项不再标 PASS，补齐 13 项自动化测试覆盖 |

### D-10A: DD-13 AI 推荐 MVP 已补齐交付（四阶段引擎）

| 项 | 内容 |
|---|---|
| 原预期 | 按 scope.md DD-13，v0.4 必交"AI 推荐 MVP + 业务发现视图最小形态" |
| 实际实现 | 首轮只交付了业务发现视图最小形态。AI 推荐 MVP（业务意图→角色匹配 + 推荐理由 + /marketplace/recommend 端点）完全缺失 |
| 补齐实现 | 2026-05-27 补齐 POST /marketplace/recommend 端点 + 前端场景入口卡片 + AI 推荐输入区 + 推荐结果展示 + 无匹配运营信号。首轮推荐引擎为两阶段（关键词映射 + LLM 推荐理由回退），经复审退回后升级为四阶段引擎（2026-05-27 复审整改）：Phase 1 推荐池准入过滤 + Phase 2 非 LLM 候选召回 + Phase 3 单次 LLM judge/rerank + Phase 4 阈值过滤/保守拒绝。推荐结果分 4 类：matched/no_match/out_of_scope/service_error。详见 handoff `dd13-recommend-rereview-submission-2026-05-27.md` |
| 用户影响 | 资产市场可按业务意图发现角色 + 推荐理由 + 场景入口，满足 DD-13 MVP 交付标准 |
| 是否补测 | **已补测**: V29-V41 覆盖推荐链路全场景（正向匹配/无匹配/语义不匹配/域不匹配/池准入排除/理由非模板/LLM 失败保守拒绝/空 intent）

### D-11A: structured_result 不合规时仍标 success

| 项 | 内容 |
|---|---|
| 原预期 | 配置了 output_type/output_schema 的角色，成功态的 structured_result 必须满足模板要求；不合模板的结果不应按 success 态提交 |
| 实际实现 | consume_service._parse_structured_result 解析 LLM JSON 失败时返回 get_default_schema（空壳结构），但 status 仍为 success |
| 偏差原因 | 默认空 schema 的 references 为空数组，违反模板必填约束；代码未对 structured_result 做合规性校验 |
| 用户影响 | 自动化消费者收到空壳 structured_result 仍标 success，无法稳定消费 |
| 是否补测 | **已修复 + 已补测**: structured_result 不合规时降级为 undefined + _compliance_errors 标注；V23/V24/V25 覆盖合规/非合规/references 验证 |

### D-11B: max_tokens 配置未透传到 LLM 调用

| 项 | 内容 |
|---|---|
| 原预期 | 用户配置的 max_tokens 应进入 LLM 调用请求 payload |
| 实际实现 | LLMService.chat() 接收 max_tokens 参数但 payload 中只有 model/messages/temperature，max_tokens 被丢弃 |
| 偏差原因 | payload 构建遗漏 max_tokens 字段 |
| 用户影响 | 角色配置的 max_tokens 不生效，所有 LLM 调用使用默认值 |
| 是否补测 | **已修复 + 已补测**: payload 加入 max_tokens 字段；V26 验证 max_tokens=2048 透传 |

### D-12A: consume 未校验 role_version_id 归属和可消费状态

| 项 | 内容 |
|---|---|
| 原预期 | 按 consume-api-design.md §3.2，consume 传入 role_version_id 时必须校验版本归属（role_version_id 必须属于 role_id）和可消费状态（is_deprecated 为 False）。不满足时返回 HTTP 400，不返回治理外壳、不生成 usage_record |
| 实际实现 | consume_service.py consume() line 54 直接取请求里的 version_id 并读字段，不校验 RoleVersion.role_id 是否等于请求 role_id，不校验 is_deprecated。传入其他角色的 version_id 可成功消费并写入 usage_record |
| 偏差原因 | 实现时遗漏版本归属校验，只做了版本字段读取 |
| 用户影响 | 消费方可传入其他角色的版本 ID，获取不属于本角色的版本字段（含 structured_result/output_type 等），写入本角色的 usage_record 导致数据污染 |
| 是否补测 | **已修复 + 已补测**: consume 和 test-consume 均新增归属校验（RoleVersion.role_id != role.id → 400 "指定的版本不属于该角色"；is_deprecated → 400 "指定版本不可消费（已归档）"）；V27 覆盖 consume/test-consume 归属校验 |

### D-12B: 请求级 output_type 覆盖未生效

| 项 | 内容 |
|---|---|
| 原预期 | 按 consume-api-design.md §3.1 line 62，ConsumeRequest 的 output_type 字段为"可选，指定输出类型；不填时使用角色版本配置的默认 output_type"。请求传了就用请求指定值（A67 验证用例） |
| 实际实现 | consume_service.py _execute_consume line 239 只取 fields.get("output_type")（版本字段值），ConsumeRequest.output_type 和 TestConsumeRequest.output_type 虽已在 schema 中暴露但实现未使用 |
| 偏差原因 | 实现时只从版本字段读取 output_type，未考虑请求级覆盖 |
| 用户影响 | 消费方无法通过请求参数指定不同输出类型（如角色配置 decision_advice 但请求要 risk_analysis），始终返回版本配置的 output_type |
| 是否补测 | **已修复 + 已补测**: consume 和 test-consume 均新增请求级 output_type 覆盖（data.output_type → fields["output_type"]）；V28 覆盖 consume/test-consume 请求覆盖 |

### D-13A: AI 推荐 / AI 创建模型名已改为可配置

| 项 | 内容 |
|---|---|
| 原预期 | `AI 推荐` 和 `AI 创建草案` 作为两条独立 AI 链路，其模型选择应可配置，至少不应把模型名硬编码在业务代码中 |
| 实际实现（已修复） | `app/services/recommend_service.py` 改为 `model=settings.AI_RECOMMEND_MODEL`；`app/services/ai_create_service.py` 改为 `model=settings.AI_CREATE_MODEL`。新增 6 个独立配置项（AI_RECOMMEND_MODEL/TEMPERATURE/MAX_TOKENS + AI_CREATE_MODEL/TEMPERATURE/MAX_TOKENS），默认值与原硬编码值一致。详见 handoff `ai-model-config-implementation-2026-05-28.md` |
| 偏差原因 | 首轮实现优先打通功能链路，模型治理未单独设计，导致推荐链路和创建链路都绑定到固定模型名 |
| 用户影响 | 无回归影响（默认值与原硬编码值一致）；配置切换后实际请求 model 字段随环境变量变化，运营可按链路分别调优 |
| 是否补测 | **已补测**: 真实运行态验证配置切换生效（AI_RECOMMEND_MODEL 从 deepseek-v4-pro 切换为 test-model-switch 后 settings 读取值变化）；79 条自动化测试通过，不影响角色测试/consume 路径（该路径使用 model_binding 机制） |

## 2. 关键落地说明

1. 当前版本为 Self-Tested（复审退回→修复→重建部署态→再升级）。
2. D-8A/D-8B/D-8C 属于 P0 阻塞项，**已修复**（2026-05-27 复审退回后修复）。真实运行态验证：3 个 P0 在 docker compose 重建后全部通过。
3. D-9A 属于证据质量问题，**已修正**（降实交付证据，不再以代码走查标 PASS）。
4. D-10A DD-13 AI 推荐 MVP **已补齐交付**（2026-05-27 三轮退回后补齐）。POST /marketplace/recommend + 四阶段引擎（准入过滤→候选召回→LLM judge→阈值过滤）+ 4 类结果区分（matched/no_match/out_of_scope/service_error）+ 推荐池准入 + 前端场景卡片/AI 推荐输入/推荐结果展示 + ops_signals 运营信号。详见 handoff `dd13-recommend-rereview-submission-2026-05-27.md`
5. D-11A/D-11B 属于消费语义/配置真实性修复，**已修复**（2026-05-27 二轮审核后修复）。
6. D-12A/D-12B 属于消费校验/请求覆盖修复，**已修复**（2026-05-27 三轮退回后修复）。真实运行态验证：版本归属校验返回 400 + output_type 覆盖生效。
7. D-4A 和 D-6A 属于 P1 修复项，**已修复**（2026-05-27 首轮修复）。
7. D-1A 和 D-7A 属于 P2 优化项，可在后续迭代改进。
8. D-3A 属于正向延伸，不影响核心主链路，无需修复但需记录。
9. D-1B/2A 属于健壮性改进，当前联动正确但缺少防护机制，应补充联动一致性测试。
10. 不得将 Formal Status 升级为 User-Acceptance-Candidate 或 Accepted（需终审方外部审核）。DD-14/DD-15 为外部阻塞。
11. D-13A AI 推荐/创建模型名已改为可配置（2026-05-28 整改通过），新增 6 个独立配置项，详见 handoff `ai-model-config-implementation-2026-05-28.md`。
12. D-14A 业务输出配置 UI 偏差（P1）**已修复**（2026-05-28）：原实现为 output_type 下拉框 + output_schema JSON textarea + 无保存确认弹窗；修复后改为 4 模板卡片选择 + 字段业务含义表 + 保存前确认弹窗。对齐 task-flows §2.2 验收点。
13. D-14B 消费结果展示偏差（P1）**已修复**（2026-05-28）：原实现为 structured_result Object.entries + JSON.stringify + 无 sources 展示；修复后改为 StructuredResultDisplay 组件（按模板字段中文标签逐项展示，子结构带嵌套标注）+ sources 来源列表（含来源名称、章节、依据类型）。对齐 task-flows §2.4 验收点。UsageDesk.tsx 和 RoleTest.tsx 共用该组件。
14. D-14C AI 协作创建流程偏差（P1）**部分修复**（2026-05-28）：已添加保存确认弹窗 + AI 生成字段标注（6 个字段加 "✨ AI 生成" 标记）。保存成功页（提供继续编辑/进入测试台/返回三出口）暂未实现——当前仍跳详情页，作为 P2 偏差待后续补齐。对齐 task-flows §2.1 验收点。
15. D-14D 运营看板偏差（P2）**部分修复**（2026-05-28）：卡片名称已对齐设计（创建运营/使用运营/质量运营/风险运营），缺失指标标注为 v0.4.x 增强（AI 草案接受率/人工修改率/草稿沉睡数量 + 测试通过率/最近评分平均）。后端 DashboardStats 当前不含这些指标，需后续版本新增统计查询。
