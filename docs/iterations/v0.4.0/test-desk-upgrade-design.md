# v0.4.0 测试台升级设计

> 版本：v0.4.0 | 日期：2026-05-26 | Formal Status：Draft
> 类型：产品功能升级设计
> 前置依赖：consume-api-design.md、business-output-templates-and-status-rules.md、version-snapshot-update-and-migration.md

---

## 1. 定位与边界

v0.3 测试台只验证角色自然语言回答质量。v0.4 测试台是 consume API 的**第一个内部消费方**，必须能验证：

1. 结构化输出是否符合 output_type 对应的 Schema
2. 6 消费状态判定是否正确
3. boundary_status 命中是否合理
4. 固定治理外壳各字段是否完整

测试台升级不是新增独立页面，而是改造现有使用台（/roles/:id/use）使其成为 consume API 的前端消费方，同时增强测试结果展示和验证能力。

---

## 2. 测试台与使用台的关系

### 2.1 测试台与 consume API 的关系

测试台**不直接调用** consume API 消费 test 版本角色。consume API 的定位是三类已发布角色消费入口，只允许 published 版本。

测试台的验证方式：复用同一套结构化输出、6 状态和 boundary_status 的校验逻辑，但走独立的测试验证通道：

1. 测试台调用 `POST /role-assets/{role_id}/test-consume`（内部测试验证接口，非正式消费 API）
2. test-consume 接口接受 test 状态版本，复用 consume API 的全部输出结构（固定治理外壳 + structured_result + status + boundary_status）
3. test-consume 不生成正式 usage_record，生成 test_validation_record（与 test_runs 共存但字段对齐 consume API 输出结构）
4. test-consume 接口是角色产品内部接口，不纳入公共契约边界

这样保证了：

1. consume API 的状态语义清晰：只消费 published 版本，生成正式 usage_record
2. 测试台能完整验证结构化输出、6 状态、boundary_status 的正确性
3. usage_records 和 test_runs 边界不被打乱
4. 校验逻辑复用，实现成本可控

### 2.2 区分

| 维度 | 测试台 | 使用台 |
|---|---|---|
| 角色状态要求 | test | published |
| 调用路径 | POST /role-assets/{role_id}/test-consume (role_version_id 指向 test 版本) | POST /role-assets/{role_id}/consume (默认当前 published 版本) |
| caller_type | human（测试验证，不生成正式 usage_record） | human / agent_platform / decision_product / system |
| 输出展示 | 增强验证模式（显示 Schema 合规性、状态判定理由、boundary 命中分析） | 正式消费模式（面向用户的简洁展示） |
| 评分 | 1-5 星 | v0.4 不实现评分 |
| 目的 | 验证角色质量是否达到发布标准 | 正式使用角色获取专业建议 |

---

## 3. 测试台升级功能清单

### 3.1 P0 功能（v0.4 必交）

#### 3.1.1 结构化输出验证

测试台消费角色后，必须展示并校验 structured_result：

1. **展示**：按 output_type 对应模板的字段列表展示 structured_result，每个字段独立展示（而非纯 JSON dump）。
2. **合规校验**：
   - 检查必填字段是否存在且类型正确
   - 检查枚举值是否合法（severity level、risk level 等）
   - 检查 references 是否非空（所有模板的 references 为必填）
3. **校验结果标注**：每个字段标注合规状态（通过 / 缺失 / 类型错误 / 值不合法）
4. **整体合规判断**：所有必填字段通过 = 合规；任一必填字段缺失或不合法 = 不合规

#### 3.1.2 消费状态判定展示

测试台必须展示 status 和 status_reason，并提供判定分析：

1. 展示 status 枚举值和中文名称
2. 展示 status_reason 原文
3. 展示 boundary_status 两个维度的枚举值和中文名称
4. 标注 boundary_status 与 status 的联动是否一致（后端校验规则的客户端镜像）

#### 3.1.3 boundary_status 命中分析

测试台必须提供 boundary 命中分析面板：

1. 展示角色声明的 knowledge_boundary 内容
2. 展示角色声明的 capability_boundary 内容
3. 展示角色声明的 capability_level
4. 将消费结果的 boundary_status 与角色声明的 boundary 对比
5. 标注命中是否合理（如 boundary_blocked 时是否确实触发了 boundary 声明中的越界规则）

#### 3.1.4 固定治理外壳完整性检查

测试台必须检查消费输出的固定治理外壳字段：

| 字段 | 检查 |
|---|---|
| answer | 非空 |
| role_id | 与请求的角色 ID 一致 |
| role_version_id | 与请求的版本 ID 一致（或为系统自动选择的当前版本） |
| validation_record_id | 非空，格式为 UUID；test-consume 生成 test_validation_record，此字段指向该记录 ID |
| created_at | ISO 8601 格式 |
| sources | 数组类型（允许空数组） |
| boundary_status | 符合复合结构（knowledge_boundary + capability_boundary 各为合法枚举值） |
| output_type | 非空（v0.4 角色必填）或 null（v0.3 legacy 角色 fallback） |
| structured_result | 对象类型（允许空对象） |
| status | 6 状态合法枚举值 |
| status_reason | 非空 |

#### 3.1.5 测试结果记录

每次测试台消费自动生成一条 test_validation_record（不写入 usage_records 表），记录：

1. caller_type = human
2. caller_id = 测试人员 ID
3. role_version_id = 被测试的 test 版本
4. query / context / answer / structured_result / status / status_reason / boundary_status / sources

test_validation_record 与 usage_records 完全区分：不同数据表、不同 API、不同查询入口。测试台页面展示的记录 ID 为 validation_record_id，不使用 usage_record_id 语义。

