# 角色产品 -> 知识平台 真实集成验收阻塞说明

> 日期：2026-05-21
> 发起方：角色产品 / virtual-actor
> 接收方：知识平台 / knowledge-workbench
> 目的：反馈本轮真实集成上线验收中的实际运行态阻塞，不涉及公共契约新增或长期冻结版本声明

---

## 一、已确认通过的运行态

角色产品已按你方提供的本机入口完成第一轮真实探测：

- `GET http://127.0.0.1:3099/api/health`：通过
- `GET http://127.0.0.1:3000/`：HTTP 200，通过

这说明知识平台运行态已启动，当前问题不在“服务未启动”层面。

---

## 二、当前阻塞项

### 1. 验收服务账号无法登录

角色产品按你方提供的验收账号调用：

- `POST http://127.0.0.1:3000/api/v1/auths/signin`

请求账号：

- email: `role-acceptance@knowledge.local`
- password: `RoleAccept2026!`

当前返回：

- HTTP 400
- `The email or password provided is incorrect. Please check for typos and try logging in again.`

影响：

- 无法获取 Bearer token
- 无法继续执行 `GET /api/v1/knowledge/`
- 无法继续执行 `GET /api/v1/knowledge/{kb_id}/files`
- 无法继续执行 `POST /api/v1/retrieval/query/collection`

因此，U01 / U02 两条真实集成场景链当前被直接阻塞。

### 2. 版本快照接口返回不符合验收口径

角色产品调用：

- `GET http://127.0.0.1:3000/api/v1/version`

当前观察结果：

- HTTP 200
- 返回内容为 Open WebUI HTML 页面
- 未返回 JSON 版本快照

影响：

- 角色产品当前无法按既定实现自动读取 `knowledge_version_id`
- 发布时无法以真实版本快照完成知识版本冻结
- U03“发布追溯”场景链被阻塞

---

## 三、角色产品需要知识平台补齐的最小条件

请知识平台完成以下两项后通知角色产品继续验收：

1. 修正或重置验收服务账号，确保以下登录可成功返回 Bearer token
   `POST http://127.0.0.1:3000/api/v1/auths/signin`

2. 修正 `GET http://127.0.0.1:3000/api/v1/version`
   使其返回本轮验收口径要求的 JSON 版本快照，而不是 HTML 页面

---

## 四、说明

本说明仅反馈**本轮真实集成验收运行态阻塞**，不应被解读为：

- 发起新的公共契约变更
- 否定前序已确认的 4 项语义收口
- 将知识平台从“稳定验收态上游”降级为不可依赖

当前角色产品判断为：

- 上游健康检查已通过
- 运行态阻塞集中在“验收账号”和“版本快照接口行为”
- 两项修复后即可继续角色产品真实集成上线验收
