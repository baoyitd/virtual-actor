# v0.3.0-commercial-trial 范围说明

> 版本：v0.3.0-commercial-trial
> Formal Status：Accepted
> 最后更新：2026-05-22

## 1. 本轮目标

把角色产品从原型验收推进到可供内部商业试用的最终用户产品，正式入口为 React + FastAPI 单服务地址，并完成与知识平台当前 Accepted 范围的真实集成验收。

## 2. Scope In

1. React 正式用户入口：登录、角色列表、详情、创建、编辑、知识绑定、测试台、测试历史、人工评分、发布、版本记录、归档。
2. FastAPI API：基础鉴权、角色资产、知识绑定、角色测试、人工评分、发布、版本追溯。
3. 知识平台 consumer 读取链：健康检查、登录、知识库列表、文件列表、内容读取、RAG 检索、版本快照。
4. Docker Compose 单机部署：应用、React 构建物、MySQL、环境变量模板、健康检查。
5. 人工手动冒烟 H01-H05 与程序化 UI 场景链 U01-U07。

## 3. Scope Out

1. 决策产品消费侧集成。
2. 不做长期冻结公共契约版本。
3. 公开 SaaS、计费、多租户、企业级 RBAC、HTTPS 域名和完整监控体系。
4. 知识平台管理面板 UI。
5. `prototype/` 作为最终用户验收入口。

## 4. 核心场景链

| ID | 场景 | 成功标准 |
|---|---|---|
| US-01 | 登录系统并查看角色资产看板 | 用户能登录、筛选和搜索角色 |
| US-02 | 新建角色并绑定真实知识 | 用户能填写角色、选择真实知识、保存并重开可见 |
| US-03 | 角色测试与人工评分 | 测试调用真实知识检索，展示来源与分数，并保存评分历史 |
| US-04 | 发布角色与版本追溯 | 发布生成不可覆写版本，并保存知识版本追溯 |
| US-05 | 编辑已发布角色 | 编辑后生成新草稿，原发布版本仍可查询 |

## 5. 非目标与禁止动作

1. 不把知识平台当前 Accepted 口径外推为长期冻结公共契约。
2. 不把 mock、stub、static fixture 或 manual fixture 描述成 real integration。
3. 不混入决策产品集成验收。

## 6. 验收标准

1. `delivery/test-results.md` 覆盖 U01-U07 与 H01-H05。
2. `delivery/release-notes.md` 与 `portfolio-sync.md` 均为 `Accepted`，且边界一致。
3. `iteration-guard.py --mode release` 通过。
