# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: scripts/v05-browser-smoke.spec.js >> v0.5 核心页面与主流程浏览器烟测
- Location: scripts/v05-browser-smoke.spec.js:10:1

# Error details

```
Error: Channel closed
```

```
Error: locator.fill: Test ended.
Call log:
  - waiting for getByLabel('密码')

```

# Page snapshot

```yaml
- main [ref=e3]:
  - generic [ref=e4]:
    - generic [ref=e5]: VA
    - heading "角色资产管理平台" [level=1] [ref=e6]
    - paragraph [ref=e7]: 面向企业 AI 角色资产运营的统一工作区，覆盖角色定义、说明卡、治理发布与外供复用。
    - generic [ref=e8]: 账号
    - textbox [ref=e9]: admin
    - generic [ref=e10]: 密码
    - textbox [ref=e11]
    - button "登录" [ref=e12] [cursor=pointer]
```

# Test source

```ts
  1   | const { test, expect } = require('@playwright/test');
  2   | const fs = require('fs');
  3   | const path = require('path');
  4   | 
  5   | const baseURL = process.env.SMOKE_BASE_URL || 'http://127.0.0.1:18080';
  6   | const outputDir = process.env.SMOKE_OUTPUT_DIR || path.join(process.cwd(), 'tmp', 'v05-browser-smoke');
  7   | 
  8   | test.describe.configure({ mode: 'serial', timeout: 180_000 });
  9   | 
  10  | test('v0.5 核心页面与主流程浏览器烟测', async ({ page }) => {
  11  |   fs.mkdirSync(outputDir, { recursive: true });
  12  |   const screenshots = {};
  13  | 
  14  |   async function shot(name) {
  15  |     const file = path.join(outputDir, `${name}.png`);
  16  |     await page.screenshot({ path: file, fullPage: true });
  17  |     screenshots[name] = file;
  18  |   }
  19  | 
  20  |   async function fillField(label, value) {
  21  |     await page.getByLabel(label, { exact: true }).fill(value);
  22  |   }
  23  | 
  24  |   async function waitBriefingFresh() {
  25  |     await expect(page.getByText('当前保存版说明卡与来源一致，可直接被使用前说明、发布和外供复用。')).toBeVisible();
  26  |   }
  27  | 
  28  |   await page.goto(baseURL, { waitUntil: 'domcontentloaded' });
  29  |   await expect(page.getByRole('heading', { name: '角色资产管理平台' })).toBeVisible();
> 30  |   await page.getByLabel('密码').fill('admin123');
      |                               ^ Error: locator.fill: Test ended.
  31  |   await page.getByRole('button', { name: '登录' }).click();
  32  |   await expect(page.getByRole('heading', { name: '角色资产工作区' })).toBeVisible();
  33  |   await shot('01-role-list');
  34  | 
  35  |   await page.getByRole('link', { name: '数据资产管理' }).first().click();
  36  |   await expect(page.getByRole('heading', { name: '数据资产管理' })).toBeVisible();
  37  |   await fillField('展示名称', '项目预算事实表');
  38  |   await fillField('数据源引用', 'warehouse.main');
  39  |   await fillField('数据库名', 'dw');
  40  |   await fillField('表名', 'fact_project_budget');
  41  |   await page.getByLabel('范围说明').fill('可读取预算执行与偏差数据，不包含未授权明细。');
  42  |   await page.getByRole('button', { name: /保存数据资产/ }).click();
  43  |   await expect(page.getByText('项目预算事实表')).toBeVisible();
  44  |   await shot('02-data-assets');
  45  | 
  46  |   await page.goto(`${baseURL}/#/create`, { waitUntil: 'domcontentloaded' });
  47  |   await expect(page.getByRole('heading', { name: '新建角色定义工作台' })).toBeVisible();
  48  |   await page.getByRole('button', { name: '生成结构化草案' }).click();
  49  |   await expect(page.getByText('AI 草案已填入当前工作区，请继续人工确认。')).toBeVisible();
  50  |   await page.getByRole('button', { name: /项目预算事实表/ }).click();
  51  |   await page.getByRole('button', { name: '保存草稿' }).click();
  52  |   await page.waitForURL(/#\/roles\/.+\/edit/);
  53  |   const roleIdMatch = page.url().match(/#\/roles\/([^/]+)\/edit/);
  54  |   if (!roleIdMatch) {
  55  |     throw new Error(`无法从 URL 提取 role_id: ${page.url()}`);
  56  |   }
  57  |   const roleId = roleIdMatch[1];
  58  |   await expect(page.getByRole('heading', { name: /角色定义工作台/ })).toBeVisible();
  59  |   await shot('03-role-edit');
  60  | 
  61  |   await page.getByRole('button', { name: /治理测试知识/ }).first().click();
  62  |   await expect(page.getByRole('button', { name: /治理测试知识 ×/ })).toBeVisible();
  63  |   await shot('04-knowledge-bound');
  64  | 
  65  |   await page.goto(`${baseURL}/#/roles/${roleId}/briefing`, { waitUntil: 'domcontentloaded' });
  66  |   await expect(page.getByRole('heading', { name: '使用前说明与调用预览' })).toBeVisible();
  67  |   await expect(page.getByText('当前来源已变化')).toBeVisible();
  68  |   await page.getByRole('button', { name: '沿用当前文字并确认' }).click();
  69  |   await waitBriefingFresh();
  70  |   await shot('05-briefing-fresh');
  71  | 
  72  |   await page.goto(`${baseURL}/#/roles/${roleId}/governance`, { waitUntil: 'domcontentloaded' });
  73  |   await expect(page.getByRole('heading', { name: '治理与发布' })).toBeVisible();
  74  |   await fillField('Owner', 'strategy-owner');
  75  |   await fillField('业务域', '经营管理');
  76  |   await page.getByRole('button', { name: /保存治理项/ }).click();
  77  |   await page.getByRole('button', { name: '进入内部试用' }).click();
  78  |   await expect(page.getByText('内部试用')).toBeVisible();
  79  |   await shot('06-governance-test-ready');
  80  | 
  81  |   await page.goto(`${baseURL}/#/roles/${roleId}/test`, { waitUntil: 'domcontentloaded' });
  82  |   await expect(page.getByRole('heading', { name: '试用与测试' })).toBeVisible();
  83  |   await page.getByLabel('测试查询').fill('请分析本月预算偏差。');
  84  |   await page.getByRole('button', { name: '执行 test-consume' }).click();
  85  |   await expect(page.getByText('validation_record_id:')).toBeVisible();
  86  |   await expect(page.getByText('成功返回')).toBeVisible();
  87  |   await shot('07-test-consume');
  88  | 
  89  |   await page.goto(`${baseURL}/#/roles/${roleId}/briefing`, { waitUntil: 'domcontentloaded' });
  90  |   await expect(page.getByText('当前来源已变化')).toBeVisible();
  91  |   await page.getByRole('button', { name: '沿用当前文字并确认' }).click();
  92  |   await waitBriefingFresh();
  93  | 
  94  |   await page.goto(`${baseURL}/#/roles/${roleId}/governance`, { waitUntil: 'domcontentloaded' });
  95  |   await page.getByRole('button', { name: '发布当前版本' }).click();
  96  |   await expect(page.getByText('已发布')).toBeVisible();
  97  |   await shot('08-published');
  98  | 
  99  |   await page.goto(`${baseURL}/#/roles/${roleId}/exports`, { waitUntil: 'domcontentloaded' });
  100 |   await expect(page.getByRole('heading', { name: '外供与追溯' })).toBeVisible();
  101 |   await page.getByRole('button', { name: '生成 Tool package' }).click();
  102 |   await expect(page.getByText('Tool package')).toBeVisible();
  103 |   await page.getByRole('button', { name: '生成 Skill package' }).click();
  104 |   await expect(page.getByText('Skill package')).toBeVisible();
  105 |   await page.getByLabel('外部形态').selectOption('external_skill');
  106 |   await page.getByRole('button', { name: '模拟外部调用' }).click();
  107 |   await expect(page.getByText(/usage_record_id/)).toBeVisible();
  108 |   await expect(page.getByText('external_skill')).toBeVisible();
  109 |   await shot('09-exports');
  110 | 
  111 |   await page.goto(`${baseURL}/#/roles/${roleId}/use`, { waitUntil: 'domcontentloaded' });
  112 |   await expect(page.getByRole('heading', { name: '正式消费' })).toBeVisible();
  113 |   await page.getByLabel('正式查询').fill('请分析本月预算偏差。');
  114 |   await page.getByRole('button', { name: '执行 consume' }).click();
  115 |   await expect(page.getByRole('heading', { name: '本次消费结果' })).toBeVisible();
  116 |   await expect(page.getByText('成功返回')).toBeVisible();
  117 |   await shot('10-usage-desk');
  118 | 
  119 |   await page.goto(`${baseURL}/#/marketplace`, { waitUntil: 'domcontentloaded' });
  120 |   await expect(page.getByRole('heading', { name: /资产市场/ })).toBeVisible();
  121 |   await expect(page.getByText('经营复盘顾问')).toBeVisible();
  122 |   await page.getByPlaceholder('例如：我需要一个帮经营管理层做预算偏差复盘的角色').fill('我需要一个帮经营管理层做预算偏差复盘的角色');
  123 |   await page.getByRole('button', { name: 'AI 推荐角色' }).click();
  124 |   await expect(page.getByRole('heading', { name: 'AI 推荐结果' })).toBeVisible();
  125 |   await expect(page.getByText('经营复盘顾问')).toBeVisible();
  126 |   await shot('11-marketplace');
  127 | 
  128 |   const summaryPath = path.join(outputDir, 'summary.json');
  129 |   fs.writeFileSync(summaryPath, JSON.stringify({ baseURL, roleId, screenshots }, null, 2));
  130 | });
```