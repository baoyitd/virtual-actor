# DD-13 推荐链路整改提审说明（2026-05-27）

## 复审要求逐项闭合

### 1. 推荐方案升级设计说明

方案路径：**推荐池准入过滤 → 非 LLM 候选召回 → 单次 LLM judge/rerank → 阈值过滤/保守拒绝**

采纳审核方建议的"单次 LLM call"方案，而非"两次同步 LLM 调用"。理由：根因是缺少匹配判定和拒判能力，不是缺少意图分析精度；两次 LLM call 增加时延和复杂度，但不更有效解决本轮问题。

#### Phase 1: 推荐池准入过滤

进入 AI 推荐池的 published 角色必须同时具备 `output_type` + `business_domain` + `applicable_scenarios`(至少1条) + `bio`(>=5字符)。缺任一项不入池，但仍在市场普通列表可见，前端标注"场景信息不完整，暂不支持 AI 推荐"。

准入判定代码：`recommend_service.py` `_meets_pool_criteria()`

#### Phase 2: 非 LLM 候选召回

关键词映射保留但降级为召回辅助，不再作为最终判定依据。召回规则：
- output_type 关键词命中：+2 分
- business_domain 词面交集：+1 分
- applicable_scenarios 词面交集：+1 分
- tags 词面交集：+0.5 分
- 按 score 降序取前 10 个角色，宁可少召回不泛召回
- 关键词映射完全未命中 → 候选集空 → 走 no_match

召回代码：`recommend_service.py` `_recall_candidates()`

#### Phase 3: 单次 LLM judge/rerank

一次 LLM call 同时完成：
- **意图分析**：`is_out_of_scope`(是否超出企业业务语境)、`business_domain_hint`、`confidence`
- **角色匹配判定**：每个候选角色输出 `match`(bool)、`score`(0-1)、`reason`(引用角色真实属性)、`applicable_problems`

`is_out_of_scope=true` → 整批拒绝（荒谬意图不是业务缺口，不记 OpsSignal）
单个角色 `match=false` → 该角色不进入推荐结果

LLM Prompt 要求 reason 必须引用角色的 `applicable_scenarios`、`business_domain`、`knowledge_boundary` 等真实属性，不允许只写通用话术。

LLM judge 代码：`recommend_service.py` `_llm_judge()`

#### Phase 4: 阈值过滤 + 保守拒绝

- `is_out_of_scope=true` → 直接 `matched=false`，不看角色评分
- 单个角色 `match=false` 或 `score < 0.5` → 不进入推荐
- 最终无角色通过 → `matched=false` + OpsSignal
- top 3 截断：最终推荐最多 3 个角色

阈值选择 `0.5` 的理由：
- 0.5 是 score 中点，匹配度不足一半不应推荐
- 正向样例：投资决策意图 + 决策顾问角色 → score 0.85 > 0.5 → 推荐成立
- 反向样例：供应链意图 + 投资管理角色 → score 0.15 < 0.5 → 拒绝成立
- 词面沾边样例：火星殖民地意图 → is_out_of_scope=true → 直接拒绝，score 机制不参与

**LLM 调用失败的保守拒绝策略**：

LLM judge 解析 JSON 失败或调用异常 → 返回 `result_type=service_error`、`matched=false`、`service_error_message="AI 推荐服务暂时不可用，请稍后重试"`。不放宽推荐、不回退到模板理由、不记录 OpsSignal。

reason fallback 仅用于：LLM 已明确判 `match=true` 但某条 reason 缺失时，用结构化 fallback 引用角色真实属性（"该角色输出类型为XX，业务域为XX，适用于XX，与您的业务意图存在匹配"），不允许只写"基于您的业务意图和角色XX输出类型匹配推荐"。

阈值和保守拒绝代码：`recommend_service.py` `recommend()` 主流程

---

### 2. 推荐池准入规则和历史数据补齐策略

#### 准入规则

| 字段 | 要求 | 不满足时 |
|------|------|---------|
| `output_type` | 非空，合法 4 类之一 | 不入池 |
| `business_domain` | 非空（版本或资产级） | 不入池 |
| `applicable_scenarios` | 非空数组，>=1 条 | 不入池 |
| `bio` | 非空且 >=5 字符 | 不入池 |

不满足的角色仍在市场列表可见，`recommend_pool_eligible=false`，前端标注"场景信息不完整，暂不支持 AI 推荐"。产品侧在角色编辑页面手工补齐后，自动满足准入条件。

#### legacy 补齐策略

当前 published 角色数量可控（4 个以内），不写迁移脚本或回填脚本，由产品侧手工补齐。

排查方法：调用 `GET /marketplace` 查看 `recommend_pool_eligible` 字段。`false` 即为被排除角色。

