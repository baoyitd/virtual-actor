# v0.4.0 Dify 集成技术评估

> 版本：v0.4.0 | 日期：2026-05-26 | Formal Status：Draft
> 类型：技术评估短文
> 目的：评估 Dify 作为开放 Agent 平台 MVP 代表的接入方式，为规划方裁决提供依据
> 前置依赖：consume-api-design.md

---

## 1. Dify 当前支持的接入方式

Dify 是一个开源 LLM 应用开发平台，支持多种接入外部工具/API 的方式。以下能力判断基于 Dify 官方文档（访问日期 2026-05-26）：

| 接入方式 | Dify 名称 | 原理 | 官方文档依据 | 适用场景 |
|---|---|---|---|---|
| HTTP Request / HTTP Tool | 自定义工具 | 在 Workflow/Agent 中注册外部 HTTP API 作为 Tool，配置 URL、方法、请求头、参数和响应格式 | Dify 官方文档 HTTP Request 节点（https://docs.dify.ai/en/use-dify/nodes/http-request）和 Tools 章节（https://docs.dify.ai/en/use-dify/workspace/tools）明确支持外部 API 调用，Workflow 中 HTTP Request 节点为标准能力 | 最灵活，适合 REST API 调用 |
| OpenAPI Schema 导入 | 导入 OpenAPI 规范 | 将 OpenAPI (Swagger) YAML/JSON 导入 Dify，自动生成可用的 Tool | Dify 官方文档 Tools 章节（https://docs.dify.ai/en/use-dify/workspace/tools）支持 OpenAPI 规范导入，Tool 类型中包含 API-based Tool | API 有标准文档时最省配置 |
| 自定义插件 | Dify Plugin | 编写 Dify 插件代码，实现更复杂的逻辑（如认证、数据转换、多步调用） | Dify 官方文档 Plugins 章节（https://docs.dify.ai/en/use-dify/workspace/plugins）描述插件开发框架和安装机制 | 需要复杂预处理或自定义认证时 |

v0.4 MVP 不作为最低可用证明路径的接入方式（后续增强候选）：

| 方式 | 理由 |
|---|---|
| MCP Server | Dify 官方文档已确认支持 MCP Server 能力（https://docs.dify.ai/en/use-dify/publish/publish-mcp 描述 MCP Server 发布流程），但 v0.4 为降低集成变量，优先采用 HTTP Request/HTTP Tool；MCP 能力作为后续增强候选，不作为本轮最低证明路径 |
| A2A 适配 | A2A 协议更早期，无可用实现 |
| Dify 内置知识库+模型直接模拟角色 | 这不是"消费角色资产"，而是绕过角色产品自行回答，不符合验收语义 |

---

## 2. 各方式对比评估

### 2.1 HTTP API Tool（推荐 MVP 方式）

**开发量**：低

- 仅需在 Dify Workflow/Agent 中配置一个 HTTP Tool
- 配置内容：URL (consume API endpoint)、Method (POST)、Headers (Content-Type + 认证)、Request Body Schema、Response Body Schema
- 角色产品侧无需额外开发——consume API 已定义完整输入输出

**稳定性**：高

- HTTP 是最基础的网络调用方式
- Dify 的 HTTP Tool 功能成熟，社区广泛使用
- 依赖最少——只需 consume API 端点可访问

**限制**：

1. Dify HTTP Tool 需手动配置请求参数映射，对 consume API 的固定治理外壳输出需要逐一映射展示字段
2. 认证方式受限于 Dify HTTP Tool 支持的认证类型（API Key Header / Bearer Token / Basic Auth）
3. 消费结果中的 structured_result、boundary_status 等复杂嵌套 JSON 需要 Dify Workflow 后续节点解析

**对 consume API 设计的影响**：

- consume API 的输入模型已兼容 HTTP 调用（role_id 在 URL path，其余字段在 request body）
- 无需修改 consume API 设计

### 2.2 OpenAPI Schema 导入

**开发量**：低（如果已有 OpenAPI 文档）

- 需要产出 consume API 的 OpenAPI 3.0 规范文件
- Dify 导入后自动生成 Tool 配置
- 比 HTTP API Tool 更省手动配置

**稳定性**：中

- OpenAPI 导入依赖规范文件的完整性和正确性
- Dify 对复杂嵌套 JSON Schema 的导入解析有时不够准确
- 需要测试导入后的 Tool 参数映射是否完整

**限制**：

1. 需要额外产出和维护 OpenAPI 规范文件（v0.4 的 consume API 是候选接口，OpenAPI 文档变更频繁）
2. Dify 对 OpenAPI 3.0 的部分特性支持不完整（如 nested object schema、enum validation）
3. boundary_status 复合结构和 structured_result 的嵌套 Schema 可能在导入时简化

**对 consume API 设计的影响**：

- 如果选择此方式，需要产出 consume API 的 OpenAPI 3.0 YAML/JSON
- consume API 的输出 Schema 需要表达为 OpenAPI 可解析的结构

