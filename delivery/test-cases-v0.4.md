# v0.4.0 测试用例

版本: v0.4.0 | 日期: 2026-05-26 | 状态: Draft

> 本文档覆盖 US-06 至 US-21（15 项交付项：US-06~US-10, US-12~US-21；US-11/DD-06 角色模板库已移出本轮范围）。复审通过后同步更新为正式版。

## US-06：角色资产治理属性可填写和展示

### 自动化 API 测试

| # | 用例 | 验证点 |
|---|------|--------|
| A35 | `POST /role-assets` 创建角色含 category | category 字段写入 RoleAsset 表，详情返回包含 category |
| A36 | `POST /role-assets` 创建角色含 owner | owner 字段写入，详情返回包含 owner |
| A37 | `POST /role-assets` 创建角色含 business_domain | business_domain 字段写入，详情返回包含 business_domain |
| A38 | `POST /role-assets` 创建角色含 visibility | visibility 字段写入，默认值为"内部"；详情返回包含 visibility |
| A39 | `POST /role-assets` 创建角色含 applicable_scenarios | applicable_scenarios 写入 RoleVersionField（EAV, L1_IDENTITY），详情返回包含字段 |
| A40 | `POST /role-assets` 创建角色含 creation_source = ai_assisted | creation_source 写入 RoleAsset 表，详情返回包含 creation_source |
| A41 | `POST /role-assets` 创建角色不填 category | category 默认为"自定义" |
| A42 | `POST /role-assets` 创建角色不填 visibility | visibility 默认为"内部" |
| A43 | `POST /role-assets` 创建角色不填 creation_source | creation_source 默认为"manual" |
| A44 | `PATCH /role-assets/{id}` 更新 owner/maintainer | 更新后详情返回新值 |
| A45 | `GET /role-assets?category=行业专家` | 按分类筛选返回匹配角色 |
| A46 | `GET /role-assets?owner=张三` | 按所有者筛选返回匹配角色 |
| A47 | `GET /role-assets?visibility=公开` | 按可见范围筛选返回匹配角色 |

### 程序化 UI 测试

| # | 用例 | 验证点 |
|---|------|--------|
| F13 | 创建页 category 下拉选择 | 下拉选项包含：行业专家、职能助手、制度顾问、项目管理、自定义 |
| F14 | 创建页 owner 文本输入 | 可输入并保存 |
| F15 | 创建页 visibility 下拉选择 | 下拉选项包含：内部、部门、公开；默认选中"内部" |
| F16 | 详情页资产治理属性展示 | 展示 category、owner、maintainer、business_domain、visibility、creation_source |
| F17 | 列表页 category 标签展示 | 角色卡片显示分类标签 |
| F18 | 列表页筛选 category/owner/visibility | 篩选下拉可用，结果匹配 |

### 人工手动冒烟

| # | 用例 | 验证点 |
|---|------|--------|
| H06 | 人工创建角色 -> 填写全部治理属性 -> 保存 -> 详情页查看 | 所有治理属性正确展示，creation_source = manual |
| H07 | 人工编辑角色 -> 修改 owner/maintainer -> 保存 -> 详情页查看 | 修改后值正确展示 |

## US-07：边界声明补齐与强化

### 自动化 API 测试

| # | 用例 | 验证点 |
|---|------|--------|
| A48 | `POST /role-assets` 创建角色含 knowledge_boundary | knowledge_boundary 写入 RoleVersionField（EAV, L3_KNOWLEDGE），详情返回包含字段 |
| A49 | `PATCH /role-assets/{id}` 更新 knowledge_boundary | 更新后详情返回新值 |
| A50 | `POST /role-assets` 创建角色不含 knowledge_boundary | knowledge_boundary 为 null |
| A51 | `GET /role-assets/{id}` 详情返回 knowledge_boundary | 字段在 RoleDetail schema 中存在 |

### 程序化 UI 测试

| # | 用例 | 验证点 |
|---|------|--------|
| F19 | 创建页 knowledge_boundary textarea | 可输入并保存 |
| F20 | 编辑页 knowledge_boundary textarea | 可输入并保存 |
| F21 | 详情页 knowledge_boundary 展示 | 展示值或"未声明"提示 |
| F22 | 详情页 capability_boundary 资产化展示 | 语义强化标注（如"本角色能力边界：仅提供分析建议"） |

### 人工手动冒烟

