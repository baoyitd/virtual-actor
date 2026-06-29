# DD-13 AI 推荐池准入规则与 Legacy 角色排除说明（2026-05-27）

## 1. 推荐池准入规则

进入 AI 推荐池的 published 角色必须同时满足以下 4 项条件：

| 字段 | 要求 | 不满足时的处理 |
|------|------|---------------|
| `output_type` | 非空，值为合法的 4 类之一 | 不进入 AI 推荐池 |
| `business_domain` | 非空（版本字段或资产级字段） | 不进入 AI 推荐池 |
| `applicable_scenarios` | 非空数组，至少 1 条场景描述 | 不进入 AI 推荐池 |
| `bio` | 非空且长度 >= 5 字符 | 不进入 AI 推荐池 |

不满足条件的角色：
- 可以继续出现在资产市场普通列表（GET /marketplace）
- 不会参与 AI 推荐流程（POST /marketplace/recommend）
- 在市场列表中 `recommend_pool_eligible=false`，前端标注"场景信息不完整，暂不支持 AI 推荐"
- 产品侧可通过角色编辑页面补齐字段，补齐后自动进入推荐池（无需额外操作）

## 2. 阈值说明

`MATCH_SCORE_THRESHOLD = 0.5`

选择 0.5 作为初值的理由：
- 0.5 是 LLM judge 的 score 中点，表示"匹配与不匹配各半"
- 低于 0.5 表示 LLM 认为角色与意图的匹配度不足一半，不应推荐
- 正向样例验证：投资决策意图 + 决策顾问角色 → score 0.85 > 0.5 → 推荐成立
- 反向样例验证：供应链意图 + 投资管理角色 → score 0.15 < 0.5 → 拒绝成立
- 词面沾边样例：火星殖民地意图 → is_out_of_scope=true → 直接拒绝，score 机制不参与

后续可根据真实运行态数据调整阈值。调整时需同时更新测试样例和说明理由。

## 3. 当前已发布角色的推荐池状态

当前运行态已发布角色数量可控（4 个以内），以下为推荐池准入排查：

| 角色 | output_type | business_domain | applicable_scenarios | bio | 推荐池准入 |
|------|-------------|-----------------|---------------------|-----|-----------|
| 各已发布角色 | 需手工确认 | 需手工确认 | 需手工确认 | 需手工确认 | 需手工确认 |

**排查方法**：调用 `GET /marketplace` 查看 `recommend_pool_eligible` 字段。`false` 的角色即为被排除角色。

**补齐策略**：不写迁移脚本或回填脚本，由产品侧在角色编辑页面手工补齐。补齐字段后角色自动满足准入条件，下次调用推荐时自动进入候选池。

## 4. 未补齐时的可见影响

- **资产市场列表**：角色仍可见，但标注"场景信息不完整，暂不支持 AI 推荐"
- **AI 推荐结果**：角色不会出现在推荐结果中
- **场景卡片过滤**：角色仍可出现在场景卡片的 output_type 过滤列表中（列表与推荐池准入无关）
- **用户预期管理**：前端明确标注"暂不支持 AI 推荐"，避免"能看到但推荐不到"的误解

## 5. 实现文件清单

- 推荐池准入逻辑：[recommend_service.py](app/services/recommend_service.py) `_meets_pool_criteria()`
- 市场列表标记：[role_marketplace.py](app/routers/role_marketplace.py) `_to_list_item()`
- 前端标注渲染：[Marketplace.tsx](frontend/src/pages/Marketplace.tsx) `recommend_pool_eligible`
- Schema 字段：[role.py](app/schemas/role.py) `RoleListItem.recommend_pool_eligible`