### 2.3 自定义插件

**开发量**：中-高

- 需编写 Python 代码，实现 Dify Plugin 接口
- 插件需要处理：认证、请求构造、响应解析、错误处理、状态判定展示
- 需在 Dify 插件市场注册或本地部署

**稳定性**：中

- 插件代码需要维护和更新
- Dify 插件框架版本变化可能导致兼容性问题
- 开发和调试成本高于 HTTP Tool

**限制**：

1. 开发周期长，不适合 MVP 最低可用证明
2. 插件需要在 Dify 端安装部署，增加了环境依赖
3. MVP 目标是"证明开放 Agent 平台可以消费已发布角色资产"，不是"产出完美的 Dify 插件"

**对 consume API 设计的影响**：

- 插件内部仍调用 consume API HTTP 端点
- 无额外设计影响，但增加维护成本

---

## 3. 推荐 MVP 接入方式及理由

**推荐：HTTP API Tool**

理由：

1. **最低开发量**：角色产品侧无需额外开发，Dify 端仅需配置一个 HTTP Tool。
2. **最高稳定性**：HTTP 调用是最成熟、依赖最少的接入方式。
3. **验收语义清晰**：Dify Workflow 调用 consume API → 角色产品返回固定治理外壳 → Dify 展示消费结果 → 角色产品生成 usage_record → 双方可追溯。这条链路符合 DD-15 的验收要求。
4. **不影响 consume API 设计**：consume API 的路径、输入输出结构完全兼容 HTTP Tool 调用。
5. **后续可升级**：v0.4.x 可补 OpenAPI Schema 文档或自定义插件，不改变 consume API 设计。

v0.4.x 扩展建议：

1. 产出 consume API 的 OpenAPI 3.0 规范文件，供 Dify 导入和更便捷配置。
2. 产出 Dify HTTP Tool 配置模板（含请求参数映射示例），供其他开放平台复用。
3. v0.5 视协议成熟度评估 MCP/A2A 适配。

---

## 4. Dify 集成代表场景技术链路

以"合同风险分析 Agent"为例，展示完整技术链路：

```text
Dify Workflow 接收用户输入（合同条款文本）
→ Dify HTTP Tool 调用 POST /role-assets/{role_id}/consume
  - role_id: 已发布风险分析角色 UUID
  - query: 合同条款文本
  - context: "合同审查场景，需关注违约金、付款条件、责任限制"
  - caller_type: agent_platform
  - caller_id: Dify workflow ID
→ 角色产品 consume API 处理请求
  - 选择当前 published 版本
  - LLM 调用生成 risk_analysis 结构化输出
  - 返回固定治理外壳 + structured_result (risk_analysis 模板)
→ Dify Workflow 接收响应
  - 解析 status、structured_result、boundary_status
  - 展示风险项、严重等级、建议缓解措施
  - 处理非 success 状态（boundary_blocked 时提示换角色）
→ 角色产品生成 usage_record
  - caller_type: agent_platform
  - caller_id: Dify workflow ID
  - role_version_id: 实际消费版本
  - status / boundary_status / structured_result 全量记录
→ 双方验收证据闭合
```

---

## 5. 认证与安全考虑

### 5.1 认证方式

v0.4 consume API 的认证方案：

1. Dify HTTP Tool 通过 API Key Header 方式传递认证（`X-API-Key: <key>`）
2. API Key 在角色产品管理台生成，配置到 Dify HTTP Tool
3. v0.4 不实现 RBAC 和权限管理，API Key 作为最低可用认证方式

### 5.2 安全边界

1. consume API 只接受 published 状态角色消费请求，不允许消费 draft/test 状态角色
2. API Key 只授权消费（POST /consume），不授权管理操作
3. v0.4 不实现消费权限校验（基于 visibility 字段），后续版本补齐

---

## 6. 验收证据格式

Dify 侧需提交：

1. Dify Workflow/Agent 配置截图（含 HTTP Tool 配置）
2. 实际调用日志（请求参数 + 响应内容）
3. 消费结果展示截图（risk_analysis 结构化输出展示）
4. 非 success 状态处理截图（至少 boundary_blocked 或 system_failed 的处理）

角色产品侧需提交：

1. usage_record 中 caller_type = agent_platform 的记录截图
2. usage_record 中 caller_id = Dify workflow ID 的记录
3. usage_record 中 role_version_id 和 role_id 的记录
4. consume API 响应的完整 JSON（含固定治理外壳）

---

## 7. 与 DD 项的支撑关系

| DD 项 | Dify 技术评估支撑点 |
|---|---|
| DD-15 | Dify 作为开放 Agent 平台消费代表的接入方式、技术链路和验收证据 |
| DD-04 | consume API 的 Dify 消费端验证 |
| DD-14 | 决策产品集成可参考 Dify 的 HTTP Tool 方式（同为外部消费方） |
| DD-16 | Dify 处理非 success 状态的交互设计依据 |