| # | 用例 | 验证点 |
|---|------|--------|
| H08 | 人工创建角色 -> 填写 knowledge_boundary -> 保存 -> 详情页查看 | knowledge_boundary 正确展示 |
| H09 | 人工查看 capability_boundary 资产化展示 | 语义标注清晰可读 |

## US-08：使用台 + 测试台升级

### 自动化 API 测试（使用台 — consume API）

| # | 用例 | 验证点 |
|---|------|--------|
| A52 | `POST /role-assets/{id}/consume` published 角色消费 | 200，返回固定治理外壳（answer + role_id + role_version_id + usage_record_id + created_at + sources + boundary_status + output_type + structured_result + status + status_reason），生成 usage_record |
| A53 | `POST /role-assets/{id}/consume` 不传 role_version_id | 系统使用当前 published 版本，输出中 role_version_id 为实际使用的版本 |
| A54 | `POST /role-assets/{id}/consume` 传 role_version_id | 系统使用指定 published 版本 |
| A55 | `POST /role-assets/{id}/consume` draft/test 角色消费 | 返回 403，不返回固定治理外壳，不生成 usage_record |
| A56 | `POST /role-assets/{id}/consume` role_version_id 不属于 role_id | 返回 400，提示"指定的版本不属于该角色" |
| A57 | `POST /role-assets/{id}/consume` 已归档版本消费 | 返回 400，提示"指定版本不可消费（已归档）" |
| A58 | `POST /role-assets/{id}/consume` role_id 不存在 | 返回 404，提示"角色资产不存在" |
| A59 | `GET /role-assets/{id}/consume-records` | 返回消费记录列表，包含 caller_type/caller_id/role_version_id/status/boundary_status/output_type/structured_result |
| A60 | usage_record 冻结验证 | 角色发布新版本后，旧 usage_record 的 role_version_id 不变 |
| A61 | consume API caller_type/caller_id 记录 | usage_record 中 caller_type 和 caller_id 与请求输入一致 |

### 自动化 API 测试（测试台 — test-consume 内部接口）

| # | 用例 | 验证点 |
|---|------|--------|
| A62 | `POST /role-assets/{id}/test-consume` test 版本角色消费 | 200，返回固定治理外壳（字段与 consume API 一致，但 usage_record_id 替换为 validation_record_id），生成 test_validation_record（不写入 usage_records 表） |
| A63 | `POST /role-assets/{id}/test-consume` published 版本角色消费 | 返回 403 或 400，test-consume 只接受 test 状态版本 |
| A64 | test_validation_record 与 usage_record 区分 | test_validation_record 不出现在 usage_records 表和 consume-records 查询结果中 |

### 程序化 UI 测试（使用台）

| # | 用例 | 验证点 |
|---|------|--------|
| F23 | published 角色详情页显示"使用"入口 | 按钮可见且可点击 |
| F24 | draft/test 角色详情页不显示"使用"入口 | 按钮不显示或禁用 |
| F25 | 使用台页面 /roles/:id/use | 页面渲染正确，支持输入 query 和可选 context |
| F26 | 使用台消费结果展示 | 展示固定治理外壳：status + status_reason + answer + boundary_status + structured_result + sources |
| F27 | 使用台 status 中文展示 | success→成功, boundary_blocked→边界阻断, insufficient_context→上下文不足, insufficient_knowledge→知识不足, system_failed→系统失败, undefined→未定义 |
| F28 | 使用台 boundary_status 中文展示 | within_boundary→边界内, near_boundary→接近边界, out_of_scope→越界, not_applicable→不适用 |

### 程序化 UI 测试（测试台）

| # | 用例 | 验证点 |
|---|------|--------|
| F29 | 测试台页面 /roles/:id/test | 页面渲染正确，支持输入 query 和可选 context |
| F30 | 测试台结构化结果展示 | 按 output_type 模板字段逐项展示，每字段标注合规状态 |
| F31 | 测试台 boundary 命中分析面板 | 展示角色声明的 boundary 与消费结果 boundary_status 对比 |
| F32 | 测试台治理外壳完整性检查 | 各字段标注合规/缺失/类型错误/值不合法 |

### 人工手动冒烟

