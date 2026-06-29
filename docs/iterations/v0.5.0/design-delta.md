# v0.5.0 设计增量

> 基线来源：`v0.4.0` 已有产品与实现基线
> 用途：只记录本轮相对 `v0.4` 的设计增量，不重复抄写全量实现
> 前置文档：`requirements-analysis.md`、`requirements-checklist.md`、`scope.md`
> 当前状态：已按 `2026-06-10` 最新需求共识完成设计回写；`Design Freeze Status = Effective`，代表环境验证与运行效果证据已闭合，`Formal Status = Self-Tested`

---

## 1. 设计目标

`v0.5` 不是新开一条产品线，而是在 `v0.4` 既有角色资产底座上做三件事：

1. 让角色更像现实世界里的**数字职责资产**
2. 让角色更容易被**理解、创建、补齐和发布**
3. 让合适的已发布角色版本能被外部 AI 环境**稳定复用**

因此，本轮设计主线固定为：

```text
角色定义层（L1-L4）
  -> 消费契约层
  -> 资产治理层
  -> 稳定外部供给载体
  -> 外部消费与追溯闭环
```

---

## 2. 固定设计原则

1. 不新增独立 `RoleAssetDefinitionPackage` 对象。
2. 平台核心承载体仍然是 `RoleAsset + RoleVersion + RoleVersionField`。
3. `L1-L4` 是角色定义层唯一主骨架；流程步骤文案不能替代 `L1-L4`。
4. 消费契约层回答“怎么用、为什么可信”，不混进角色定义页主叙事。
5. 资产治理层回答“如何管理、发布、外供和追溯”，不反向定义角色能力。
6. 旧的 `capability_boundary / capability_level / collaboration_mode` 默认移出当前正文，不再主导 `L3`。
7. 任何字段是否保留，只看它是否对真实运行、真实理解或真实治理有作用，不因历史而默认保留。
8. AI 起草与人工编辑必须落在同一套角色理解模型中，不能形成两条产品线。
9. 知识绑定、数据能力绑定都允许为空；空状态必须被明确表达，不能暗示成异常。
10. `L4` 默认合法路径是 `freeform`；只有选择 `structured` 时，结构化模板和扩展字段才进入主路径。
11. 对外供给建立在现有 `consume API` 之上，不另造平行运行平面。
12. 本轮的交互重设计目标是**降低理解成本和操作门槛**，不是视觉换肤。

---

## 3. DD-17 角色定义层重构

### 3.1 角色定义层总结构

本轮角色定义层固定为：

| 层级 | 本轮主题 | 核心问题 |
| --- | --- | --- |
| `L1` | 身份与判断 | 这个角色是谁，最核心负责什么，默认从什么视角看问题 |
| `L2` | 知识依据 | 它是否绑定真实知识；若绑定，知识边界到哪里 |
| `L3` | 数据能力（可选） | 它是否被授权读取结构化业务数据；若授权，绑定哪些数据资产 |
| `L4` | 输出方式与运行配置 | 它默认自由输出还是结构化输出；如结构化，模板和扩展是什么 |

固定口径：

1. 原 `L2` 判断方式字段并入新的 `L1`。
2. 原 `source_physical_role` 转为治理侧的 `enterprise_role_mapping`。
3. 原独立 `responsibility_boundary` 移出本轮输入。
4. 旧 `capability_*` 与 `collaboration_mode` 默认移出正文，不再作为角色成立前提。

### 3.2 新 `L1`：身份与判断

#### 字段归属

| 字段 | 本轮定位 | 页面位置 | 是否硬门禁 |
| --- | --- | --- | --- |
| `name` | 角色识别名 | `L1` 主路径 | 否 |
| `bio` | 一句话摘要 | `L1` 主路径 | 否 |
| `main_duty_cluster` | 角色核心职责锚点，用户侧显示为 `核心职责` | `L1` 主路径 | 是 |
| `point_of_view` | 默认分析视角 | `L1` 主路径 | 否，推荐完整 |
| `decision_style` | 结论形成风格 | `L1` 高级项 | 否 |
| `identity_background` | 判断背景与专业来源 | `L1` 高级项 | 否 |
| `speaking_style` | 表达方式与语气 | `L1` 高级项 | 否 |

