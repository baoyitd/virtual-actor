# v0.3.0-commercial-trial 设计增量

> 基线来源：早期 prototype 与角色产品初版 API
> 用途：记录本轮相对原型阶段的增量设计

## 1. 背景与目标

本轮目标是把角色产品从可演示原型推进到内部商业试用产品，解决正式用户入口、真实知识平台集成、发布版本追溯和基础交付部署问题。

## 2. 关键变化

| 设计项 | 决策 | 影响范围 |
|---|---|---|
| DD-01 | React 作为唯一正式验收入口，`prototype/` 仅保留迁移参考 | 前端入口、release notes、测试计划 |
| DD-02 | 知识绑定使用 `knowledge_object_id`，内部补充 `kb_id` 支撑检索 | 知识绑定、角色测试、发布追溯 |
| DD-03 | 已发布版本不可覆写，编辑已发布角色时生成新草稿 | 角色版本、发布、历史查询 |
| DD-04 | 字段说明、模板辅助和知识浏览弹层提升角色配置可用性 | 角色创建、编辑、知识绑定 |
| DD-05 | Docker Compose 作为本轮单机交付形态 | 部署、验收、release notes |

## 3. 数据与状态变化

1. 知识绑定内部持久化 `kb_id`，正式文件级对象标识仍为 `knowledge_object_id`。
2. 测试记录冻结当时 `role_version_id`。
3. 发布时保存最小 `validated_knowledge_versions`：`knowledge_object_id` 与 `knowledge_version_id`。
4. 编辑已发布角色会创建新的 draft version，原 published version 不被覆盖。

## 4. 风险与边界

1. 知识平台 Accepted 仅覆盖当前 handoff 范围，不代表长期冻结依赖。
2. 当前鉴权为内部商业试用基础能力，不覆盖企业级 RBAC。
3. 历史版本详情入口和少量枚举中文映射保留为后续体验优化。
