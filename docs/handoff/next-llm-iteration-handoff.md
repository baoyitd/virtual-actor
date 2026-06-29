# virtual-actor 下一执行方接手说明

> 项目：`virtual-actor`
> 文档用途：交由另一个 LLM、Codex 会话或执行代理继续推进时的接手说明
> 建立日期：2026-05-22

## 1. 项目位置与仓库状态

接手项目路径：

```text
/Users/baoyi/Documents/code_buddy/virtual-actor
```

当前项目已完成 GitHub 仓库化，远程 `main` 已同步。

最新机制提交：

```text
4b52fd0 chore: add iteration control gates
```

## 2. 当前版本基线

当前已验收基线：

```text
版本：v0.3.0-commercial-trial
Formal Status：Accepted
基线 dossier：/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.3.0-commercial-trial/
```

当前活跃迭代：

```text
版本：v0.4.0
Formal Status：Draft
活跃迭代指针：/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/current.txt
```

## 3. 接手后必须先阅读

```text
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/process/product-iteration-control.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/process/quality-toolchain.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/process/rule-changelog.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/process/issue-and-optimization-log.md
/Users/baoyi/Documents/code_buddy/virtual-actor/tools/skills/virtual-actor-iteration-control/SKILL.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/scope.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/design-delta.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/traceability.md
```

## 4. 工作规则

1. 后续工作按产品迭代方式推进，不允许直接进入实现。
2. 每个版本必须维护 dossier：`scope.md`、`design-delta.md`、`implementation-notes.md`、`traceability.md`。
3. 实现前必须先收口 Scope In、Scope Out、核心用户路径、测试用例、验收标准和停止条件。
4. 任何 scope 扩大、接口新增、字段变化、UI 路径变化、真实集成口径变化，都必须先回写 dossier，再继续实现。
5. Formal Status 只能使用：`Draft`、`Self-Tested`、`User-Acceptance-Candidate`、`Accepted`。
6. 不得将 mock、stub、static fixture 或 manual fixture 证据描述成真实集成证据。
7. 不得把知识平台当前 Accepted 范围表述为长期冻结公共契约版本。
8. 不得把决策产品集成混入当前角色产品迭代，除非另行立项和治理确认。
9. 未通过质量门禁前，不得声明上线完成、Accepted 或可交付最终用户使用。

## 5. v0.4.0 当前候选需求

`v0.4.0` 目前只是 Draft，占位承接下一轮需求。候选需求包括：

1. 角色模板库。
2. AI 辅助填充角色配置。
3. 历史版本详情入口。
4. 详情页枚举中文映射。

进入实现前，请先确认本轮 `v0.4.0` 实际 Scope In，并更新：

```text
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/scope.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/design-delta.md
/Users/baoyi/Documents/code_buddy/virtual-actor/docs/iterations/v0.4.0/traceability.md
/Users/baoyi/Documents/code_buddy/virtual-actor/delivery/test-plan.md
/Users/baoyi/Documents/code_buddy/virtual-actor/delivery/test-cases.md
```

其中 `delivery/test-plan.md` 和 `delivery/test-cases.md` 仅在本轮范围进入可实现状态后再同步更新。

## 6. 质量命令

```bash
cd /Users/baoyi/Documents/code_buddy/virtual-actor
npm run lint:md
vale delivery docs portfolio-sync.md
python3 scripts/iteration-guard.py --repo-root . --mode release
./venv/bin/python -m pytest tests -q
cd frontend && npm run build
```

已验证结果：

1. `iteration-guard.py` 可识别 `v0.3.0-commercial-trial` 的 `Accepted` 与 `v0.4.0` 的 `Draft`。
2. `init_iteration_version.py` 可初始化新版本 dossier。
3. `iteration-guard.py` 能拦截非法 Formal Status。
4. markdownlint、Vale、pytest、frontend build 均已通过。

## 7. 新版本初始化

如果需要启动新版本：

```bash
cd /Users/baoyi/Documents/code_buddy/virtual-actor
python3 scripts/init_iteration_version.py vX.Y.Z --repo-root . --set-current
```

启动新版本后必须先填写新版本 dossier，再进入实现。

## 8. 接手第一步

接手后第一步不是写代码，而是读取本说明和上述规则文件，确认本轮 Scope In、Scope Out 与验收标准。

若发现需要修改公共契约、跨项目依赖边界、读写边界或版本规则，必须停止相关实现并上提裁决。
