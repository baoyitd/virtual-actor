# AI 模型可配置化补充要求（2026-05-28）

> 项目：`virtual-actor`
> 用途：给工作方的补充整改要求，收口 AI 推荐 / AI 创建链路的模型配置问题
> 性质：当前轮次新增要求，不涉及公共契约、跨项目字段或读写边界变更

## 1. 背景

在本轮真实运行态复审中，资产市场 AI 推荐链路存在明显响应时延。继续检查实现后确认：

1. `AI 推荐` 当前在 [app/services/recommend_service.py](/Users/baoyi/Documents/code_buddy/virtual-actor/app/services/recommend_service.py:329) 将模型名硬编码为 `deepseek-v4-pro`
2. `AI 创建草案` 当前在 [app/services/ai_create_service.py](/Users/baoyi/Documents/code_buddy/virtual-actor/app/services/ai_create_service.py:60) 也将模型名硬编码为 `deepseek-v4-pro`
3. 当前只有 `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_PROVIDER` 是配置项；模型名本身不是配置项

这会导致产品在以下方面缺少运营弹性：

1. 无法按链路分别调优时延、质量和成本
2. 一旦需要更换推荐模型或创建模型，必须改代码并重新发布
3. 无法对 `AI 推荐`、`AI 创建` 和 `角色消费/测试` 做清晰分层治理

## 2. 明确要求

本轮补充要求如下：

1. `AI 推荐` 使用的模型必须改为可配置，不能继续硬编码
2. `AI 创建草案` 使用的模型必须改为可配置，不能继续硬编码
3. `角色测试 / consume` 当前已有 `model_binding` 机制，本要求不要求重做这一块

## 3. 边界

本要求的边界如下：

1. 这是角色产品内部实现与运维配置要求，不新增公共 API，不改变公共契约
2. 本轮不强制要求新增后台管理 UI 来改模型；环境变量或服务端配置即可
3. 不强制工作方按某一种具体实现方式落地，但必须满足“模型名不再硬编码”的本质要求

## 4. 建议方案

建议优先采用独立配置项，而不是继续共用一个默认模型常量。建议口径：

1. `AI_RECOMMEND_MODEL`
2. `AI_CREATE_MODEL`
3. 可选补充：
   - `AI_RECOMMEND_TEMPERATURE`
   - `AI_RECOMMEND_MAX_TOKENS`
   - `AI_CREATE_TEMPERATURE`
   - `AI_CREATE_MAX_TOKENS`

说明：

1. `AI 推荐` 和 `AI 创建` 的目标不同，不应默认绑定成同一模型
2. 如果工作方认为存在更优实现方式，可以提出反馈，但不能回退到硬编码

## 5. 交付与验证要求

工作方补齐后，至少需要提交以下证据：

1. 配置入口说明：新增了哪些配置项，默认值策略是什么
2. 代码证据：`AI 推荐` 和 `AI 创建` 不再直接写死模型名
3. 运行态证据：修改配置后，实际发往 LLM 网关的 `model` 字段随配置变化
4. 回归说明：变更后不影响现有 `角色测试 / consume` 路径

最低通过标准：

1. `recommend_service.py` 不再直接写死推荐模型
2. `ai_create_service.py` 不再直接写死创建模型
3. 至少完成一次真实运行态验证，证明配置切换生效

## 6. 给工作方的处理原则

这条要求是明确新增要求，不是建议性观察。

但实现细节上，工作方仍应按以下原则处理：

1. 回归本质评估，不机械照抄建议方案
2. 如果发现会引出新的配置治理问题，可提出更优设计
3. 如果需要扩大到后台可视化配置、租户级配置或角色级策略配置，应先说明，不在本条要求里默认扩展
