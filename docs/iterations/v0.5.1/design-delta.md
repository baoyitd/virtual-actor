# v0.5.1 设计增量

> 基线来源：v0.5.0 已冻结设计 + Knowledge Workbench 公共契约接口冻结定义（`design-freeze-public-contract-interfaces.zh-CN.md`）
> 用途：只记录本轮相对基线的增量，不重复抄写全量设计
> 裁决依据：`adjudication-knowledge-interface-ownership-change-2026-06-17.md`

## 1. 背景与目标

v0.5.0 验收后，执行公共契约裁决落地的知识平台接口对接点变更。角色产品从直接调用 Open WebUI 端点切换到 Knowledge Workbench 公共契约接口，获取协议层输出（分层元数据、tier 过滤后的检索结果）。

## 2. 关键变化

| 设计项 | 决策 | 影响范围 |
|---|---|---|
| DD-25 | `knowledge_platform.py` 对接点从 Open WebUI 切换到 Knowledge Workbench：`/api/packages` → 库列表；`/api/packages/{id}/manifest` → 结构化元数据；`/api/packages/{id}/retrieve` → 检索；`/api/packages/{id}/status` → 版本标识+健康检查 | `knowledge_platform.py`、`role_service.py`（知识绑定）、`consume_service.py`（检索调用） |
| DD-26 | 检索结果从扁平 chunks（chunk+source+score）变更为分层命中（含 tier/doc_role/evidence_type/source_reference/score/line_start/line_end） | `consume_service.py` 检索结果处理；`PromptBuilder` 知识注入格式 |
| DD-27 | 说明卡生成利用 manifest 的 tier 分布输出"绑定N篇P1+M篇P2"结构化描述 | `briefing_service.py` 说明卡生成逻辑 |
| DD-28 | 版本标识从 `GET /api/v1/version` 切换到 `GET /api/packages/{id}/status` 的 version_id（git commit hash 优先，manifest SHA 回退） | `role_service.py` 发布时版本快照 |
| DD-29 | 健康检查从 Open WebUI 认证接口切换到 Knowledge Workbench status 接口 | `knowledge_platform.py` health() |
| DD-30 | 接口基线文档更新 | `role-to-knowledge-integration-proposal.md` |
| DD-31 | 03 试用与测试页面信息架构调整：baseline-strip（4个大chip+混按钮）改为紧凑信息栏；"返回02"按钮移到顶部back-link区域；测试查询section提到页面第一个核心位置 | `RoleTest.tsx` |
| DD-32 | 04 治理与发布页面信息架构调整：metric-row（4个状态chip）改为紧凑状态栏；版本级动作（发布/归档）从页面最底部提前到治理表单之后；证据概况和准备度卡片降级为底部参考区 | `RoleGovernance.tsx` |
| DD-33 | 06 外供与追溯页面信息架构调整：RoleBriefingCard（大卡片）移除改为紧凑状态栏；4个overview-card移除压缩到状态栏；生成Tool/Skill包按钮提前到页面第一个核心section；"刷新"按钮移到顶部back-link区域不再和生成按钮混排 | `RoleExports.tsx` |
| DD-34 | 治理页表单交互变更：Owner/Maintainer 从自由文本改为下拉选择（数据源：系统用户列表）；业务域从自由文本改为下拉选择（数据源：business_domains 表）；企业实际角色映射从 textarea 改为多选下拉（数据源：enterprise_roles 表，按已选业务域过滤）；标签从逗号分隔文本改为 chip 组件（输入+回车添加，点×删除） | `RoleGovernance.tsx`、新增 `config` API |
| DD-35 | 新增 `business_domains` 表（业务域枚举）和 `enterprise_roles` 表（企业实际角色，FK→business_domains）。初始化快消品行业 12 个业务域 + 30 个核心角色。新增配置管理 API（GET/POST/PATCH/DELETE） | `models/business_domain.py`、`models/enterprise_role.py`、`routers/config.py`、迁移脚本 |
| DD-36 | 消费回答机制重构为两次调用：第1次 LLM 以角色立场自由回答产出完整原文；第2次 LLM 从原文中按 output_type 模板提取结构化字段（temperature=0.1）。自由输出模式仍为单次调用。移除 `_finalize_answer` 的截断知识摘要追加逻辑 | `consume_service.py` |
| DD-37 | 说明卡 source hash 移除 `business_domain`：业务域是治理元数据，不是角色定义，不应因治理页修改而反向导致说明卡 stale | `briefing_service.py` |
| DD-38 | 说明卡 source hash 移除 `validation_summary`：测试结果不是角色定义，每次新测试不应导致说明卡变 stale | `briefing_service.py` |
| DD-39 | 04 治理页操作区重构：保存+发布合并到同一操作区；发布成功后显示 banner + 引导下一步；已发布且无变更时发布按钮禁用；归档增加确认弹窗（说明后果+确认/取消）；准备度卡片+证据概况合并为统一"发布前检查"清单 | `RoleGovernance.tsx` |
| DD-40 | 合并 05 正式消费 + 06 外供与追溯为统一页面"外供与调用"：取消 05 页面（UsageDesk.tsx），将其消费功能合并到 06（RoleExports.tsx）；模拟调用支持全部 caller_type（human/external_tool/external_skill）；记录显示全部类型；新增"调用方式说明"section（API 地址、请求格式、Dify/Codex 使用引导）；RoleStageNav 从 6 步改为 5 步；全局链接从 `/use` 改为 `/exports` | `UsageDesk.tsx`（删除）、`RoleExports.tsx`（重写）、`RoleStageNav.tsx`、`App.tsx`、`RoleList.tsx`、`RoleDetail.tsx`、`Marketplace.tsx` |
| DD-41 | retrieve/route 端点路径调整为独立端点（裁决落地）：retrieve 从 `POST /api/packages/{package_id}/retrieve` 改为 `POST /api/retrieve`；route 从 `POST /api/packages/{package_id}/route` 改为 `POST /api/route`；retrieve 调用时传入 `knowledge_object_ids` 限定检索范围为角色绑定文档；package_id 不再参与运行态检索范围定义 | `knowledge_platform.py`、`consume_service.py` |