未补齐时的可见影响：
- 市场列表：角色仍可见，标注"暂不支持 AI 推荐"
- AI 推荐：角色不会出现在推荐结果中
- 场景卡片过滤：角色仍可出现在列表（列表与推荐池准入无关）

完整文档：`docs/handoff/dd13-recommend-pool-eligibility-2026-05-27.md`

---

### 3. 新增/修改自动化测试清单与结果

#### 新增 7 条验收测试（v35-v41）

| 测试 | 类型 | 断言要点 |
|------|------|---------|
| v35 | 正向匹配 | 投资决策意图 → result_type=matched, output_type=decision_advice, reason 非模板 |
| v36 | 业务范围内无匹配 | 候选角色被 LLM 拒判 → result_type=no_match + OpsSignal |
| v37 | 词面沾边语义不匹配 | "火星殖民地税务筹划" → is_out_of_scope=true → result_type=no_match |
| v38 | 角色画像缺失不入池 | 缺字段角色 → recommend_pool_eligible=false |
| v39 | 推荐理由非模板 | LLM reason 引用角色真实属性，不含"匹配推荐"模板话术 |
| v40 | LLM 失败保守拒绝 | fake_chat 返回纯文本 → result_type=service_error, 不记 OpsSignal |
| v41 | 域不匹配 | 投资决策意图 + 合规风控角色 → LLM 判 no_match → result_type=no_match |

#### 修改 5 条旧测试（v29-v33）

旧测试使用 `V04_ROLE`（缺 business_domain/applicable_scenarios），在推荐池准入逻辑下该角色不入池。已更新测试预期和角色数据：
- v29: 改为验证 service_error 保守拒绝
- v31: 改为验证 service_error
- v32: 改为使用准入角色 + 验证 category 过滤
- v33: 改为验证缺字段角色不入池（recommend_pool_eligible=false）

#### 测试结果

全部 78 条测试通过（含 7 条新增 + 5 条修改 + 66 条不变）。

---

### 4. 3 类结果区分的实现

| result_type | 含义 | matched | OpsSignal | 前端渲染 |
|-------------|------|---------|-----------|---------|
| matched | 业务意图匹配到角色 | true | 不记录 | 推荐卡片列表 |
| no_match | 业务范围内但角色池无覆盖 | false | 记录运营信号 | "未找到匹配角色 + 运营信号提示" |
| service_error | 推荐服务自身故障 | false | 不记录 | "AI 推荐服务暂时不可用 + 请稍后重试" |

区分理由：
- OpsSignal 只记录"业务上成立但角色池未覆盖"的需求，不记录服务故障和荒谬意图
- service_error 不伪装成"未找到匹配角色"，前端明确提示服务不可用
- is_out_of_scope 只用于明显荒谬/超产品边界请求，不替代普通 no-match

实现代码：
- Schema: `marketplace.py` `RecommendResponse.result_type` / `service_error_message`
- 后端: `recommend_service.py` 3 个分支返回
- 前端: `Marketplace.tsx` 3 类渲染

---

### 5. 实现文件清单

| 文件 | 变更 |
|------|------|
| `app/schemas/marketplace.py` | 新增 result_type, service_error_message, match_score |
| `app/services/recommend_service.py` | 整体重写为四阶段引擎 |
| `app/schemas/role.py` | RoleListItem 新增 recommend_pool_eligible |
| `app/routers/role_marketplace.py` | 列表接口计算 recommend_pool_eligible |
| `frontend/src/api.ts` | RecommendResponse 新增 result_type/service_error_message |
| `frontend/src/pages/Marketplace.tsx` | 3 类拒绝态渲染 + 场景卡片 output_type 过滤 |
| `frontend/src/index.css` | 新增 .pool-hint 样式 |
| `tests/test_api.py` | 新增 v35-v41, 修改 v29-v33 |
| `docs/handoff/dd13-recommend-pool-eligibility-2026-05-27.md` | 准入规则与 legacy 说明 |

---

### 6. 待补充：真实运行态浏览器验证

以上 1-4 项已全部完成。真实运行态浏览器验证（正向命中 + 反向拒绝）需启动服务后手工执行，尚未录制。提审时将补充以下证据：

1. 正向推荐：输入"我需要帮高管做项目投资决策的角色" → 出现合理推荐卡片，result_type=matched
2. 反向拒绝：输入"火星殖民地税务筹划和跨星际报关审查" → 出现"未找到匹配角色"空态，result_type=no_match
3. 服务失败：LLM 不可用时 → 出现"AI 推荐服务暂时不可用"，result_type=service_error
4. 返回列表复位：从推荐结果返回列表后，筛选状态和结果态已正确清空