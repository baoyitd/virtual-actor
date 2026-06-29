# 角色产品 → 知识平台 分阶段联调确认与凭据提供

> 版本：v1.0 | 日期：2026-06-17
> 发起方：角色产品（Virtual Actor）
> 接收方：知识平台（Knowledge Workbench）
> 目的：确认分阶段联调方案，提供 Open WebUI 访问凭据以解除适配器开发阻塞
> 前置文档：`handoff-knowledge-execution-deviation-response.zh-CN.md`（知识平台偏离回应）

---

## 一、分阶段联调确认

角色产品接受知识平台提出的分阶段联调方案：

### 阶段1：结构验证（确定性评分器，不切 production 代码）

| 验证项 | 内容 |
|--------|------|
| 端点可达 | `/api/packages`、`/api/packages/{id}/manifest`、`/api/packages/{id}/retrieve`、`/api/packages/{id}/status` 均可达 |
| 请求/响应结构 | 符合 `design-freeze-public-contract-interfaces.zh-CN.md` 冻结定义 |
| 简化模式越界拒答 | retrieve 不传 allowed_tiers 时，Q0 返回 refused:true + refusal_reason + hits:[] |
| version_id 一致 | `/api/packages`、`/api/packages/{id}/status`、`/api/packages/{id}/manifest` 返回一致 version_id |
| 结构化元数据字段 | tier/doc_role/evidence_type/canonical_default/use_for/not_for 字段存在且正确 |

**约束**：阶段1不修改角色产品 production 代码，仅验证接口契约结构。

### 阶段2：质量验证 + 代码切换（Open WebUI 适配器就绪后）

| 验证项 | 内容 |
|--------|------|
| 检索质量 | retrieve 检索质量不低于角色产品当前直连 Open WebUI 的水平 |
| production 代码切换 | `knowledge_platform.py` / `consume_service.py` / 说明卡逻辑切换到 Knowledge Workbench |
| 联调验证 | 角色消费全链路运行态闭环 |
| 质量门禁 | pytest / frontend build / markdownlint / Vale / iteration-guard 全链路通过 |

**触发条件**：知识平台完成 Open WebUI 适配器 + 内部测试通过 + 发出可联调通知。

---

## 二、Open WebUI 访问凭据

知识平台适配器开发的唯一阻塞项是 Open WebUI 认证凭据。角色产品提供当前使用的凭据：

| 配置项 | 值 |
|--------|---|
| Open WebUI 地址 | `http://localhost:3000` |
| 认证邮箱 | `role-acceptance@knowledge.local` |
| 认证密码 | `virtual-actor-service-2026` |
| 默认知识库 ID | `41cee65b-7f9c-4820-ba0d-bb865e0b1e41` |

认证方式：`POST http://localhost:3000/api/v1/auths/signin`，使用 email + password 获取 Bearer token。

当前角色产品代码 `app/services/knowledge_platform.py` 已实现 token 过期自动刷新（401 时用 email/password 重新 signin），知识平台可参考相同机制。

**说明**：

1. 这是知识平台基础设施（Open WebUI）的访问凭据，不是角色产品的应用密钥。
2. JWT token 有过期时间，建议使用 email/password 动态获取 token，不硬编码 JWT。
3. 凭据变更时双方需同步通知。

---

## 三、下一步

| 步骤 | 负责方 | 内容 | 依赖 |
|------|--------|------|------|
| 1 | 知识平台 | 使用凭据访问 Open WebUI，解除适配器开发阻塞 | 本文档凭据 |
| 2 | 知识平台 | 实现 OpenWebUIRetrievalAdapter（6步计划） | 步骤1 |
| 3 | 角色产品 + 知识平台 | 阶段1结构验证（确定性评分器，不切代码） | 可并行启动 |
| 4 | 知识平台 | 适配器内部测试 + pytest 回归 | 步骤2 |
| 5 | 知识平台 | 发出可联调通知（适配器就绪） | 步骤4 |
| 6 | 角色产品 + 知识平台 | 阶段2质量验证 + 代码切换 | 步骤5 |

步骤3可与步骤1-2并行推进。
