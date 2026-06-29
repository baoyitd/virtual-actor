# v0.4.0 DD-10 AI 协作创建流程扩展规格

> 版本：v0.4.0 | 日期：2026-05-26 | Formal Status：Draft
> 类型：产品功能扩展规格
> 规划方裁决依据：planning-response 3.1 批准 DD-10 扩展至包含 output_type 和 applicable_scenarios 推荐
> 前置依赖：business-output-templates-and-status-rules.md、version-snapshot-update-and-migration.md

---

## 1. DD-10 原定义与扩展内容

### 1.1 原定义

DD-10（AI 协作创建）原范围：AI 生成角色名称、bio、边界声明（knowledge_boundary / capability_boundary）、治理属性（category / owner / business_domain / visibility）。

### 1.2 扩展内容

规划方裁决批准扩展，新增：

1. AI 推荐 `output_type`（4 模板枚举之一）
2. AI 生成 `applicable_scenarios`（适用场景描述）
3. AI 基于 output_type 推荐生成 `output_schema` 默认结构

扩展理由：

- 否则 AI 创建只生成角色基础信息，用户仍需手工补 output_type 和适用场景，AI 原生体验断裂
- output_type 是 DD-11/DD-12 的前置
- applicable_scenarios 是 DD-13 AI 推荐的前置

---

## 2. AI 草案生成范围

### 2.1 生成字段清单

| 字段 | AI 行为 | 用户可编辑 | 保存逻辑 | 来源依据 |
|---|---|---|---|---|
| name | AI 生成 | 可编辑 | 保存为草案 L1_IDENTITY | 角色意图推导 |
| bio | AI 生成 | 可编辑 | 保存为草案 L1_IDENTITY | 角色意图推导 |
| knowledge_boundary | AI 生成 | 可编辑 | 保存为草案 L3_KNOWLEDGE | 角色意图 + 业务域推导 |
| capability_boundary | AI 生成 | 可编辑 | 保存为草案 L4_CAPABILITY | 角色意图 + output_type 推导 |
| capability_level | AI 推断 | 可编辑（下拉选择） | 保存为草案 L4_CAPABILITY | 默认 A1；如意图含执行动作则推荐 A2/A3 |
| applicable_scenarios | AI 生成 | 可编辑（自由文本或结构化） | 保存为草案 L1_IDENTITY | 角色意图 + 业务域推导 |
| output_type | AI 推荐 | 可编辑（下拉选择） | 保存为草案 L5_CONFIG | 角色意图关键词匹配（见规则表） |
| output_schema | AI 生成（基于 output_type 模板默认） | 可编辑（v0.4 仅模板选择，v0.4.x 支持自定义字段追加） | 保存为草案 L5_CONFIG | 按 output_type 对应模板自动填充 |
| category | AI 推荐 | 可编辑（下拉选择） | 保存为 RoleAsset 资产级属性 | 角色意图推导 |
| business_domain | AI 推荐 | 可编辑（下拉选择） | 保存为 RoleAsset 资产级属性 | 角色意图推导 |
| tags | AI 生成 | 可编辑 | 保存为草案 L1_IDENTITY | 角色意图关键词提取 |

### 2.2 AI 生成逻辑

#### output_type 推荐规则

| 角色意图关键词 | 推荐 output_type | 推荐 capability_level |
|---|---|---|
| 决策 / 判断 / 建议 / 评估 / 方案选择 | decision_advice | A1 |
| 风险 / 合规 / 分析 / 审查 / 识别 | risk_analysis | A1 |
| 制度 / 规定 / 流程 / 解释 / 政策 / 规范 | policy_explanation | A1 |
| 审查 / 审核 / 评审 / 检查 / 检验 / 审计 | review_findings | A1 |
| 执行 / 操作 / 动作 / 流程执行 / 自动化 | 不推荐（v0.4 无 A3 角色；提示用户该意图超出 v0.4 范围） | A3（v0.4 不支持） |

注：capability_level 默认为 A1（最安全层级），除非意图明确要求执行动作才推断 A2/A3。v0.4 MVP 角色均为 A1 层级（问答建议）。

#### applicable_scenarios 生成规则

AI 基于角色意图和 output_type 生成 applicable_scenarios，格式为自然语言描述，例如：

- decision_advice 角色："适合重大事项决策前的立场判断和风险评估场景，如项目立项、投资决策、组织调整等需要多维度依据支持的决策事项"
- risk_analysis 角色："适合合同、方案、项目的风险识别和等级评估场景，如经营风险分析、合同条款审查、项目风险排查等"
- policy_explanation 角色："适合制度条文解释和合规指导场景，如员工咨询制度适用范围、操作流程合规性判断等"
- review_findings 角色："适合各类专业审查和问题清单场景，如合同审查、技术方案评审、项目文档审查等"

