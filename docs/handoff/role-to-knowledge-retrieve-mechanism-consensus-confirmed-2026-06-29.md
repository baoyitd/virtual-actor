# 角色产品 → 知识平台：retrieve 执行机制共识确认

> 版本：v1.0 | 日期：2026-06-29
> 发起方：角色产品（Virtual Actor）
> 接收方：知识平台（Knowledge Workbench）
> 目的：确认知识平台 06-29 共识确认文档，retrieve 执行机制共识正式生效
> 性质：共识闭合确认
> 前置文档：
> - 共识发起：`role-to-knowledge-retrieve-mechanism-consensus-2026-06-29.md`（角色产品发起）
> - 知识平台确认：`knowledge-to-role-retrieve-mechanism-consensus-confirmation-2026-06-29.md`（知识平台 4 项核查通过 + 裁决 §4 授权依据）
> - 上游裁决：`role-knowledge-interface-adjudication-2026-06-18.md` §4（owner 自主决策事项授权）

---

## 一、确认内容

角色产品确认知识平台 06-29 共识确认文档，无异议。以下事项正式生效：

| 共识事项 | 状态 |
|---|---|
| retrieve 执行机制为混合检索（open_webui 向量检索为主 + deterministic 确定性评分补充 + fallback） | ✅ 双方共识 |
| `execution_engine` 为诊断字段，不纳入公共契约消费必填；后续引擎策略调整不构成 breaking change | ✅ 双方共识 |
| fallback 行为：Open WebUI 不可用时退化为纯确定性，消费方无感知（除非检查 execution_engine） | ✅ 双方共识 |
| 不涉及公共契约字段变更（7 个维度全部"否"） | ✅ 双方共识 |
| 无需上提组合层裁决（基于 06-18 裁决 §4 owner 自主决策事项授权） | ✅ 双方共识 |

---

## 二、裁决 §4 授权依据确认

角色产品核查上游裁决 `role-knowledge-interface-adjudication-2026-06-18.md` 原文：

- 第 22 行："Open WebUI 适配器的实现细节"——明确列入"默认不处理"清单
- 第 23 行："检索引擎选型与调优方案"——明确列入"默认不处理"清单
- 第 183 行：Open WebUI 适配器是否就绪及检索质量——列为验证项（交付前需说明），非裁决冻结项

角色产品确认：混合检索方案属于知识平台在裁决 §4 授权范围内的执行方案选择，不构成对裁决的偏离，无需上提组合层裁决。

---

## 三、追溯说明

如 lead 后续对 retrieve 执行机制提出异议或要求重新裁决，角色产品同意配合补流程。本共识文档作为执行方案选择的归档依据保留。

---

## 四、角色产品侧后续动作

| 动作 | 状态 |
|---|---|
| v0.5.1 dossier 中 retrieve 执行机制表述更新为"混合检索（已共识确认）" | 本次完成 |
| portfolio-sync.md 更新 retrieve 执行机制共识状态 | 本次完成 |

---

## 五、共识闭合

**retrieve 执行机制共识正式闭合。** 本共识文档为闭合依据。

双方无待办。如后续需要调整 retrieve 执行机制，按"先反馈再执行"原则重新发起共识。
