# 角色平台 → 知识平台：中文 package_id manifest 端点 404 缺陷反馈

版本：`2026-06-24`
发起方：角色产品（Virtual Actor）
接收方：知识平台（Knowledge Workbench）
目的：反馈中文 `package_id` 的 manifest/status 端点返回 404 的缺陷，请知识平台修复

前置文档：
- 知识平台就绪通知：`knowledge-to-role-retrieve-scope-ready-2026-06-23.md`
- 上位裁决：`eve` 仓库 `decision-closed-loop/role-knowledge-retrieve-scope-adjudication-2026-06-23.md`

---

## 一、缺陷描述

知识平台 `/api/public/packages` 返回 7 个知识包，其中 2 个 `package_id` 含中文字符。当角色平台请求这两个包的 manifest 或 status 端点时，知识平台返回 `404 {"error": "Not found"}`，ASCII 包名（eve、togaf、ai 等）的同类请求正常。

### 受影响的包

| package_id | name | document_count | manifest | status |
|---|---|---|---|---|
| `快消品行业知识` | `30-Resources/快消品行业知识` | 9 | ❌ 404 | ❌ 404 |
| `复星旅文知识库` | `30-Resources/复星旅文知识库` | 非零 | ❌ 404 | ❌ 404 |
| `eve` | `10-Areas/eve` | 51 | ✅ 200 | ✅ 200 |
| `togaf` | `30-Resources/togaf` | 6 | ✅ 200 | ✅ 200 |
| `ai` | `10-Areas/ai` | 非零 | ✅ 200 | ✅ 200 |
| `engineering` | `10-Areas/engineering` | 非零 | ✅ 200 | ✅ 200 |
| `product` | `10-Areas/product` | 非零 | ✅ 200 | ✅ 200 |

### 复现步骤

```bash
# 1. 确认包存在（document_count=9）
curl -s http://localhost:3099/api/public/packages | python3 -c "
import sys,json
for p in json.load(sys.stdin):
    if p.get('package_id')=='快消品行业知识':
        print(json.dumps(p, indent=2, ensure_ascii=False))
"
# 输出: {"package_id": "快消品行业知识", "name": "30-Resources/快消品行业知识", "document_count": 9, ...}

# 2. 请求 manifest（URL 编码后）
curl -s "http://localhost:3099/api/public/packages/%E5%BF%AB%E6%B6%88%E5%93%81%E8%A1%8C%E4%B8%9A%E7%9F%A5%E8%AF%86/manifest"
# 输出: {"error": "Not found"}

# 3. 请求 manifest（原始中文）
curl -s "http://localhost:3099/api/public/packages/快消品行业知识/manifest"
# 输出: {"error": "Not found"}

# 4. 对比 ASCII 包名（正常）
curl -s "http://localhost:3099/api/public/packages/eve/manifest" | python3 -c "
import sys,json
print(len(json.load(sys.stdin).get('documents',[])),'docs')
"
# 输出: 51 docs
```

### 环境

- 知识平台版本标识：`fafecb7e4b17519c06e7dd2e65ee8865619bf3ff`
- 知识平台地址：`http://localhost:3099`
- 测试时间：2026-06-24

---

## 二、影响范围

### 受影响的功能

1. **知识目录浏览**：角色平台 01 页选择"快消品行业知识"或"复星旅文知识库"包时，目录为空——用户无法浏览和选择这两个包中的文档
2. **知识 tier 统计**：角色平台 02 页"使用前说明"中，已绑定这两个包文档的 tier 分布无法计算（manifest 取不到）
3. **说明卡 source_hash**：因 tier 分布为空，说明卡来源指纹与保存时不一致，判定为 stale，阻断外供包生成

### 不受影响的功能

- **retrieve 检索**：retrieve 端点使用 `knowledge_object_ids`（文档路径）做 scope 过滤，不依赖 manifest，已验证快消品文档检索正常
- **route 路由**：独立端点，不依赖 manifest
- **packages 列表**：`GET /api/public/packages` 正常返回所有 7 个包

---

## 三、角色平台侧已做的适配

为确保非 ASCII 包名请求的 URL 合法性，角色平台已对 `package_id` 做 `urllib.parse.quote` 编码（`app/services/knowledge_platform.py:list_documents/get_manifest/get_package_status`）。但即使编码后，知识平台仍返回 404，确认是知识平台侧的路由匹配问题。

---

## 四、期望修复

请知识平台排查 `/api/public/packages/{package_id}/manifest` 和 `/api/public/packages/{package_id}/status` 端点的路由匹配逻辑，确保非 ASCII `package_id`（中文等）能正确命中。

修复后可按以下方式验证：

```bash
# 全部 7 个包的 manifest 都应返回 200
for pid in "ai" "engineering" "eve" "product" "togaf" "复星旅文知识库" "快消品行业知识"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3099/api/public/packages/$(python3 -c "import urllib.parse;print(urllib.parse.quote('$pid',safe=''))")/manifest")
  echo "$pid: $status"
done
```

期望输出：
```
ai: 200
engineering: 200
eve: 200
product: 200
togaf: 200
复星旅文知识库: 200
快消品行业知识: 200
```

---

## 五、下一步

按"先反馈再执行"原则，请知识平台确认并修复后回同步。角色平台侧在修复前可正常使用已绑定知识的 retrieve/route 功能，仅知识目录浏览和 tier 统计受限。