#### 交互设计规则

1. 首次创建时，用户主路径先只面对：
   - `name`
   - `bio`
   - `main_duty_cluster`
   - `point_of_view`
2. `decision_style / identity_background / speaking_style` 统一收进高级 / 补充项。
3. 所有文本型字段模板句式优先直接写进 `placeholder`。
4. 下方辅助说明只解释作用与边界，不再承担主模板内容。

#### 模板句式

| 字段 | `placeholder` 模板句式 |
| --- | --- |
| `bio` | `面向【对象/场景】，提供【结果/价值】。` |
| `main_duty_cluster` | `围绕【对象/场景】，负责【动作1】、【动作2】，并输出【结果1】与【结果2】。` |
| `point_of_view` | `优先从【维度1】、【维度2】看问题，重点关注【关键矛盾/指标】。` |
| `identity_background` | `具备【经验/专业背景】，擅长从【维度】判断问题。` |
| `speaking_style` | `先【顺序1】，再【顺序2】，使用【语气/风格】表达。` |

### 3.3 新 `L2`：知识依据

#### 字段归属

| 字段 | 本轮定位 | 页面位置 | 是否硬门禁 |
| --- | --- | --- | --- |
| `knowledge_refs` | 真实知识绑定对象 | `L2` 主路径 | 否 |
| `knowledge_boundary` | 知识覆盖范围声明 | `L2` 主路径，但仅在有知识绑定时可编辑 | 否 |
| `validated_knowledge_versions` | 发布后的最小追溯结构 | 只读弱展示 | 否 |

#### 交互设计规则

1. `L2` 必须同时支持两条合法路径：
   - 暂不绑定真实知识
   - 选择知识后再确认知识边界
2. 无知识绑定时：
   - 系统明确展示 `当前未绑定真实知识`
   - `knowledge_boundary` 不要求用户手写
3. 有知识绑定时：
   - 保留真实知识绑定入口
   - `knowledge_boundary` 优先根据已绑定知识生成可编辑初稿
4. 当前检索仍按知识库 collection 执行；文件级绑定主要用于展示、追溯和知识范围声明，不得误表述为严格文件级检索约束。

#### 模板句式

| 字段 | `placeholder` 模板句式 |
| --- | --- |
| `knowledge_boundary` | `基于【知识来源】回答，暂不覆盖【不覆盖范围】。` |

### 3.4 新 `L3`：数据能力（可选）

`L3` 本轮不再写说明性能力文案，只保留**版本级数据能力绑定**。

#### 字段归属

| 字段 | 本轮定位 | 页面位置 | 是否硬门禁 |
| --- | --- | --- | --- |
| `data_asset_bindings` | 当前角色版本被授权读取的结构化业务数据资产项 | `L3` 主路径 | 否 |

#### 角色页设计规则

1. `L3` 标题固定为 `数据能力（可选）`。
2. 角色页只允许：
   - 打开选择器
   - 选择 `0~多条` 数据资产项
   - 查看已绑定摘要
   - 查看空状态
3. 角色页不再提供自由文本输入，避免“写文案冒充能力授权”。
4. 未绑定时必须明确显示：`当前未授权结构化业务数据`。
5. 已绑定时展示：
   - `display_name`
   - `scope_summary`
   - 技术细节只在管理员页查看，不进入角色定义主路径

#### 管理员侧数据资产管理页

平台管理员需要独立页面维护可绑定的数据资产项；角色页只做选择，不做现场创建。

| 字段 | 类型 | 要求 |
| --- | --- | --- |
| `display_name` | String | 必填 |
| `datasource_ref` | String | 必填 |
| `database_name` | String | 必填 |
| `table_name` | String | 必填 |
| `scope_summary` | Text | 必填 |
| `freshness` | String | 可选 |
| `owner_team` | String | 可选 |
| `status` | Enum | 系统字段 |
| `created_at / updated_at` | Datetime | 系统字段 |

固定口径：

1. 当前只考虑数据库 / 表级结构化业务数据资产。
2. 当前只表达**只读**的数据能力，不承载写入、修改或执行动作。
3. 当前不做版本快照；运行时依赖当前生效的数据资产配置。
4. 平台内测试、正式消费和外平台复用，都通过平台服务端查询层让数据能力真实生效，不暴露数据库连接到角色页或外部平台。