| # | 用例 | 验证点 |
|---|------|--------|
| H10 | 人工进入 published 角色使用台 -> 输入查询 -> 查看回复 -> 查看消费记录 | 使用台完整可用，记录与测试记录区分 |
| H11 | 人工进入 test 角色测试台 -> 输入查询 -> 查看 structured_result 验证面板 | 结构化输出合规性校验、6 状态展示、boundary 命中分析完整可见 |

## US-09：统一消费 API 可调用

### 自动化 API 测试

| # | 用例 | 验证点 |
|---|------|--------|
| A65 | `POST /role-assets/{role_id}/consume` 正常消费 | 返回固定治理外壳全量字段（answer/role_id/role_version_id/usage_record_id/created_at/sources/boundary_status/output_type/structured_result/status/status_reason） |
| A66 | consume API 输入不含 output_type | 使用角色版本配置的默认 output_type |
| A67 | consume API 输入含 output_type | 使用请求指定的 output_type |
| A68 | consume API 输入含 context | context 传入 LLM 调用 |
| A69 | consume API 版本选择：只传 role_id | 系统选择当前 published 版本 |
| A70 | consume API 版本选择：传 role_id + role_version_id | 系统使用指定版本 |
| A71 | consume API 错误场景汇总验证 | 400/403/404 不返回固定治理外壳、不生成 usage_record、不计入 6 状态统计 |

## US-10：执行能力模型定义完成

### 自动化 API 测试

| # | 用例 | 验证点 |
|---|------|--------|
| A72 | `POST /role-assets` 创建角色含 capability_level | capability_level 写入 RoleVersionField（EAV, L4_CAPABILITY），详情返回包含字段 |
| A73 | `POST /role-assets` 创建角色不含 capability_level | capability_level 默认为 A1 |
| A74 | `PATCH /role-assets/{id}` 更新 capability_level | 更新后详情返回新值 |
| A75 | capability_level 版本快照验证 | 角色发布后 capability_level 进入版本快照，后续版本变更不影响已发布版本 |

### 程序化 UI 测试

| # | 用例 | 验证点 |
|---|------|--------|
| F33 | 创建/编辑页 capability_level 选择 | 下拉选项：A1 问答建议、A2 生成产物、A3 执行动作 |
| F34 | 详情页 capability_level 展示 | 展示能力层级标注和语义说明 |

## US-12：历史版本详情可查看

### 程序化 UI 测试

| # | 用例 | 验证点 |
|---|------|--------|
| F35 | 版本列表页 /roles/:id/versions | 渲染版本列表 |
| F36 | 版本内容查看 | 可查看版本内容差异 |

## US-13：详情页枚举中文映射

### 程序化 UI 测试

| # | 用例 | 验证点 |
|---|------|--------|
| F37 | 详情页 status 中文映射 | draft→草稿, test→测试中, published→已发布, archived→已归档 |
| F38 | 详情页 layer 中文映射 | L1→角色身份, L2→角色心智, L3→知识边界, L4→能力边界, L5→模型配置 |
| F39 | 列表页 status/layer 中文 | 对应枚举显示中文 |
| F40 | 详情页 capability_level 中文映射 | A1→问答建议, A2→生成产物, A3→执行动作 |
| F41 | 详情页 output_type 中文映射 | decision_advice→决策建议, risk_analysis→风险分析, policy_explanation→制度解释, review_findings→专业审查 |
| F42 | 消费结果 boundary_status 中文映射 | within_boundary→边界内, near_boundary→接近边界, out_of_scope→越界, not_applicable→不适用 |

## US-14：运营看板可用

### 程序化 UI 测试

| # | 用例 | 验证点 |
|---|------|--------|
| F43 | 运营看板页面渲染 | 页面包含 5 维度分区：资产总览、创建运营、质量运营、使用运营、风险运营 |
| F44 | 资产总览数字卡片 | 展示全部/发布/草稿/归档 4 个数字 |
| F45 | 创建运营 AI 草案接受率 | 展示 AI 草案接受率和人工修改率（基于 creation_source 字段统计） |
| F46 | 使用运营消费状态分布 | 展示 6 状态分布百分比 |
| F47 | 风险运营 boundary_blocked 比率 | 展示 boundary_blocked 和 undefined 比率 |

### 人工手动冒烟

| # | 用例 | 验证点 |
|---|------|--------|
| H12 | 人工进入运营看板 -> 查看各维度数据 | 5 维度数字卡片正确展示，消费状态分布包含 6 状态 |

## US-15：AI 协作创建可用