测试结果可与 v0.3 评分系统并存：先展示消费结果验证面板，再展示评分入口。

### 3.2 P1 功能（v0.4.x 增强）

1. 测试问题 AI 生成建议（基于角色 knowledge_boundary 和 capability_boundary 自动生成测试问题）
2. 测试失败原因 AI 分析
3. 测试报告导出
4. 批量测试运行

---

## 4. 测试台页面信息架构

### 4.1 页面分区

```
┌─────────────────────────────────────────────────┐
│ 测试台 / Test Console                             │
├─────────────────────────────────────────────────┤
│ [角色名称] [版本号] [状态: test]                   │
│ [capability_level: A1] [output_type: risk_analysis] │
├─────────────────────────────────────────────────┤
│ 输入区                                            │
│ ┌──────────────────────┐ ┌──────────────────┐   │
│ │ query (必填)          │ │ context (可选)    │   │
│ │ [文本输入框]          │ │ [文本输入框]      │   │
│ └──────────────────────┘ └──────────────────┘   │
│ [消费测试] 按钮                                    │
├─────────────────────────────────────────────────┤
│ 输出区                                            │
│ ┌── 治理外壳 ──────────────────────────────┐    │
│ │ status: [状态枚举] + 中文名               │    │
│ │ status_reason: [原因说明]                │    │
│ │ answer: [自然语言回答]                    │    │
│ │ role_version_id / validation_record_id       │    │
│ │ created_at / sources                     │    │
│ └──────────────────────────────────────────┘    │
│ ┌── boundary 命中分析 ─────────────────────┐    │
│ │ knowledge_boundary: [枚举] + 声明内容对比 │    │
│ │ capability_boundary: [枚举] + 声明内容对比 │    │
│ │ 联动校验: [一致/不一致]                   │    │
│ └──────────────────────────────────────────┘    │
│ ┌── structured_result ─────────────────────┐    │
│ │ [按模板字段逐项展示]                      │    │
│ │ 每字段标注: ✅合规 / ❌缺失 / ⚠️类型错误  │    │
│ │ 整体合规: [合规/不合规]                   │    │
│ └──────────────────────────────────────────┘    │
│ ┌── 评分 ──────────────────────────────────┐    │
│ │ [1-5 星评分] (v0.3 保留)                  │    │
│ └──────────────────────────────────────────┘    │
├─────────────────────────────────────────────────┤
│ 测试历史                                          │
│ [测试记录列表，每条含 query/status/评分/时间]      │
└─────────────────────────────────────────────────┘
```

### 4.2 状态标注设计

测试台的输出展示区使用以下标注：

| 标注 | 含义 | 颜色建议 |
|---|---|---|
| ✅ 合规 | 字段存在且类型/值合法 | 绿色 |
| ❌ 缺失 | 必填字段不存在 | 红色 |
| ⚠️ 类型错误 | 字段存在但类型不匹配 | 橙色 |
| ⚠️ 值不合法 | 字段存在但枚举值不合法 | 橙色 |
| 🔄 联动一致 | boundary_status 与 status 联动规则一致 | 绿色 |
| ❌ 联动不一致 | boundary_status 与 status 联动规则不一致 | 红色 |

### 4.3 空/错误/加载状态

| 状态 | 展示 |
|---|---|
| 空状态（未执行测试） | 输入区可见，输出区显示"请输入查询并点击消费测试" |
| 加载状态（测试进行中） | 输入区 disabled，输出区显示加载动画 + "角色正在响应..." |
| system_failed | 输出区展示 status = system_failed，boundary_status 两维度 not_applicable，无 structured_result |
| boundary_blocked | 输出区展示 status = boundary_blocked，boundary 命中分析面板高亮越界维度 |

---

## 5. 与 consume API 的技术关系

### 5.1 前端调用方式

测试台前端调用内部测试验证接口（而非正式 consume API）：

```
POST /role-assets/{role_id}/test-consume
{
  "role_version_id": "test版本UUID",
  "query": "测试人员输入的查询",
  "context": "测试人员可选的上下文",
  "output_type": null,  // 使用角色版本配置的默认 output_type
  "caller_type": "human",
  "caller_id": "当前登录用户ID"
}
```

输出结构沿用 consume API 固定治理外壳的字段布局，但做以下字段名适配：

1. `usage_record_id` 替换为 `validation_record_id`（指向 test_validation_record，避免 usage_record 语义污染）
2. 其余字段（answer / role_id / role_version_id / created_at / sources / boundary_status / output_type / structured_result / status / status_reason）含义和格式与 consume API 完全一致

test-consume 生成 test_validation_record 而非正式 usage_record。test_validation_record 不写入 usage_records 表，不出现在 consume-records 查询结果中。

### 5.2 前端校验 vs 后端校验

前端展示的合规校验是**辅助分析工具**，不替代后端校验。后端 consume API 负责输出完整性；前端测试台负责可视化和人可读的验证报告。

### 5.3 测试台作为 consume API 的验证方

测试台验证 consume API 的输出质量，属于"内部消费方"角色。如果测试台无法正确展示和校验消费输出，则 consume API 的"测试发布"环节不可走通。

---

## 6. 与 DD 项的支撑关系

| DD 项 | 测试台升级支撑点 |
|---|---|
| DD-03 | 使用台升级为 consume API 前端消费方 |
| DD-11 | structured_result Schema 合规校验 |
| DD-16 | 6 状态展示 + boundary_status 命中分析 |
| DD-05 | capability_level 展示 + boundary_blocked 判定依据 |
| DD-02 | boundary 声明与 boundary_status 命中对比分析 |