#### 模板句式

| 字段 | `placeholder` 模板句式 |
| --- | --- |
| `data_asset.scope_summary` | `可读取【业务对象/指标】，粒度到【组织/周期】；不包含【明显不含范围】。` |

### 3.5 新 `L4`：输出方式与运行配置

#### 字段归属

| 字段 | 本轮定位 | 页面位置 | 是否硬门禁 |
| --- | --- | --- | --- |
| `output_mode` | 输出方式总开关：`freeform / structured` | `L4` 主路径 | 否，但试用前应明确 |
| `output_type` | 平台预置结构化模板类型 | 仅在 `structured` 路径下进入主路径 | 条件硬门禁 |
| `output_schema` | 基于模板的角色级业务字段扩展 | 仅在 `structured` 路径下进入主路径 | 条件硬门禁 |
| `model_binding` | 运行模型覆盖项 | `L4` 高级配置 | 否 |

#### 交互设计规则

1. `L4` 先让用户选择：
   - `自由输出`
   - `结构化输出`
2. 默认值为 `freeform`。
3. 只有选择 `structured` 后，才出现：
   - `output_type`
   - `output_schema`
4. `output_type` 用业务语言卡片表达，不让用户直接面对技术字段。
5. `output_schema` 必须基于平台模板自动带出，并只允许追加业务字段。
6. 角色级扩展不允许删除或改坏平台模板核心字段。
7. `model_binding` 默认继承系统值，并折叠在高级设置中。
8. `temperature / max_tokens / fallback_enabled` 等运行参数不占据角色定义首屏。

固定口径：

1. `freeform` 是合法默认路径，不等于“角色不完整”。
2. 只有走 `structured` 的角色，`output_type / output_schema` 才成为必须完整的消费契约。
3. AI 草案应继续能够产出：
   - `output_mode` 建议
   - 若建议结构化输出，则一并产出 `output_type + output_schema` 初稿

---

## 4. DD-18 消费契约层（页面外显：使用前说明与调用预览）

消费契约层回答的是：

```text
别人怎么正确使用这个角色？
为什么可以信它？
```

### 字段归属

| 字段 | 本轮定位 | 是否硬门禁 |
| --- | --- | --- |
| `applicable_scenarios` | 角色适合被调用的业务阶段 / 任务 | 是 |
| `usage_notes` | 角色怎么被正确使用、输入前提是什么 | 是 |
| `support_basis_summary` | 角色靠什么成立、已有何种证据 | 是 |

### 页面表达

页面外显固定为 `使用前说明与调用预览`，并以系统生成说明卡为主，而不是第二个重表单页。

固定分成 5 个模块：

1. 头部摘要（只读）
   - 角色名、版本、状态、输出方式、知识状态、数据能力状态、最近验证状态
2. 这个角色适合干什么
   - `bio / main_duty_cluster` 只读引用自角色定义层
   - `applicable_scenarios` 默认自动生成，仅允许轻量修订
3. 怎么正确使用
   - `usage_notes` 由系统预生成整段说明，人工微调
   - 不再拆出独立 `调用前提提示` 字段
4. 你将得到什么
   - 只读输出预览
   - `freeform` 显示结果风格说明
   - `structured` 显示模板骨架 / 关键字段预览
5. 为什么可信 / 当前限制
   - `support_basis_summary` 由系统生成主体，人工补充一句业务说明
   - 首屏展示知识 / 数据 / 验证摘要，并支持展开详情
   - 只表达事实状态，不承担 `待补齐 / 不可发布 / 不合格` 门禁裁决

### 模板句式

| 字段 | `placeholder` 模板句式 |
| --- | --- |
| `applicable_scenarios` | `输入【业务阶段/任务】` |
| `usage_notes` | `系统预生成：面向【使用者】，在【输入前提】下输入【输入】，获得【输出】。` |
| `support_basis_summary` | `系统先拼接知识/数据/测试依据；人工补充【业务依据/限制】。` |

固定口径：