### 自动化 API 测试

| # | 用例 | 验证点 |
|---|------|--------|
| A76 | AI 创建角色保存后 creation_source = ai_assisted | RoleAsset 表 creation_source 字段值为 ai_assisted |
| A77 | AI 创建角色保存后 output_type 进入版本快照 | RoleVersionField 中包含 output_type 字段 |
| A78 | AI 创建角色保存后 applicable_scenarios 进入版本快照 | RoleVersionField 中包含 applicable_scenarios 字段 |
| A79 | AI 创建角色保存后 output_schema 进入版本快照 | RoleVersionField 中包含 output_schema 字段 |

### 程序化 UI 测试

| # | 用例 | 验证点 |
|---|------|--------|
| F48 | AI 创建入口页面 | 展示"AI 协作创建"和"手动创建"两个选项 |
| F49 | AI 创建意图输入 | 大文本输入框，空输入时按钮 disabled，<10 字提示补充 |
| F50 | AI 草案展示 | 所有 AI 生成字段标注"AI 生成"或"AI 推荐"；分组展示（基础信息/边界声明/业务输出/治理属性） |
| F51 | AI 草案编辑 | 所有字段可编辑；output_type/capability_level/category 为下拉选择 |
| F52 | AI 创建保存确认弹窗 | 弹窗确认"角色草案将保存为 draft 状态" |
| F53 | AI 创建成功页 | 展示角色名称、状态、创建来源 |
| F54 | AI 失败处理 | 部分失败标注失败字段；全失败提供重新尝试和手动创建两个选项 |
| F55 | output_type 修改联动 output_schema | 修改 output_type 后 output_schema 自动切换为新模板默认结构 |

### 人工手动冒烟

| # | 用例 | 验证点 |
|---|------|--------|
| H13 | 人工点击 AI 协作创建 -> 输入意图 -> AI 生成草案 -> 编辑草案 -> 确认保存 | 完整流程可用，creation_source = ai_assisted，output_type/applicable_scenarios/output_schema 正确保存 |

## US-16：业务输出 Schema 可配置

### 自动化 API 测试

| # | 用例 | 验证点 |
|---|------|--------|
| A80 | 角色配置 output_type = decision_advice 后消费输出 structured_result | structured_result 包含 position/key_reasons/major_risks/suggested_actions/references 必填字段 |
| A81 | 角色配置 output_type = risk_analysis 后消费输出 structured_result | structured_result 包含 key_findings/risk_items/overall_risk_level/impact_scope/suggested_mitigations/references 必填字段 |
| A82 | 角色配置 output_type = policy_explanation 后消费输出 structured_result | structured_result 包含 applicable_clauses/clause_explanation/allowed_actions/prohibited_actions/references 必填字段 |
| A83 | 角色配置 output_type = review_findings 后消费输出 structured_result | structured_result 包含 issues/overall_severity/references 必填字段 |
| A84 | 发布前校验：output_type 为非法枚举值 | 校验失败，不允许进入 published |
| A85 | 发布前校验：output_schema 为空 | 校验失败，不允许进入 published |
| A86 | 发布前校验：capability_level 为非法值 | 校验失败，不允许进入 published |
| A87 | output_type/output_schema 版本快照不可覆写 | 已 published 版本的 output_type/output_schema 不随后续编辑变更 |

### 程序化 UI 测试

| # | 用例 | 验证点 |
|---|------|--------|
| F56 | 详情页 output_type 展示 | 展示输出类型中文名 |
| F57 | 详情页 output_schema 展示 | 按模板字段列表展示，每字段标注中文名/业务含义/必填性 |

### 人工手动冒烟

| # | 用例 | 验证点 |
|---|------|--------|
| H14 | 人工配置角色 output_type = decision_advice -> 发布 -> 消费 -> 查看 structured_result | decision_advice 模板必填字段全部存在且类型正确 |

## US-17：业务输出配置体验可用

### 程序化 UI 测试

| # | 用例 | 验证点 |
|---|------|--------|
| F58 | 业务输出配置页面 | 4 模板卡片并列展示，选中后高亮 |
| F59 | 模板选择后字段列表展示 | 每字段显示中文名、英文名、业务含义、必填性、示例值 |
| F60 | AI 推荐 output_type 标注 | AI 推荐类型标注推荐理由 |
| F61 | 保存确认弹窗版本快照提示 | 弹窗明确提示"配置进入版本快照，修改需创建新版本" |
| F62 | published 角色 output_type 不可修改 | 提示"已发布角色的输出类型不可修改，需创建新版本" |

