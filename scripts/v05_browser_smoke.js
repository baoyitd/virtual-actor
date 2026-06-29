#!/usr/bin/env node
/* eslint-disable no-console */
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const baseURL = process.env.SMOKE_BASE_URL || 'http://127.0.0.1:18080';
const outputDir = process.env.SMOKE_OUTPUT_DIR || path.join(process.cwd(), 'tmp', 'v05-browser-smoke');

fs.mkdirSync(outputDir, { recursive: true });

function logStep(title) {
  console.log(`\n[SMOKE] ${title}`);
}

async function waitVisible(locator, description, timeout = 15000) {
  await locator.waitFor({ state: 'visible', timeout });
  console.log(`  - ${description}`);
}

async function screenshot(page, name, screenshots) {
  const file = path.join(outputDir, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  screenshots[name] = file;
  console.log(`  - screenshot: ${file}`);
}

function escapeLabel(label) {
  return label.replace(/"/g, '\\"');
}

async function findField(page, label) {
  const exactLabel = page.getByLabel(label, { exact: true });
  if (await exactLabel.count()) {
    return exactLabel.first();
  }

  const escaped = escapeLabel(label);
  const wrapped = page.locator(`label:has-text("${escaped}")`).locator('input, textarea, select');
  if (await wrapped.count()) {
    return wrapped.first();
  }

  const adjacent = page.locator(
    `label:text-is("${escaped}") + input, label:text-is("${escaped}") + textarea, label:text-is("${escaped}") + select`,
  );
  if (await adjacent.count()) {
    return adjacent.first();
  }

  throw new Error(`找不到字段：${label}`);
}

async function fillField(page, label, value) {
  const field = await findField(page, label);
  await field.fill(value);
}

async function clickEnabledButton(page, text) {
  const locator = page.locator(`button:has-text("${escapeLabel(text)}"):not([disabled])`).first();
  await locator.waitFor({ state: 'visible', timeout: 15000 });
  await locator.click();
}

async function clickAndWaitForPost(page, buttonText, pathFragment, expectedStatus = 200) {
  const responsePromise = page.waitForResponse(
    response =>
      response.url().includes(pathFragment)
      && response.request().method() === 'POST'
      && response.status() === expectedStatus,
    { timeout: 15000 },
  );
  await clickEnabledButton(page, buttonText);
  await responsePromise;
}

(async () => {
  const browser = await chromium.launch({ headless: process.env.SMOKE_HEADLESS !== '0' });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
  const page = await context.newPage();
  const screenshots = {};

  page.on('pageerror', error => {
    console.error(`[PAGEERROR] ${error.stack || error.message}`);
  });

  page.on('console', message => {
    if (message.type() === 'error') {
      console.error(`[BROWSER:${message.type()}] ${message.text()}`);
    }
  });

  try {
    logStep('打开登录页');
    await page.goto(baseURL, { waitUntil: 'domcontentloaded' });
    await waitVisible(page.getByText('角色资产管理平台', { exact: true }), '登录页已渲染');
    await fillField(page, '密码', 'admin123');
    await page.getByRole('button', { name: '登录' }).click();
    await waitVisible(page.getByRole('heading', { name: '角色资产工作区' }), '已进入角色列表');
    await screenshot(page, '01-role-list', screenshots);

    logStep('创建数据资产');
    await page.getByRole('link', { name: '数据资产管理' }).first().click();
    await waitVisible(page.getByRole('heading', { name: '数据资产管理' }), '已进入数据资产管理页');
    const existingAsset = page.getByRole('button', { name: /项目预算事实表/ }).first();
    if (await existingAsset.count()) {
      await waitVisible(existingAsset, '复用已存在的数据资产');
    } else {
      await fillField(page, '展示名称', '项目预算事实表');
      await fillField(page, '数据源引用', 'warehouse.main');
      await fillField(page, '数据库名', 'dw');
      await fillField(page, '表名', 'fact_project_budget');
      await page.getByLabel('范围说明').fill('可读取预算执行与偏差数据，不包含未授权明细。');
      await page.getByRole('button', { name: /保存数据资产/ }).click();
      await waitVisible(existingAsset, '数据资产已保存');
    }
    await screenshot(page, '02-data-assets', screenshots);

    logStep('AI 起草并创建角色草稿');
    await page.goto(`${baseURL}/#/create`, { waitUntil: 'domcontentloaded' });
    await waitVisible(page.getByRole('heading', { name: '新建角色定义工作台' }), '已进入角色定义工作台');
    const aiIntentInput = page.getByPlaceholder('例如：我想创建一个能帮助集团管理层做经营复盘和投资前置判断的角色，它要基于已绑定知识和经营指标，输出可复用的建议与风险提示。');
    await waitVisible(aiIntentInput, 'AI 创建输入框已渲染');
    const draftButton = page.getByRole('button', { name: '生成结构化草案' });
    if (await draftButton.isEnabled()) {
      throw new Error('AI 草案按钮在空白输入时不应可点击');
    }
    await aiIntentInput.fill('我要一个能做经营复盘和预算判断的角色，它需要结合知识和经营数据给出结构化建议。');
    await draftButton.click();
    await waitVisible(page.getByRole('button', { name: '生成中...' }), 'AI 草案生成状态已出现');
    await waitVisible(page.getByText('AI 草案已填入当前工作区，请继续人工确认。'), 'AI 草案已写入表单', 45000);
    await page.getByRole('button', { name: /项目预算事实表/ }).first().click();
    await page.getByRole('button', { name: '选择真实知识' }).click();
    await waitVisible(page.getByRole('heading', { name: '选择真实知识' }), '知识选择器已打开');
    await page.waitForFunction(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const target = buttons.find(button => button.textContent?.includes('当前知识库全选'));
      return Boolean(target && !target.disabled);
    }, { timeout: 45000 });
    await page.getByRole('button', { name: '当前知识库全选' }).click();
    await page.getByRole('button', { name: '完成选择' }).click();
    await waitVisible(page.getByText('治理测试知识'), '知识选择已回写工作台');
    await waitVisible(page.getByText('经营分析知识'), '多文件选择已回写工作台');
    await page.getByRole('button', { name: '保存草稿' }).click();
    await page.waitForURL(/#\/roles\/.+\/edit/, { timeout: 15000 });
    const roleIdMatch = page.url().match(/#\/roles\/([^/]+)\/edit/);
    if (!roleIdMatch) {
      throw new Error(`无法从 URL 提取 role_id: ${page.url()}`);
    }
    const roleId = roleIdMatch[1];
    await waitVisible(page.getByRole('heading', { name: /角色定义工作台/ }), '角色草稿已落库');
    await screenshot(page, '03-role-edit', screenshots);

    logStep('确认工作台内知识选择已保存');
    await waitVisible(page.getByText('治理测试知识'), '知识摘要保留在已保存工作台');
    await waitVisible(page.getByText('经营分析知识'), '批量选择后的第二个文件也已保留');
    await screenshot(page, '04-knowledge-selected', screenshots);

    logStep('确认说明卡当前保存版');
    await page.goto(`${baseURL}/#/roles/${roleId}/briefing`, { waitUntil: 'domcontentloaded' });
    await waitVisible(page.getByRole('heading', { name: '使用前说明与调用预览' }).first(), '已进入说明卡页面');
    await waitVisible(page.getByText('当前保存版说明卡与来源一致，可直接被使用前说明、发布和外供复用。'), '说明卡已回到 fresh');
    await screenshot(page, '05-briefing-fresh', screenshots);

    logStep('从测试页启动内部试用并执行 test-consume');
    await page.goto(`${baseURL}/#/roles/${roleId}/test`, { waitUntil: 'domcontentloaded' });
    await waitVisible(page.getByRole('heading', { name: '试用与测试' }), '已进入测试台');
    await page.getByLabel('测试查询').fill('请分析本月预算偏差。');
    const toTestResponse = page.waitForResponse(
      response => response.url().includes('/to-test') && response.request().method() === 'POST' && response.status() === 200,
      { timeout: 15000 },
    );
    const testConsumeResponse = page.waitForResponse(
      response => response.url().includes('/test-consume') && response.request().method() === 'POST' && response.status() === 200,
      { timeout: 15000 },
    );
    await page.getByRole('button', { name: '开始内部试用并执行 test-consume' }).click();
    await toTestResponse;
    console.log('  - to-test 已返回 200');
    await testConsumeResponse;
    await waitVisible(page.getByText('validation_record_id:'), '测试记录已生成');
    await waitVisible(page.getByText('成功返回'), 'test-consume 成功');
    await screenshot(page, '06-test-consume', screenshots);

    logStep('测试后再次确认说明卡');
    await page.goto(`${baseURL}/#/roles/${roleId}/briefing`, { waitUntil: 'domcontentloaded' });
    await waitVisible(page.getByText('当前来源已变化'), '测试摘要变化已触发说明卡 stale');
    await page.getByRole('button', { name: '沿用当前文字并确认' }).click();
    await waitVisible(page.getByText('当前保存版说明卡与来源一致，可直接被使用前说明、发布和外供复用。'), '说明卡再次 fresh');

    logStep('治理侧补齐并发布当前版本');
    await page.goto(`${baseURL}/#/roles/${roleId}/governance`, { waitUntil: 'domcontentloaded' });
    await waitVisible(page.getByRole('heading', { name: '治理与发布' }), '已进入治理页');
    await fillField(page, 'Owner', 'strategy-owner');
    await fillField(page, '业务域', '经营管理');
    await page.getByRole('button', { name: /保存治理项/ }).click();
    await page.locator('button:has-text("保存治理项"):not([disabled])').first().waitFor({ state: 'visible', timeout: 15000 });
    await screenshot(page, '07-governance-ready', screenshots);
    await clickAndWaitForPost(page, '发布当前版本', '/publish');
    console.log('  - publish 已返回 200');
    await screenshot(page, '08-published', screenshots);

    logStep('生成外供包并模拟外部调用');
    await page.goto(`${baseURL}/#/roles/${roleId}/exports`, { waitUntil: 'domcontentloaded' });
    await waitVisible(page.getByRole('heading', { name: '外供与追溯' }), '已进入外供页');
    await page.getByRole('button', { name: '生成 Tool package' }).click();
    await waitVisible(page.getByText('Tool package'), 'Tool package 已生成');
    await page.getByRole('button', { name: '生成 Skill package' }).click();
    await waitVisible(page.getByText('Skill package'), 'Skill package 已生成');
    await page.getByLabel('外部形态').selectOption('external_skill');
    await page.getByRole('button', { name: '模拟外部调用' }).click();
    await waitVisible(page.locator('.collapsed-note').getByText(/usage_record_id/), '外部调用结果已返回');
    await waitVisible(page.locator('.record-list').getByText('external_skill', { exact: true }), '外部调用记录已回写');
    await screenshot(page, '09-exports', screenshots);

    logStep('正式消费');
    await page.goto(`${baseURL}/#/roles/${roleId}/use`, { waitUntil: 'domcontentloaded' });
    await waitVisible(page.getByRole('heading', { name: '正式消费' }), '已进入使用台');
    await page.getByLabel('正式查询').fill('请分析本月预算偏差。');
    await page.getByRole('button', { name: '执行 consume' }).click();
    const usageResultSection = page.locator('section.detail-section').filter({
      has: page.getByRole('heading', { name: '本次消费结果' }),
    });
    await waitVisible(usageResultSection.getByRole('heading', { name: '本次消费结果' }), '正式消费结果已展示');
    await waitVisible(usageResultSection.getByText('成功返回', { exact: true }), '正式消费成功');
    await screenshot(page, '10-usage-desk', screenshots);

    logStep('资产市场与 AI 推荐');
    await page.goto(`${baseURL}/#/marketplace`, { waitUntil: 'domcontentloaded' });
    await waitVisible(page.getByRole('heading', { name: /资产市场/ }), '已进入资产市场');
    await waitVisible(page.locator('.marketplace-grid .marketplace-card').getByText('经营复盘顾问', { exact: true }).first(), '已发布角色出现在市场列表');
    await page.getByPlaceholder('例如：我需要一个帮经营管理层做预算偏差复盘的角色').fill('我需要一个帮经营管理层做预算偏差复盘的角色');
    await page.getByRole('button', { name: 'AI 推荐角色' }).click();
    await waitVisible(page.getByRole('heading', { name: 'AI 推荐结果' }), '推荐结果已展示');
    await waitVisible(page.locator('.recommend-grid .recommend-card').getByText('经营复盘顾问', { exact: true }).first(), '目标角色被推荐');
    await screenshot(page, '11-marketplace', screenshots);

    const summary = {
      baseURL,
      roleId,
      screenshots,
      completedAt: new Date().toISOString(),
    };
    fs.writeFileSync(path.join(outputDir, 'summary.json'), JSON.stringify(summary, null, 2));
    console.log(`\n[SMOKE] PASS role_id=${roleId}`);
  } finally {
    await context.close();
    await browser.close();
  }
})().catch(error => {
  console.error(`\n[SMOKE] FAIL ${error.stack || error.message}`);
  process.exitCode = 1;
});