1. 消费契约不替代 `L1-L4`，但会被发布门禁、使用前前置卡和外供包引用。
2. 知识状态和数据能力状态都要在消费契约侧如实表达：
   - 知识未绑定：明确展示未绑定真实知识
   - 数据能力未授权：明确展示当前未授权结构化业务数据
3. `applicable_scenarios` 会影响选择、推荐与发布门禁，但当前不直接控制 `consume` 运行时行为。
4. `support_basis_summary` 保留字段名，但交互上不再作为完全空白人工录入区。
5. 说明卡以**当前保存版**为唯一生效文本：
   - 使用前前置卡读取当前保存版
   - 发布 / 外供门禁检查当前保存版
   - 外供包在生成时读取当前保存版
6. 当以下来源变化后，系统不得静默覆盖当前保存版，而应把说明卡标记为`待确认更新`：
   - `L1-L4`
   - 知识状态 / 知识边界
   - 数据能力状态 / 绑定摘要
   - 最近验证摘要
7. `待确认更新` 不是新的版本状态；用户可根据最新角色信息重生成说明卡并确认替换，也可沿用当前文本并重新保存。
8. 说明卡处于`待确认更新`时，不得进入正式发布 / 外供。

---

## 5. DD-19 AI 协作创建升级

### 固定主链路

```text
自然语言输入
  -> 结构化角色草案
  -> 人确认 / 编辑
  -> 保存 draft
  -> 保存当前说明卡
  -> 进入 test
```

### AI 草案最低覆盖

AI 草案应优先生成：

1. `name`
2. `bio`
3. `main_duty_cluster`
4. `point_of_view`
5. `decision_style`
6. `identity_background`
7. `speaking_style`
8. `applicable_scenarios`
9. `usage_notes`
10. `support_basis_summary`
11. `knowledge_boundary` 草案
12. `output_mode` 建议
13. 若建议结构化输出，则一并生成 `output_type / output_schema` 初稿

### AI 不直接决定的内容

AI 不负责直接确定：

1. 实际 `knowledge_refs`
2. 实际 `data_asset_bindings`
3. `model_binding` 的运行时覆盖值
4. `owner / maintainer / visibility / enterprise_role_mapping / publish / export`
5. 测试证据与发布结论

固定口径：

1. AI 入口仍是“一段描述 -> 结构化草案”，不是零散字段建议集合。
2. AI 只负责降低起步门槛，不替代用户理解和确认。
3. AI 草案与人工编辑必须进入同一工作区骨架。

---

## 6. DD-20 创建 / 编辑交互重设计

### 6.1 两类用户侧

交互上固定两类用户侧：

| 用户侧 | 负责内容 |
| --- | --- |
| 角色能力侧 | `L1-L4` 角色定义 + 消费契约 |
| 资产治理侧 | 治理字段、测试证据、发布门禁、数据资产管理、外供与追溯 |

### 6.2 页面结构

| 页面 | 归属 | 设计意图 |
| --- | --- | --- |
| 角色定义工作台 | 角色能力侧 | 只回答“这个角色由什么组成” |
| 使用前说明与调用预览 | 角色能力侧 | 以系统生成说明卡回答“怎么用、为什么可信” |
| 试用与测试 | 角色能力侧 / 验证桥接 | 只对 `test` 角色做内部验证，先确认当前版本是否能工作 |
| 治理与发布 | 资产治理侧 | 管治理字段、发布门禁，以及版本级 `publish / archive` 动作 |
| 正式消费 | 消费侧 | 面向已发布版本的正式使用入口 |
| 数据资产管理 | 资产治理侧 / 管理员 | 管理可被选择的数据资产项 |
| 外供与追溯 | 外部复用侧 | 管单个已发布版本的对外供给与回写 |

### 6.3 交互约束

1. 角色定义页必须首先回到 `L1-L4`，不能再以步骤流程代替。
2. 首次创建时，不要求一次性补齐治理项。
3. 用户始终能看见当前处于哪一侧、缺口在定义侧还是治理侧。
4. 高影响字段留在主路径；低频字段收进高级项或独立页面。
5. 角色页保留知识绑定操作，不退化成只读摘要。
6. `L3` 用选择与摘要表达数据能力，不再靠自由文本描述。
7. `L4` 先选输出方式，再展开结构化路径和高级配置。
8. `治理与发布` 主路径只放 `owner / business_domain / category`。
9. `visibility / maintainer / tags / enterprise_role_mapping` 作为补充治理项保留，其中 `visibility` 不按 ACL 语义描述。
10. `owner / business_domain / category` 不是纯展示字段：
    - 内部试用阶段：允许后补，不作为前置阻断
    - 进入“可供他人消费”前：三项全部为硬要求
    - 正式发布 / 外供前：三项全部进入现有门禁硬校验
