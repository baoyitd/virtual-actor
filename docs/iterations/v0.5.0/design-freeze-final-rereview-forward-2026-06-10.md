# v0.5.0 Design Freeze 终审复核重提说明

> 版本：v0.5.0 | 日期：2026-06-10 | Formal Status：Draft
> 当前状态：Design Freeze Status = Effective（2026-06-10 终审通过）
> 用途：作为本轮最新版终审复核提交与通过归档说明；`Formal Status` 仍保持 `Draft`

---

## 1. 本次重提背景

上一轮终审未通过，原因不是 `v0.5` 方向错误，而是**高保真原型与测试锁定仍有关键偏差**，会直接带偏后续实现。

本次重提只处理并闭合以下两类阻塞：

1. 高保真原型与真源文档对齐
2. 测试真源把关键 UI 语义和运行效果型约束显式锁死

本轮未扩 Scope，未进入实现，未修改 `Formal Status`。

## 2. 当前阶段状态

| 维度 | 状态 |
| --- | --- |
| Formal Status | Draft |
| Design Freeze Status | Effective（2026-06-10 终审确认） |
| 是否允许代码实现 | 是 |
| 当前阶段目标 | 进入代码实现准备与实现，并持续按冻结口径推进 |

## 3. 已完成的修订

### 3.1 高保真原型与 DD-18 对齐

已完成以下同步：

1. 页面外显名称统一为 `使用前说明与调用预览`，不再对外显示 `消费契约`
2. 高保真原型中的 DD-18 页面结构已改为**系统生成说明卡优先**，轻量修订入口折叠呈现
3. 不再保留“左侧编辑表单 + 右侧预览”这一会带偏实现的旧结构

### 3.2 治理阶段提示与冻结规则对齐

高保真原型中的可见文案已改为分阶段规则：

1. 起草阶段：不强制补齐全部治理项
2. 内部试用前：`owner` 必填
3. 进入“可供他人消费”前：`owner / business_domain / category` 全部为硬要求
4. 正式发布 / 外供前：继续叠加其余既有门禁

已避免旧口径“治理只在正式发布 / 外供前才要求闭合”继续误导实现和评审。

### 3.3 测试真源补齐 UI 锁定项

已在测试计划与测试用例中显式加入以下 UI 约束：

1. 页面外显名必须固定为 `使用前说明与调用预览`
2. 说明页必须以系统生成说明卡为主，不得回退成“编辑表单优先 + 预览”结构

### 3.4 测试真源补齐运行效果型约束

在上一轮基础上，进一步补强了“功能真实生效”验收，不再只停留在页面逻辑、字段保存和门禁提示。

已新增并锁定：

1. 知识绑定是否真实影响平台内 `test / consume` 结果
2. 未绑定真实知识时是否如实降级，而不是伪装为已引用真实知识
3. `knowledge_boundary` 是否在运行时真实生效
4. 数据能力绑定后是否真实走平台查询层，而不是只展示绑定状态
5. 不同数据资产绑定是否会带来结果差异
6. `freeform / structured` 是否在运行时产出不同且符合契约的结果形态
7. 外供后的真实调用是否继续遵循同一输出契约，并如实保留知识 / 数据限制

## 4. 本次终审应重点复核的材料

### 4.1 真源文档

1. `README.md`
2. `requirements-analysis.md`
3. `requirements-checklist.md`
4. `scope.md`
5. `design-delta.md`
6. `traceability.md`
7. `task-flows-acceptance-and-design-freeze.md`
8. `ui-ux-wireframes.md`
9. `high-fidelity-prototype-scope.md`

### 4.2 高保真原型

1. `prototype/v0.5-hifi/index.html`
2. `prototype/v0.5-hifi/app.js`
3. `prototype/v0.5-hifi/styles.css`

### 4.3 测试真源

1. `delivery/test-plan-v0.5.md`
2. `delivery/test-cases-v0.5.md`

## 5. 本次终审结果

本次重提后的终审结论为：

1. 未发现新的冻结阻塞项
2. 上一轮终审指出的原型偏差已针对性回写
3. 测试真源已不再只约束“页面存在”，而开始约束“配置对真实运行结果的影响”
4. 当前材料已通过 Design Freeze 终审复核

## 6. 终审结论回写

本次终审已确认：

1. 上一轮终审指出的两类阻塞已闭合
2. 当前高保真原型与 7 份真源已达到可冻结程度
3. `Design Freeze Status` 已从 `Pending Final Review` 升级为 `Effective`

补充说明：

1. 即使终审通过，`Formal Status` 仍保持 `Draft`
2. 当前已允许进入代码实现准备与实现阶段

## 7. 提交前校验

本次重提前已完成以下校验：

1. `npm run lint:md` 通过
2. `vale delivery docs/iterations/v0.5.0` 通过
3. `node --check prototype/v0.5-hifi/app.js` 通过

---

> 结论：本材料对应的 **Design Freeze 终审已通过**；`Formal Status` 仍为 `Draft`，当前可进入代码实现准备与实现。