### 人工手动冒烟

| # | 用例 | 验证点 |
|---|------|--------|
| H15 | 人工进入角色编辑 -> 配置业务输出 -> 选择模板 -> 确认保存 | 配置流程完整可用，output_type 和 output_schema 进入版本快照 |

## US-18：资产市场 AI 推荐可用

### 自动化 API 测试

| # | 用例 | 验证点 |
|---|------|--------|
| A88 | AI 推荐接口调用（输入业务意图） | 返回匹配的已发布角色列表 + 推荐理由 |
| A89 | AI 推荐接口调用（无匹配意图） | 返回空结果 + 运营信号记录 |
| A90 | 已发布角色列表查询 | 只返回 published 状态且具备 output_type 的角色 |

### 程序化 UI 测试

| # | 用例 | 验证点 |
|---|------|--------|
| F63 | 资产市场首页 | 展示场景入口 + AI 推荐输入 + 已发布角色列表 |
| F64 | 场景入口卡片 | 4 场景分类卡片可见可点击（决策支持/风控分析/制度合规/审查评审） |
| F65 | AI 推荐输入和结果 | 输入意图后展示推荐角色卡片（含推荐理由、适用问题、输出类型） |
| F66 | 角色卡片信息 | 卡片含角色名称、output_type、capability_level、业务域、适用场景 |
| F67 | 无匹配提示 | 无匹配时不硬推荐，提示"当前角色资产缺口"，记录运营信号 |
| F68 | applicable_scenarios 缺失标注 | 角色缺少 applicable_scenarios 时标注"适用场景待补充" |
| F69 | legacy 角色资产市场展示 | 标注"需升级"，不提供试用和消费入口按钮，只提供"升级版本"引导 |

### 人工手动冒烟

| # | 用例 | 验证点 |
|---|------|--------|
| H16 | 人工进入资产市场 -> 输入意图 -> 查看 AI 推荐结果 -> 点击试用 | 推荐流程完整可用，跳转到使用台消费页面 |

## US-19：决策产品集成证据闭合

### 集成验证

| # | 用例 | 验证点 |
|---|------|--------|
| I01 | 角色产品侧集成准备里程碑（本地 readiness 证据） | consume API 可被外部 HTTP 调用消费，返回完整固定治理外壳 |
| I02 | 角色产品侧证据链准备里程碑（本地 readiness 证据） | usage_record 包含 caller_type = decision_product + caller_id + role_version_id + status + boundary_status + structured_result |
| I03 | 决策产品真实场景消费 | 决策产品传入业务上下文调用 consume API，展示 decision_advice 结构化结果 |
| I04 | 双方证据闭合 | 角色产品侧 usage_record 与决策产品侧决策记录互相对上（role_id/role_version_id/usage_record_id/caller_id 对应） |
| I05 | 非 success 状态处理验证 | 决策产品正确处理 boundary_blocked/insufficient_context/system_failed 状态 |

注：I03~I05 需终审方协调决策产品团队配合。I01~I02 为角色产品侧集成准备里程碑（本地 readiness 证据），不等于 DD-14 验收通过。DD-14 通过条件为 I03~I05 全部闭合；若外部配合窗口未就绪，应记录为外部阻塞，不得自动降级为 I01~I02 即通过。

## US-20：Dify 消费证明通过

### Dify 集成验证

| # | 用例 | 验证点 |
|---|------|--------|
| D01 | Dify HTTP Tool 配置 | 配置 consume API URL (POST)、方法、Headers (X-API-Key)、请求参数映射、响应参数映射 |
| D02 | Dify Workflow 调用 consume API | Dify 成功调用 consume API，返回完整固定治理外壳 |
| D03 | Dify 展示消费结果 | Dify 展示角色 answer + structured_result + status |
| D04 | 角色 product 侧 usage_record 对上 | usage_record 中 caller_type = agent_platform, caller_id = Dify workflow ID, role_version_id 与 Dify 调用一致 |
| D05 | Dify 处理非 success 状态 | boundary_blocked → Dify 展示阻断提示；system_failed → Dify 展示错误信息 |
| D06 | Dify 集成代表场景完整链路 | 合同风险分析 Agent 完整场景走通（用户输入合同条款 -> Dify Workflow -> consume API -> 角色 product 返回 risk_analysis -> Dify 展示消费结果） |