11. 全局一级导航按 `资产市场 -> 角色资产 -> 运营看板 -> 数据资产管理` 排列，优先服务消费主场景。
12. `新建角色` 是 `角色资产` 页内动作入口，不作为一级导航项，避免把页面域和单次动作并列。
13. `运营看板` 先呈现当前待处理缺口，再呈现五维统计；它是管理员的运营入口，不是纯数字总览页。
14. 角色主链页面顺序固定为 `01 角色定义工作台 -> 02 使用前说明与调用预览 -> 03 试用与测试 -> 04 治理与发布 -> 05 正式消费 -> 06 外供与追溯`。
15. `数据资产管理` 是配套管理员页，不进入角色主链编号。
16. 页头只放当前页面的全局动作；跨页跳转统一交给阶段导航、角色概览页和阻断提示，不在每个页面页头重复堆叠。
17. `02 使用前说明与调用预览` 的保存动作会把当前可编辑版本推进到 `test`；`03 试用与测试` 只承接执行 / 复测，不再负责 `draft -> test`。
18. `治理与发布` 页承接 `publish / archive`；`archived` 不再出现在活跃市场、正式消费和新外供里，但历史追溯继续保留。
19. `正式消费` 与 `外供与追溯` 都是发布后的复用面：前者面向平台内正式消费，后者面向外部环境复用，二者不互为前置，也不构成新状态。
20. `使用前说明与调用预览` 的重生成动作必须显式表达为“根据最新角色信息重生成说明卡”，并只在 `stale / 待确认更新` 上下文出现。
21. `试用与测试` 页对 `使用前说明与调用预览` 的复用，固定为“复用同一真源的测试前摘要 + 查看入口”，而不是在测试页首屏再次铺开完整说明卡。

---

## 7. DD-21 现有发布门禁补充

本轮不新建门禁体系，只在既有发布机制上补充新增 requirement。

### 新增硬门禁

1. `main_duty_cluster` 非空
2. `applicable_scenarios` 非空
3. `usage_notes` 非空
4. `support_basis_summary` 非空
5. `owner` 非空
6. `business_domain` 非空
7. `category` 非空
8. 说明卡不得处于`待确认更新`
9. 若 `output_mode = structured`，则：
   - `output_type` 非空
   - `output_schema` 完整

### 固定合法状态

1. `knowledge_refs` 可为空，但必须明确表达知识状态。
2. `data_asset_bindings` 可为空，但必须明确表达数据能力状态。
3. `output_mode = freeform` 是合法默认路径，不阻断发布。

### 软提示

1. `enterprise_role_mapping` 缺失：建议补齐企业实际角色映射
2. `point_of_view` 缺失：建议补齐分析视角，降低消费方理解成本
3. `test` 阶段 `business_domain / category` 缺失：提示尽早补齐，避免后续共享 / 发布返工

---

## 8. DD-22 对外供给稳定载体

### 最小供给单位

对外供给的最小单位固定为：

```text
单个 published role version
```

### 本轮供给形态

1. `Tool package`
2. `Skill package`

### 供给物最小内容

共同必需文件：

1. `package-manifest.json`
2. `role-brief.md`
3. `consume-contract.json`
4. `output-contract.json`
5. `writeback-policy.md`

形态专属文件：

6. `Tool package`：`tool-manifest.json`
7. `Skill package`：`SKILL.md`

固定口径：

