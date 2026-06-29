# AI 模型可配置化整改说明（2026-05-28）

## 1. 配置入口说明

新增 6 个独立配置项，全部通过环境变量读取：

| 配置项 | 环境变量 | 默认值 | 用途 |
|--------|---------|-------|------|
| AI 推荐模型 | `AI_RECOMMEND_MODEL` | `deepseek-v4-pro` | 推荐链路 LLM judge/rerank |
| AI 推荐温度 | `AI_RECOMMEND_TEMPERATURE` | `0.3` | 推荐链路 LLM temperature |
| AI 推荐最大 token | `AI_RECOMMEND_MAX_TOKENS` | `4096` | 推荐链路 LLM max_tokens |
| AI 创建模型 | `AI_CREATE_MODEL` | `deepseek-v4-pro` | 创建草案链路 LLM |
| AI 创建温度 | `AI_CREATE_TEMPERATURE` | `0.7` | 创建草案链路 LLM temperature |
| AI 创建最大 token | `AI_CREATE_MAX_TOKENS` | `4096` | 创建草案链路 LLM max_tokens |

默认值与原硬编码值一致，零回归风险。

配置方式：
- 开发环境：`.env` 文件或环境变量
- Docker 环境：`docker-compose.yml` environment 区块（已添加）
- 生产环境：环境变量注入

## 2. 代码改动说明

| 文件 | 改动 |
|------|------|
| `app/config.py` | 新增 6 个配置项（AI_RECOMMEND_MODEL/TEMPERATURE/MAX_TOKENS + AI_CREATE_MODEL/TEMPERATURE/MAX_TOKENS） |
| `app/services/recommend_service.py` | `model="deepseek-v4-pro"` → `model=settings.AI_RECOMMEND_MODEL`；`temperature=0.3` → `temperature=settings.AI_RECOMMEND_TEMPERATURE`；`max_tokens=4096` → `max_tokens=settings.AI_RECOMMEND_MAX_TOKENS`；新增 `from app.config import settings` |
| `app/services/ai_create_service.py` | `model="deepseek-v4-pro"` → `model=settings.AI_CREATE_MODEL`；`temperature=0.7` → `temperature=settings.AI_CREATE_TEMPERATURE`；`max_tokens=4096` → `max_tokens=settings.AI_CREATE_MAX_TOKENS`；新增 `from app.config import settings` |
| `docker-compose.yml` | environment 区块新增 6 条 AI 模型配置环境变量 |

两个服务中不再存在任何硬编码模型名。

## 3. 真实运行态证据

### 证据 1：默认配置下模型名与硬编码值一致

```
AI_RECOMMEND_MODEL=deepseek-v4-pro
AI_RECOMMEND_TEMPERATURE=0.3
AI_RECOMMEND_MAX_TOKENS=4096
AI_CREATE_MODEL=deepseek-v4-pro
AI_CREATE_TEMPERATURE=0.7
AI_CREATE_MAX_TOKENS=4096
```

### 证据 2：配置切换后模型名实际变化

设置 `AI_RECOMMEND_MODEL=test-model-switch` 和 `AI_CREATE_MODEL=test-create-switch` 后重启容器：

```
AI_RECOMMEND_MODEL=test-model-switch
AI_CREATE_MODEL=test-create-switch
```

容器内 settings 读取值随环境变量变化，不再硬编码。

### 证据 3：代码中不再硬编码模型名

容器内验证：
- `recommend_service.py` 不含 `"deepseek-v4-pro"` 硬编码字符串
- `ai_create_service.py` 不含 `"deepseek-v4-pro"` 硬编码字符串
- 两文件均使用 `settings.AI_RECOMMEND_MODEL` / `settings.AI_CREATE_MODEL` 读取配置

## 4. 回归说明

本次改动不影响现有角色测试 / consume 路径：

1. 角色测试和 consume 使用的是 `model_binding` 机制（每个角色独立配置 model_provider + model_name + temperature + max_tokens），走 `llm_service.chat(model=role.model_binding.model_name)`，与本次新增的 `AI_RECOMMEND_*` 和 `AI_CREATE_*` 配置完全无关。

2. 默认值与原硬编码值完全一致（推荐=deepseek-v4-pro/0.3/4096，创建=deepseek-v4-pro/0.7/4096），在不设环境变量的情况下行为与改动前完全相同。

3. 自动化测试 79 条全部通过，无回归。