### Dify 侧验收证据

| # | 验证点 |
|---|---|
| D-E01 | Dify Workflow/Agent 配置截图（含 HTTP Tool 配置） |
| D-E02 | 实际调用日志（请求参数 + 响应内容） |
| D-E03 | 消费结果展示截图（risk_analysis 结构化输出展示） |
| D-E04 | 非 success 状态处理截图（boundary_blocked 或 system_failed 的处理） |

### 角色 product 侧验收证据

| # | 验证点 |
|---|---|
| D-E05 | usage_record 中 caller_type = agent_platform 的记录截图 |
| D-E06 | usage_record 中 caller_id = Dify workflow ID 的记录 |
| D-E07 | usage_record 中 role_version_id 和 role_id 的记录 |
| D-E08 | consume API 响应的完整 JSON（含固定治理外壳） |

## US-21：6 状态判定正确

### 自动化 API 测试（6 状态命中路径）

| # | 用例 | 验证点 |
|---|------|--------|
| A91 | consume API status = success | boundary_status 两维度均为 within_boundary 或 near_boundary；structured_result 包含模板必填字段；output_type 非空 |
| A92 | consume API status = boundary_blocked | boundary_status 至少一个维度为 out_of_scope；structured_result 为空对象 {}；answer 包含边界阻断说明和建议 |
| A93 | consume API status = insufficient_context | boundary_status 两维度均为 within_boundary；answer 包含需补充信息提示 |
| A94 | consume API status = insufficient_knowledge | knowledge_boundary 为 near_boundary 或 within_boundary；capability_boundary 为 within_boundary；answer 包含知识不足说明 |
| A95 | consume API status = system_failed（已处理的下游失败：LLM 超时/不可达但系统仍能返回治理外壳） | 返回 HTTP 200 + 固定治理外壳；boundary_status 两维度均为 not_applicable；structured_result 为空对象 {}；answer 包含系统错误提示；生成 usage_record；计入 6 状态统计 |
| A96 | consume API status = undefined | boundary_status 两维度均为 not_applicable；answer 包含人工复核提示 |

### 自动化 API 测试（boundary_status 联动校验）

| # | 用例 | 验证点 |
|---|------|--------|
| A97 | status = success 时 boundary_status 不得有 out_of_scope 或 not_applicable | 后端校验规则：success 时两维度仅允许 within_boundary 或 near_boundary |
| A98 | status = boundary_blocked 时至少一个维度为 out_of_scope | 后端校验规则：boundary_blocked 时至少一维度 out_of_scope |
| A99 | status = insufficient_context 时两维度均为 within_boundary | 后端校验规则：insufficient_context 不允许 near_boundary |
| A100 | status = system_failed 或 undefined 时两维度均为 not_applicable | 后端校验规则：system_failed/undefined 时两维度 not_applicable |

### 自动化 API 测试（v0.3 legacy 角色消费）

| # | 用例 | 验证点 |
|---|------|--------|
| A101 | legacy published 角色（缺少 output_type）使用台消费（caller_type: human） | 200 返回固定治理外壳；output_type = null；structured_result = {}；status = success；answer 包含"该版本未配置结构化输出（需升级）"提示 |
| A102 | legacy published 角色 Dify 消费（caller_type: agent_platform） | 400 返回错误；提示"该角色版本不满足 v0.4 消费标准（缺少业务输出配置），请使用已配置输出类型的版本" |
| A103 | legacy published 角色决策产品消费（caller_type: decision_product） | 400 返回错误；同 A102 规则 |
| A104 | legacy 角色缺少 capability_level 时使用台消费 | 按 A1 处理 |
| A105 | legacy 角色缺少 capability_level 时 Dify/决策产品消费 | 400 返回错误 |

### 自动化 API 测试（consume API 错误与 6 状态分离）

| # | 用例 | 验证点 |
|---|------|--------|
| A106 | HTTP 400（role_version_id 不属于 role_id） | 不返回固定治理外壳；不生成 usage_record；不计入 6 状态统计；响应为 `{ "detail": "指定的版本不属于该角色" }` |
| A107 | HTTP 403（draft/test 状态角色） | 不返回固定治理外壳；不生成 usage_record；不计入 6 状态统计 |
| A108 | HTTP 404（role_id 不存在） | 不返回固定治理外壳；不生成 usage_record；不计入 6 状态统计 |
| A109 | HTTP 500（未捕获服务异常：框架崩溃/数据库连接断开等系统无法生成治理外壳） | 不返回固定治理外壳；不生成 usage_record；不计入 6 状态统计；作为"服务可用性异常"单独统计 |