## 3. 数据与状态变化

### 3.1 接口端点变更

| 原端点（Open WebUI） | 新端点（Knowledge Workbench） | 用途 |
|---|---|---|
| `GET /api/v1/knowledge/` | `GET /api/packages` | 知识库列表 |
| `GET /api/v1/knowledge/{kb_id}/files` | `GET /api/packages/{package_id}/manifest` | 知识对象清单（含 tier/doc_role/evidence_type） |
| `POST /api/v1/retrieval/query/collection` | `POST /api/packages/{package_id}/retrieve` | RAG 检索（含 tier 标注 + 路由） |
| `GET /api/v1/version` | `GET /api/packages/{package_id}/status` | 版本标识 + 健康检查 |

### 3.2 检索结果结构变更

原结构（Open WebUI）：

```json
{"chunk": "...", "source": "...", "score": 0.95}
```

新结构（Knowledge Workbench）：

```json
{
  "route": {"question_type": "Q1", "allowed_tiers": ["P1"], ...},
  "hits": [
    {
      "doc_id": "...", "title": "...", "relative_path": "...",
      "tier": "P1", "doc_role": "master_doc", "evidence_type": "theory",
      "score": 41.6, "line_start": 866, "line_end": 866,
      "snippet": "...", "source_reference": "master/core-thesis.md#L866"
    }
  ]
}
```

### 3.3 越界拒答处理

简化模式下 retrieve 内部执行路由，Q0 越界时返回 `refused: true` + `refusal_reason`，hits 为空。角色消费时需处理此拒答 payload。

### 3.4 数据库结构

无变化。role_assets/role_versions/knowledge_refs 等表结构不变。knowledge_object_id（文件路径型）和 knowledge_version_id（Git commit hash）格式不变。

## 4. 风险与边界

1. **Open WebUI 适配器未就绪**：当前 Knowledge Workbench retrieve 使用确定性评分器，检索质量不足。在适配器就绪前不进行代码切换。已上提反馈（`role-to-knowledge-execution-risk-feedback-2026-06-17.md`）。
2. **evidence_tier 标注不在本轮**：L4 output_schema 已冻结，evidence_tier 需走设计变更流程，是后续迭代项（裁决追踪）。
3. **认证机制**：Knowledge Workbench 当前无 auth，角色产品当前可工作，后续 auth 方案需双方共同定义。
4. **多知识包**：当前只有 master 一个包，接口结构预留多包扩展。

## 5. 待裁决项

| 裁决项 | 说明 | 状态 |
|---|---|---|
| Open WebUI 适配器就绪时间 | 知识平台未给出明确时间点 | 待回应 |
| evidence_tier 标注纳入迭代 | 后续迭代项，裁决追踪 | 追踪中 |
