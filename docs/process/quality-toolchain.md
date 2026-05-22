# 质量工具链

> 适用项目：`virtual-actor`
> 建立日期：2026-05-22

## 1. 文档与迭代闸门

```bash
npm run lint:md
vale delivery docs portfolio-sync.md
python3 scripts/iteration-guard.py --repo-root . --mode release
```

用途：

1. `markdownlint-cli2` 检查 Markdown 基础结构。
2. `Vale` 拦截非正式状态名和 mock/fixture 冒充真实集成的高风险表述。
3. `iteration-guard.py` 检查版本、Formal Status、Interface Delta、dossier、人工冒烟和真实集成口径。

## 2. 产品实现闸门

```bash
./venv/bin/python -m pytest tests -q
python3 -m compileall app
cd frontend && npm run build
```

用途：

1. 后端 API、知识平台服务和版本规则回归。
2. Python 模块编译检查。
3. React 正式入口生产构建。

## 3. 当前不接入的机制

本项目当前不是 Markdown/Vault 真源项目，因此不接入 knowledge-workbench 的 `quality-check.py`。

本轮也不启用 pre-commit hook。先通过显式命令和 GitHub 提交前人工执行闸门，等流程稳定后再决定是否加入 pre-commit。