### 程序化 UI 测试（消费结果状态展示）

| # | 用例 | 验证点 |
|---|------|--------|
| F70 | success 状态展示 | 绿色标识 + 中文名"成功" + status_reason |
| F71 | boundary_blocked 状态展示 | 阻断标识 + 中文名"边界阻断" + boundary 命中分析面板高亮越界维度 |
| F72 | insufficient_context 状态展示 | 提示标识 + 中文名"上下文不足" + 补充信息提示 |
| F73 | insufficient_knowledge 状态展示 | 提示标识 + 中文名"知识不足" + 知识不足说明 |
| F74 | system_failed 状态展示 | 错误标识 + 中文名"系统失败" + 重试按钮 |
| F75 | undefined 状态展示 + 人工复核提示 | 中文名"未定义" + 提示人工复核 |

### 人工手动冒烟

| # | 用例 | 验证点 |
|---|------|--------|
| H17 | 人工消费 published 角色 -> success 状态 | 6 状态正确展示，boundary_status 与声明对比正确，structured_result 合规 |
| H18 | 人工消费 test 角色（测试台）-> boundary_blocked 状态 | boundary 命中分析面板高亮越界维度，联动校验一致 |
| H19 | 人工消费 legacy published 角色（使用台） | output_type = null 标注，answer 中"需升级"提示清晰可见 |

## UI/UX 人工冒烟专项

### Human 使用习惯专项检查（跨全部核心流程）

| # | 检查项 | 验证点 |
|---|------|--------|
| UX01 | 文案是否业务化 | 所有 UI 文案使用业务语言而非技术术语；status 中文名而非枚举值；模板字段中文名而非英文名 |
| UX02 | 字段是否有解释和示例 | 每个配置字段有中文说明、业务含义和示例值；output_schema 模板每字段有示例 |
| UX03 | 按钮顺序是否符合操作习惯 | 主操作按钮在右侧，取消/返回在左侧；确认弹窗确认在右，取消在左 |
| UX04 | 危险操作是否有确认 | 发布角色、修改 published 版本字段等不可逆操作有确认弹窗 |
| UX05 | 错误提示是否可理解可恢复 | 错误提示使用中文说明原因和建议动作；不使用技术错误码；提供重试/返回/替代路径 |
| UX06 | 长文本是否可读可滚动 | answer、structured_result 详情等长文本区域有滚动条；不截断内容 |
| UX07 | 多数据列表是否可搜索筛选 | 角色列表有基础搜索；运营看板数据按维度分组 |
| UX08 | 保存/发布/返回/取消状态是否明确 | 每个页面标注当前操作状态；按钮文案清晰（不是"OK""Submit"） |
| UX09 | AI 生成内容是否可区分 | AI 生成字段标注"AI 生成"或"AI 推荐"；用户可看出哪些是 AI 产出 |
| UX10 | 消费状态是否一目了然 | success 有绿色标识；非 success 有对应颜色和图标；boundary_blocked 不误认为"失败" |

## 类型标注说明

| 标注 | 含义 |
|---|---|
| 自动化 API | pytest 覆盖，运行 `venv/bin/pytest -q` |
| 程序化 UI | 前端构建通过 + 页面渲染验证 |
| 人工手动冒烟 | 由人实际操作 React 入口验证 |
| 集成验证 | 跨项目真实场景调用验证（Dify / 决策产品） |
| UI/UX 人工冒烟 | Human 使用习惯专项检查清单走查 |

## 与旧口径的变更说明

以下旧口径已删除：

- ~~"DD-04 不改变接口"~~ — 已升级为新增统一消费 API（POST /role-assets/{role_id}/consume）
- ~~"DD-04 消费侧 API 设计说明文档"~~ — 已升级为实际 API 设计与实现
- ~~"US-09 无新增或修改的 API 路径"~~ — 已删除，consume API 是新增写入接口
- ~~"使用台需要新增读写接口时必须先回写 dossier"~~ — 已回写并经规划方裁决批准
