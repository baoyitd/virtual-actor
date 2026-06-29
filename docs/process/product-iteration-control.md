# virtual-actor 产品迭代控制规则

> **已整合**：本文档内容已全部纳入 `project-rules.md`（项目级流程与治理规则入口）。本文件保留作为历史参考，新增/修改规则请直接更新 `project-rules.md`。
>
> 适用项目：`virtual-actor`
> 建立日期：2026-05-22
> 定位：子项目内部迭代控制机制，不替代上位治理协议、公共契约裁决或交付质量门禁
> 项目级规则真源：`docs/process/project-rules.md`
> 活跃版本真源：`docs/iterations/current.txt` + 活跃版本 `README.md` + 活跃版本 dossier + 活跃 README 列出的交付真源文件

## 1. 状态口径

对外只使用 4 个 Formal Status：

1. `Draft`
2. `Self-Tested`
3. `User-Acceptance-Candidate`
4. `Accepted`

`consumer scope only`、`UI excluded`、`ready to release` 等只能作为范围说明，不能替代 Formal Status。

## 2. 每个版本的固定证据链

每个版本必须有独立 dossier：

```text
docs/iterations/<version>/
  scope.md
  design-delta.md
  implementation-notes.md
  traceability.md
```

最低要求：

1. `scope.md` 写清 `Scope In`、`Scope Out`、核心用户场景、非目标和停止条件。
2. `design-delta.md` 只写本轮相对上一版的增量设计，不重写全量产品说明。
3. `implementation-notes.md` 记录预期与实际实现的偏差、原因、用户影响和补测要求。
4. `traceability.md` 把用户场景、设计项、实现、测试证据和发布口径串起来。

## 3. 版本推进顺序

1. 新版本先初始化 dossier，并确认 `docs/iterations/current.txt` 指向当前活跃版本。
2. 实现前先补 `scope.md`、`design-delta.md` 和测试用例草案。
3. 实现中出现 scope 扩大、接口新增、字段不足、页面路径变化时，先回写 dossier，再继续实现。
4. **复审/整改/裁决等外部输入是设计输入，不是已收口设计规格**：收到复审退回整改要求、规划方裁决或终审方意见后，必须先回写 design-delta.md、scope.md、traceability.md 等设计文档，再进入代码实现。"先改代码后补文档"不属于设计先行流程（R-002，2026-05-28 补入，DD-13 整改流程违规教训）。
5. 验收前运行 `iteration-guard.py`，核对 `delivery/`、`portfolio-sync.md` 和当前 dossier 是否一致。
6. 未通过质量门禁前，不得把版本表述为 `User-Acceptance-Candidate`、`Accepted` 或上线完成。

## 4. 止损条件

遇到以下情况必须停止默认实现：

1. 需要新增或修改公共契约、跨项目依赖边界、读写边界、版本规则。
2. 真实集成能力低于 release notes 或 portfolio-sync 的表述。
3. 人工手动冒烟缺失，但版本被表述为已验收或可交付。
4. 不得将 mock、stub、static fixture 或 manual fixture 证据描述成 `real integration`。
5. 决策产品集成被混入当前角色产品 + 知识平台验收范围。

## 5. 本项目质量命令

```bash
npm run lint:md
vale delivery docs portfolio-sync.md
python3 scripts/iteration-guard.py --repo-root . --mode release
./venv/bin/python -m pytest tests -q
python3 -m compileall app
cd frontend && npm run build
```

其中前三项是迭代控制与文档质量闸门；后三项是产品实现质量闸门。