#### output_schema 生成规则

AI 基于 output_type 自动填充对应模板的默认字段结构（参见 business-output-templates-and-status-rules.md 1.2~1.5 各模板字段定义）。v0.4 不支持自定义字段追加。

### 2.3 默认值与失败回退

| 场景 | 处理 |
|---|---|
| AI 无法识别角色意图 | output_type 留空，提示用户手动选择；applicable_scenarios 留空 |
| AI 推荐的 output_type 与用户预期不符 | 用户可在草案编辑界面修改 |
| AI 生成 applicable_scenarios 内容过于宽泛 | 用户可编辑精化；编辑后保存 |
| AI 调用失败（LLM 服务异常） | 生成只包含 name（由用户输入的意图关键词衍生）和 bio（基于意图简述），其余字段留空；提示"AI 生成部分失败，请手动补充" |
| 用户在意图输入中明确指定 output_type | AI 优先采用用户指定值，不再自动推断 |

---

## 3. 用户可编辑范围

### 3.1 完全可编辑字段

以下字段 AI 生成后用户可完全修改：

1. name：自由文本编辑
2. bio：自由文本编辑
3. knowledge_boundary：自由文本编辑
4. capability_boundary：自由文本编辑
5. applicable_scenarios：自由文本编辑

### 3.2 选择型可编辑字段

以下字段 AI 推荐/推断后用户通过下拉选择修改：

1. output_type：下拉选择 4 模板枚举之一
2. capability_level：下拉选择 A1 / A2 / A3
3. category：下拉选择预定义分类
4. business_domain：下拉选择预定义业务域

### 3.3 联动逻辑

| 用户操作 | 联动影响 |
|---|---|
| 修改 output_type | output_schema 自动切换为新模板的默认结构；capability_boundary 可能需同步调整（如从"建议型"调整为"审查型"） |
| 修改 capability_level | capability_boundary 需同步调整（如从 A1 问答调整为 A2 生成型边界） |
| 修改 applicable_scenarios | 无联动——独立字段 |

---

## 4. 保存逻辑

### 4.1 草案保存

用户确认/编辑后保存为 draft：

1. AI 生成和用户编辑的字段全部保存到 RoleAsset 和 RoleVersion（draft 状态）
2. creation_source 自动标记为 ai_assisted
3. output_type / output_schema / capability_level / applicable_scenarios 进入版本快照（RoleVersionField EAV）
4. category / business_domain / visibility 等治理属性保存到 RoleAsset 资产级属性

### 4.2 版本快照影响

新增字段（output_type / output_schema / capability_level / applicable_scenarios）进入版本快照后：

1. 已保存的草案版本包含这些字段
2. 后续编辑修改这些字段会产生新版本快照
3. 已 published 版本的这些字段不可直接覆写

---

## 5. AI 创建流程交互设计要点（UI 原型细节另见线框图文档）

### 5.1 流程步骤

```text
Step 1: 用户输入角色意图（自然语言描述）
        → AI 解析意图

Step 2: AI 展示角色草案（所有生成字段）
        → 用户逐项查看和编辑

Step 3: 用户确认草案
        → 保存为 draft + creation_source = ai_assisted
```

### 5.2 Step 2 草案展示布局

草案展示应分组呈现：

1. **角色基础信息**：name / bio / applicable_scenarios
2. **角色边界声明**：knowledge_boundary / capability_boundary / capability_level
3. **业务输出配置**：output_type / output_schema（按模板字段列表展示）
4. **治理属性**：category / business_domain / visibility

每组标注"AI 生成"或"AI 推荐"，用户可逐项编辑。

### 5.3 output_schema 展示方式

output_schema 不展示为原始 JSON，而是：

1. 按 output_type 对应模板的字段列表逐项展示
2. 每项显示：字段中文名称、业务含义、是否必填、示例值
3. v0.4 不支持自定义字段追加——字段列表为模板固定字段
4. v0.4.x 补"自定义字段"入口

---

## 6. 与 DD 项的支撑关系

| DD 项 | DD-10 扩展支撑点 |
|---|---|
| DD-11 | AI 推荐 output_type 为结构化输出的前置 |
| DD-12 | AI 推荐 output_schema 为配置体验的前置 |
| DD-13 | AI 生成 applicable_scenarios 为资产市场推荐的前置 |
| DD-05 | AI 推断 capability_level 为能力层级标注的前置 |
| DD-09 | creation_source = ai_assisted 为运营看板 AI 草案接受率统计的前置 |