1. 外供不是裸 API 导出。
2. 外供不是“始终跟随最新版本”。
3. 未发布版本不能生成正式供给物。
4. “是否进入外供”由用户在已发布版本上显式执行生成动作表达，不新增独立外供开关字段。
5. `role-brief.md` 必须复用平台内同一张说明卡当前保存版，不再维护第二套说明。
6. `consume-contract.json` 必须固定 `role_id / role_version_id / consume API / 输入输出边界`。
7. `output-contract.json` 至少固定 `output_mode`；若结构化输出，再固定 `output_type / output_schema`。
8. `writeback-policy.md` 必须明确外部环境不得绕开平台既有 `consume` 语义，并说明回写要求。
9. 由于 `L3` 当前不做版本快照，外供当前冻结的是身份、消费契约、输出契约与回写语义；数据能力按当前生效配置工作，不承诺版本冻结复现。
10. 若说明卡或数据能力摘要来源发生变化，已生成供给物必须被标记为“需要重新生成后再对外分发”。

---

## 9. DD-23 外部复用与追溯闭环

代表性外部环境当前只要求两类：

1. `Tool package` 代表环境：`Dify`
2. `Skill package` 代表环境：`Codex`

外部复用后，平台侧必须继续保留：

1. `role_id`
2. `role_version_id`
3. `structured_result`
4. `status`
5. `boundary_status`
6. `usage_record`

固定口径：

1. 外部环境不直接绕开平台运行。
2. 数据能力、知识状态、输出契约都要通过平台侧继续生效或被如实表达。
3. 如果未来更换代表环境，必须先回写 dossier。
4. 外供说明应复用 `使用前说明与调用预览` 的同一张说明卡真源，不再维护第二套说明。
5. “可直接使用”的最小判定标准固定为：
   - 接入方不需要手工拼接 `role_id / role_version_id / consume` 契约
   - 只需填写环境相关配置项，即可在代表环境完成一次真实调用
   - 调用后平台侧能形成对应 `usage_record`
6. 代表性验证通过标准固定为：
   - `Dify`：可导入 `Tool package` 并完成一次真实调用
   - `Codex`：可安装 `Skill package` 并完成一次真实调用
7. 外部复用链路中必须保留：
   - `role_id`
   - `role_version_id`
   - `status`
   - `boundary_status`
   - `structured_result` 或自由输出结果摘要
   - `usage_record`

---

## 10. DD-24 legacy 角色兼容

### 兼容原则

1. legacy 角色必须可打开、可编辑、可补齐。
2. 旧字段可继续被兼容读取，但不再进入 `v0.5` 新建 / 编辑主路径。
3. 未补齐新 requirement 的 legacy 角色：
   - 可继续查看和编辑
   - 不能直接当作 `v0.5` 可发布 / 可外供资产

### 旧字段处置

| 字段 / 组 | 处置方式 |
| --- | --- |
| `role_positioning` | 移出本轮输入；仅 legacy 兼容读 |
| `responsibility_boundary` | 移出本轮输入；仅 legacy 兼容读 |
| `capability_boundary / capability_level / collaboration_mode` | 移出当前正文；仅 legacy 兼容读，不再主导新页结构 |

---

## 11. 字段分层归属表

| 归属层 | 字段 |
| --- | --- |
| 角色定义层 | `name` `bio` `main_duty_cluster` `point_of_view` `decision_style` `identity_background` `speaking_style` `knowledge_refs` `knowledge_boundary` `validated_knowledge_versions` `data_asset_bindings` `output_mode` `output_type` `output_schema` `model_binding` |
| 消费契约层 | `applicable_scenarios` `usage_notes` `support_basis_summary` |
| 资产治理层 | `category` `owner` `maintainer` `business_domain` `visibility` `tags` `enterprise_role_mapping` 测试记录 发布门禁 外供生成状态 使用记录与追溯记录 数据资产管理 |

---

## 12. 设计冻结结果与执行边界

1. `design-delta.md`、`traceability.md`、`task-flows-acceptance-and-design-freeze.md`、`ui-ux-wireframes.md`、`high-fidelity-prototype-scope.md`、`delivery/test-plan-v0.5.md`、`delivery/test-cases-v0.5.md` 已完成同步。
2. 高保真原型已体现：
   - `L3` 已改为数据能力
   - `L4` 已改为输出方式 + 运行配置
   - 管理员数据资产页存在
3. 不允许再把旧 `capability_*` 口径写回新正文。
4. `Design Freeze` 已生效；后续实现不得绕过本设计真源擅自改口径。
