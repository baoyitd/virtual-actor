# v0.5.1 范围说明

> 版本：v0.5.1
> Formal Status：Draft
> 最后更新：2026-06-26
> 前置文档：`adjudication-knowledge-interface-ownership-change-2026-06-17.md`（裁决）、`role-to-knowledge-consensus-confirmation-2026-06-17.md`（共识）、v0.5.0 dossier

## 1. 本轮目标

v0.5.0 验收后，执行公共契约裁决落地后的知识平台接口对接点变更。

裁决事项：角色产品对知识平台的接口对接点从 Open WebUI 变更为 Knowledge Workbench 公共契约接口。Open WebUI 退为知识平台内部执行适配层。

本轮解决：让角色产品的知识消费链路对接到 Knowledge Workbench 协议层接口，获取分层元数据（tier/doc_role/evidence_type）和 tier 过滤后的检索结果，替代当前扁平的 Open WebUI 检索。

## 2. Scope In

| ID | 范围项 | 优先级 | 说明 |
|---|---|---|---|
| DD-25 | 知识平台接口对接点变更 | P0 | `knowledge_platform.py` 从 Open WebUI 端点切换到 Knowledge Workbench 端点（packages/manifest/retrieve/status） |
| DD-26 | 检索结果结构适配 | P0 | `consume_service.py` 适配 retrieve 返回的新结构（含 tier/doc_role/evidence_type/source_reference） |
| DD-27 | 说明卡结构化知识范围描述 | P0 | 利用 manifest tier 分布生成"3篇P1+5篇P2+2篇P3"结构化描述 |
| DD-28 | 知识版本标识适配 | P0 | 从 `/api/v1/version` 切换到 `/api/packages/{id}/status` 的 version_id |
| DD-29 | 健康检查适配 | P0 | 从 Open WebUI 认证接口切换到 Knowledge Workbench status 接口 |
| DD-30 | 接口基线文档更新 | P0 | `role-to-knowledge-integration-proposal.md` 更新为 Knowledge Workbench 接口版本 |
| DD-31 | 03 试用与测试页面信息架构调整 | P1 | baseline-strip改为紧凑信息栏，测试查询提前为核心section，返回按钮移到顶部 |
| DD-32 | 04 治理与发布页面信息架构调整 | P1 | metric-row改为紧凑状态栏，版本级动作提前到治理表单之后，证据概况和准备度卡片降级 |
| DD-33 | 06 外供与追溯页面信息架构调整 | P1 | RoleBriefingCard移除改为紧凑状态栏，生成按钮提前到第一个核心section，overview压缩 |
| DD-34 | 治理页表单交互变更 | P1 | Owner/Maintainer下拉用户、业务域下拉、企业角色多选、标签chip组件 |
| DD-35 | 新增 business_domains + enterprise_roles 表 | P0 | 建表、迁移脚本、初始数据（12业务域+30角色）、配置管理API |
| DD-36 | 消费回答两次调用机制 | P1 | 先原文后结构化，回答质量优先 |
| DD-37 | 说明卡source hash移除business_domain | P1 | 业务域是治理元数据不应反向导致stale |
| DD-38 | 说明卡source hash移除validation_summary | P1 | 测试结果不是角色定义，每次新测试不应导致说明卡stale |
| DD-39 | 04 治理页操作区重构 | P1 | 保存+发布合并、发布成功提示、已发布拦截、归档确认弹窗、发布前检查清单 |
| DD-40 | 合并 05+06 为统一"外供与调用"页 | P1 | 取消05页面，消费功能合并到06，模拟调用支持全caller_type，新增调用方式说明，导航改5步 |
| DD-41 | retrieve/route 端点路径调整 + knowledge_object_ids | P0 | retrieve 改为 `/api/retrieve`，传入 knowledge_object_ids 限定检索范围 |

## 3. Scope Out

1. evidence_tier 标注（核心结论字段知识支撑层级）不在本轮范围——L4 output_schema 已冻结，需走设计变更流程，是后续迭代项（裁决追踪）
2. 不改变角色产品自身数据模型（role_assets/role_versions/knowledge_refs 等表结构不变）
3. 不改变角色产品消费 API 的外部接口（消费方无感知）
4. 不实现角色产品的路由接口对接（route 接口按需使用，非本轮强依赖）
5. 不承担 Knowledge Workbench 接口开发义务（知识平台侧工作）
6. 不在 Open WebUI 适配器就绪前做代码切换——当前 Knowledge Workbench retrieve 使用确定性评分器，检索质量不足以支撑生产级语义检索，等待知识平台完成裁决 §5.2 步骤3 后再启动联调

## 4. 核心场景链

| ID | 场景 | 成功标准 |
|---|---|---|
| US-31 | 角色消费时知识检索获取分层结果 | retrieve 返回结果含 tier/doc_role/evidence_type；角色回答中可区分制度级与参考级引用 |
| US-32 | 角色发布时知识版本快照 | 从 Knowledge Workbench status 获取 version_id，发布时快照记录 |
| US-33 | 说明卡生成结构化知识范围 | 说明卡展示"绑定N篇P1+M篇P2"结构化描述 |
| US-34 | 知识平台健康检查 | 消费前确认 Knowledge Workbench 可达 |
| US-35 | 03 测试页面核心功能突出 | 用户进入测试页即看到查询输入框，不被角色信息条带挤压 |
| US-36 | 04 治理页发布动作可达 | 用户进入治理页后无需滚动翻阅大量信息即可看到发布按钮 |
| US-37 | 06 外供页生成动作可达 | 用户进入外供页即看到生成Tool/Skill包按钮，不被说明卡和overview挤压 |
| US-38 | 治理页表单标准化选择 | Owner/Maintainer从用户列表选、业务域从枚举选、企业角色按业务域多选、标签chip式管理 |
| US-39 | 消费回答完整原文 | 结构化模式下自然语言回答是LLM完整原文，不是摘要 |
| US-40 | 说明卡不受治理修改影响 | 在04页保存治理项不导致02页说明卡变stale |
| US-41 | 治理页操作流畅 | 保存+发布一气呵成；发布后有成功提示和引导；归档有确认弹窗 |
| US-42 | 发布前检查清晰 | 发布前检查清单统一展示，不再分准备度卡片和证据概况两个重复section |
| US-43 | 发布后对外可用统一入口 | 一个页面承载外供包生成、调用方式说明、验证调用和全部调用记录，不再分05/06两个页面 |
| US-44 | 角色消费只检索绑定知识 | retrieve 传入 knowledge_object_ids，只检索角色绑定的文档，未绑定的文档不参与检索 |

## 5. 非目标与禁止动作

1. 不在知识平台 Open WebUI 适配器未就绪时进行代码切换。
2. 不自行修改 v0.5.0 已冻结的 L4 output_schema（evidence_tier 是后续迭代）。
3. 不单方面变更知识平台接口契约。
4. 不改变 knowledge_object_id（文件路径型）和 knowledge_version_id（Git commit hash）格式——已由 Lead 裁决。

## 6. 验收标准

1. `knowledge_platform.py` 全部对接 Knowledge Workbench 端点，不再调用 Open WebUI。
2. `consume_service.py` 正确处理 retrieve 返回的分层结构。
3. 说明卡生成逻辑利用 manifest tier 分布输出结构化描述。
4. 角色发布时从 Knowledge Workbench status 获取 version_id。
5. pytest / frontend build / markdownlint / Vale / iteration-guard 全链路通过。
6. 与 Knowledge Workbench 联调验证运行态闭环。
7. 检索质量不低于当前对接 Open WebUI 的水平（依赖 Open WebUI 适配器就绪）。

## 7. 前置依赖

| 依赖项 | 提供方 | 当前状态 |
|---|---|---|
| 裁决落地 | 组合层 | 已通过 |
| Knowledge Workbench 公共契约接口就绪 | 知识平台 | 接口已交付，22/22 测试通过 |
| Knowledge Workbench Open WebUI 适配器就绪 | 知识平台 | **未完成**——当前使用确定性评分器。知识平台 06-22~06-23 期间将公共契约接口部署到运行环境并通知就绪，角色产品据此启动代码切换（授权路径见 implementation-notes §2.1）。Open WebUI 适配器就绪后需重新联调验证检索质量。 |

## 8. 停止条件

1. ~~若 Knowledge Workbench Open WebUI 适配器未就绪，不进行代码切换。~~ **已解除**：知识平台 06-22~06-23 期间将公共契约接口部署到运行环境并通知就绪，角色产品据此启动代码切换。Open WebUI 适配器仍未实现（retrieve 使用确定性评分器），检索质量回退作为已知偏差记录（见 implementation-notes §1 偏差记录）。
2. 若联调中发现接口契约与共识约定不一致，停止并上提。
