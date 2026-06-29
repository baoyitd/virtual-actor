const ROLE_SNAPSHOT_META = {
  roleId: "41cee65b-actor-ops",
  roleVersionId: "rv_2026_06_08_v3",
  versionLabel: "v3",
};

const screenMeta = {
  workspace: {
    title: "角色定义工作台",
    subtitle:
      "这页只回答一个问题：一个角色本身由什么组成。主骨架必须回到 L1-L4。",
  },
  briefing: {
    title: "使用前说明与调用预览",
    subtitle:
      "这页以系统生成说明卡回答别人怎么正确地使用它、为什么可以信它。",
  },
  validation: {
    title: "试用与测试",
    subtitle:
      "先验证当前角色版本在既有知识、数据和输出配置下能不能工作，再进入治理与发布。",
  },
  publish: {
    title: "治理与发布",
    subtitle:
      "这里不再承接测试动作，只负责治理字段、发布门禁和版本级发布动作。",
  },
  usage: {
    title: "正式消费",
    subtitle:
      "正式消费固定面向已发布版本，调用前先看同一张说明卡，再决定是否继续使用。",
  },
  "data-assets": {
    title: "数据资产管理",
    subtitle:
      "管理员在这里维护可绑定的数据资产项；角色页只做选择，不现场创建。",
  },
  package: {
    title: "外供与追溯",
    subtitle:
      "外供建立在当前平台既有 consume 语义和已发布角色版本之上，并继续形成追溯闭环。",
  },
};

const scenarioSuggestions = [
  "经营复盘",
  "投资分析前置判断",
  "经营诊断",
  "预算编制前置评估",
  "项目立项前分析",
];

const knowledgeCatalog = [
  {
    id: "eve-weekly-caliber",
    kbId: "knowledge-eve",
    kbName: "knowledge-eve",
    title: "经营周报口径说明",
    version: "kv_2026_06_01",
    summary: "经营周报核心指标、归因维度和对齐口径。",
    path: "10-Areas/eve/master/weekly-metric-caliber.md",
  },
  {
    id: "eve-review-pattern",
    kbId: "knowledge-eve",
    kbName: "knowledge-eve",
    title: "经营复盘框架",
    version: "kv_2026_06_03",
    summary: "经营复盘常用问题拆解框架和建议结构。",
    path: "10-Areas/eve/master/ops-review-pattern.md",
  },
  {
    id: "eve-investment-check",
    kbId: "knowledge-eve",
    kbName: "knowledge-eve",
    title: "投资前分析清单",
    version: "kv_2026_05_30",
    summary: "投资分析前置判断需要检查的关键因子。",
    path: "10-Areas/eve/master/investment-checklist.md",
  },
  {
    id: "finance-risk-exposure",
    kbId: "knowledge-finance",
    kbName: "knowledge-finance",
    title: "损益与风险暴露指引",
    version: "kv_2026_05_28",
    summary: "经营风险暴露和损益异常的解释口径。",
    path: "20-Domains/finance/risk-exposure-guide.md",
  },
  {
    id: "finance-budget-note",
    kbId: "knowledge-finance",
    kbName: "knowledge-finance",
    title: "预算跟踪说明",
    version: "kv_2026_05_18",
    summary: "预算跟踪、偏差分析和动作建议模板。",
    path: "20-Domains/finance/budget-tracking-note.md",
  },
];

const dataAssetCatalogSeed = [
  {
    id: "ops-metric-daily",
    displayName: "经营指标日表",
    datasourceRef: "warehouse.ops_core",
    databaseName: "ops_dw",
    tableName: "fact_daily_metric",
    scopeSummary: "可读取经营指标、收入和效率指标，粒度到组织 / 日。",
    freshness: "T+1",
    ownerTeam: "经营分析组",
    status: "active",
  },
  {
    id: "project-budget-fact",
    displayName: "项目预算事实表",
    datasourceRef: "warehouse.finance_budget",
    databaseName: "finance_dw",
    tableName: "fact_project_budget",
    scopeSummary: "可读取项目预算、执行偏差和科目结构，粒度到项目 / 月。",
    freshness: "T+1",
    ownerTeam: "财务 BP",
    status: "active",
  },
  {
    id: "approval-log-ledger",
    displayName: "审批日志明细",
    datasourceRef: "warehouse.workflow",
    databaseName: "workflow_dw",
    tableName: "fact_approval_log",
    scopeSummary: "可读取审批流节点和处理时长，粒度到单据 / 节点。",
    freshness: "小时级",
    ownerTeam: "流程运营组",
    status: "inactive",
  },
];

const outputModeMeta = {
  freeform: {
    title: "自由输出",
    description:
      "默认合法路径。角色先按自然语言输出结果，不强制要求结构化模板。",
  },
  structured: {
    title: "结构化输出",
    description:
      "当消费方需要稳定模板时，再进入结构化路径并选择平台模板。",
  },
};

const outputChoiceMeta = {
  decision_advice: {
    title: "决策建议",
    code: "decision_advice",
    description: "适合经营判断、投资前置分析和建议草案输出。",
    schema: [
      { key: "position", label: "立场 / 倾向" },
      { key: "key_reasons", label: "关键理由" },
      { key: "major_risks", label: "主要风险" },
      { key: "suggested_actions", label: "建议动作" },
      { key: "references", label: "引用依据" },
    ],
    businessFields: [
      "判断对象（如项目 / 事项 / 指标）",
      "时间范围",
      "关键异常点",
    ],
  },
  risk_analysis: {
    title: "风险分析",
    code: "risk_analysis",
    description: "适合风险识别、暴露说明和缓释建议输出。",
    schema: [
      { key: "key_findings", label: "关键发现" },
      { key: "risk_items", label: "风险项" },
      { key: "overall_risk_level", label: "综合风险等级" },
      { key: "suggested_mitigations", label: "建议缓解措施" },
      { key: "references", label: "引用依据" },
    ],
    businessFields: ["风险主体", "影响范围", "风险暴露场景"],
  },
  policy_explanation: {
    title: "制度解释",
    code: "policy_explanation",
    description: "适合制度条款解释、操作边界说明和可做 / 不可做判断。",
    schema: [
      { key: "applicable_clauses", label: "适用条款" },
      { key: "clause_explanation", label: "条款解释" },
      { key: "allowed_actions", label: "可做事项" },
      { key: "prohibited_actions", label: "不可做事项" },
      { key: "references", label: "引用依据" },
    ],
    businessFields: ["制度版本", "适用组织范围", "特殊前提条件"],
  },
  review_findings: {
    title: "专业审查",
    code: "review_findings",
    description: "适合材料审查、问题识别和整改意见输出。",
    schema: [
      { key: "issues", label: "问题项" },
      { key: "items_to_confirm", label: "待确认事项" },
      { key: "overall_severity", label: "综合严重等级" },
      { key: "references", label: "引用依据" },
    ],
    businessFields: ["审查对象", "批次 / 版本", "整改跟踪口径"],
  },
};

const KNOWLEDGE_UNBOUND_MESSAGE =
  "当前未绑定真实知识，不提供知识追溯型支撑。";
const DATA_ASSET_UNBOUND_MESSAGE = "当前未授权结构化业务数据。";

const stageMeta = [
  {
    key: "draft",
    title: "起草角色",
    description: "先把角色本体立住，不要求一次性补满治理项。",
  },
  {
    key: "briefing",
    title: "补齐使用前说明",
    description: "先让别人知道这个角色怎么用、为什么可信。",
  },
  {
    key: "validation",
    title: "试用与测试",
    description: "先验证当前版本能不能工作，再进入治理与发布。",
  },
  {
    key: "governance",
    title: "治理与发布",
    description: "补齐治理主路径，闭合发布门禁并生成已发布版本。",
  },
  {
    key: "reuse",
    title: "正式复用",
    description: "发布后进入平台内正式消费，或进一步生成外供物。",
  },
];

const routeByRequirement = {
  knowledgeState: { screen: "workspace", step: "knowledge" },
  dataAssetState: { screen: "workspace", step: "capability" },
  hasTestEvidence: { screen: "validation" },
  outputMode: { screen: "workspace", step: "output" },
  structuredContract: { screen: "workspace", step: "output" },
  mainDuty: { screen: "workspace", step: "identity" },
  pointOfView: { screen: "workspace", step: "identity" },
  scenarios: { screen: "briefing" },
  usageNotes: { screen: "briefing" },
  supportBasis: { screen: "briefing" },
  briefingFresh: { screen: "briefing" },
  owner: { screen: "publish" },
  businessDomain: { screen: "publish" },
  category: { screen: "publish" },
};

const BRIEFING_SOURCE_FIELDS = new Set([
  "name",
  "bio",
  "mainDuty",
  "pointOfView",
  "decisionStyle",
  "identityBackground",
  "speakingStyle",
  "knowledgeBoundary",
  "outputMode",
  "outputType",
]);

const manualState = {
  mode: "manual",
  intentDescription:
    "我想创建一个能帮助集团管理层做经营复盘和投资前置判断的角色。它要基于经营分析知识和指标口径，输出结构化建议与风险提示，不替代最终经营决策。",
  name: "经营分析顾问",
  bio: "",
  enterpriseRoleMappings: [],
  mainDuty: "",
  scenarios: ["经营复盘", "投资分析前置判断"],
  tags: "经营, 分析, 复盘",
  category: "职能助手",
  owner: "finance.bp.owner",
  maintainer: "strategy.ops",
  businessDomain: "经营分析",
  visibility: "内部",
  briefingNeedsRefresh: false,
  identityBackground: "",
  pointOfView: "",
  decisionStyle: "均衡审慎",
  speakingStyle: "",
  usageNotes: "",
  supportBasis: "",
  knowledgeMode: "unbound",
  selectedKnowledgeIds: [],
  hasTestEvidence: true,
  testScore: "4.6 / 5",
  testSummary: "2026-06-06 · 运营复盘场景",
  knowledgeBoundary: "",
  dataAssetMode: "unbound",
  selectedDataAssetIds: [],
  outputMode: "freeform",
  outputType: "decision_advice",
  modelProvider: "custom",
  modelName: "deepseek-v4-pro",
  temperature: "0.3",
  maxTokens: "4096",
  packageMode: "tool",
  isPublished: false,
  activeAdminDataAssetId: "ops-metric-daily",
};

const aiDraftState = {
  mode: "ai",
  intentDescription:
    "我想创建一个能帮助集团管理层做经营复盘和投资前置判断的角色。它要基于经营分析知识和指标口径，输出结构化建议与风险提示，不替代最终经营决策。",
  name: "经营分析顾问",
  bio: "围绕经营复盘、投资前置判断和经营诊断，输出结构化建议与风险提示。",
  enterpriseRoleMappings: [],
  mainDuty: "经营分析结论提炼与建议生成",
  scenarios: ["经营复盘", "投资分析前置判断", "经营诊断"],
  tags: "经营, 分析, 决策辅助",
  category: "职能助手",
  owner: "finance.bp.owner",
  maintainer: "strategy.ops",
  businessDomain: "经营分析",
  visibility: "内部",
  briefingNeedsRefresh: false,
  identityBackground:
    "具备集团经营分析、预算跟踪和业务复盘经验，擅长从收入、成本、效率和组织动作多维度看问题。",
  pointOfView:
    "优先关注经营结果背后的关键驱动因素，强调用数据解释现象，用业务动作闭环问题。",
  decisionStyle: "均衡审慎",
  speakingStyle: "先给结论，再给依据与建议，语言正式简洁。",
  usageNotes:
    "面向经营管理层、财务 BP 或上游决策系统使用。调用前应提供经营背景、核心指标和需要判断的问题，获得建议草案或结构化结果。",
  supportBasis:
    "基于经营分析知识、固定输出模板和既有测试基础成立，适合经营复盘和投资判断前置分析。",
  knowledgeMode: "bound",
  selectedKnowledgeIds: [
    "eve-weekly-caliber",
    "eve-review-pattern",
    "eve-investment-check",
  ],
  hasTestEvidence: true,
  testScore: "4.6 / 5",
  testSummary: "2026-06-06 · 运营复盘场景",
  knowledgeBoundary:
    "仅基于已绑定知识和输入材料作答，不覆盖未验证的外部市场一手情报。",
  dataAssetMode: "bound",
  selectedDataAssetIds: ["ops-metric-daily"],
  outputMode: "structured",
  outputType: "decision_advice",
  modelProvider: "custom",
  modelName: "deepseek-v4-pro",
  temperature: "0.3",
  maxTokens: "4096",
  packageMode: "tool",
  isPublished: false,
  activeAdminDataAssetId: "ops-metric-daily",
};

const state = structuredClone(manualState);
const dataAssetCatalogState = structuredClone(dataAssetCatalogSeed);
state.logs = [];

const baselineRequirementMap = [
  {
    key: "knowledgeState",
    label: "知识依据状态已确认",
    group: "v0.4 基线",
    done: () => isKnowledgeStateConfirmed(),
  },
  {
    key: "hasTestEvidence",
    label: "至少 1 次角色测试已完成",
    group: "v0.4 基线",
    done: () => Boolean(state.hasTestEvidence),
  },
  {
    key: "outputMode",
    label: "输出方式已明确",
    group: "v0.4 基线",
    done: () => isFilled(state.outputMode),
  },
  {
    key: "structuredContract",
    label: "结构化输出契约已完整（仅 structured 路径）",
    group: "v0.4 基线",
    done: () => isStructuredContractReady(),
  },
];

const addedRequirementMap = [
  {
    key: "mainDuty",
    label: "核心职责已明确",
    group: "v0.5 补充",
    done: () => isFilled(state.mainDuty),
  },
  {
    key: "scenarios",
    label: "适用场景已填写",
    group: "v0.5 补充",
    done: () => Array.isArray(state.scenarios) && state.scenarios.length > 0,
  },
  {
    key: "usageNotes",
    label: "使用说明已填写",
    group: "v0.5 补充",
    done: () => isFilled(state.usageNotes),
  },
  {
    key: "supportBasis",
    label: "可信依据摘要已填写",
    group: "v0.5 补充",
    done: () => isFilled(state.supportBasis),
  },
  {
    key: "briefingFresh",
    label: "说明卡已按最新来源重新确认",
    group: "v0.5 补充",
    done: () => !state.briefingNeedsRefresh,
  },
];

const softRequirementMap = [
  {
    key: "enterpriseRoleMappings",
    label: "建议补齐企业实际角色映射",
    done: () =>
      Array.isArray(state.enterpriseRoleMappings) &&
      state.enterpriseRoleMappings.length > 0,
  },
];

const definitionRequirementMap = [
  {
    key: "mainDuty",
    label: "L1 核心职责已明确",
    group: "角色定义",
    done: () => isFilled(state.mainDuty),
  },
  {
    key: "pointOfView",
    label: "L1 分析视角已明确",
    group: "角色定义",
    done: () => isFilled(state.pointOfView),
  },
  {
    key: "knowledgeState",
    label: "L2 知识依据状态已确认",
    group: "角色定义",
    done: () => isKnowledgeStateConfirmed(),
  },
  {
    key: "dataAssetState",
    label: "L3 数据能力状态已确认",
    group: "角色定义",
    done: () => isDataAssetStateConfirmed(),
  },
  {
    key: "outputMode",
    label: "L4 输出方式已明确",
    group: "角色定义",
    done: () => isFilled(state.outputMode),
  },
  {
    key: "structuredContract",
    label: "L4 结构化输出契约已完整（仅 structured 路径）",
    group: "角色定义",
    done: () => isStructuredContractReady(),
  },
];

const contractRequirementMap = [
  {
    key: "scenarios",
    label: "适用场景已填写",
    group: "使用前说明",
    done: () => Array.isArray(state.scenarios) && state.scenarios.length > 0,
  },
  {
    key: "usageNotes",
    label: "使用说明已填写",
    group: "使用前说明",
    done: () => isFilled(state.usageNotes),
  },
  {
    key: "supportBasis",
    label: "可信依据摘要已填写",
    group: "使用前说明",
    done: () => isFilled(state.supportBasis),
  },
];

const governanceRequirementMap = [
  {
    key: "hasTestEvidence",
    label: "已有测试证据可供发布侧核对",
    group: "资产治理",
    done: () => Boolean(state.hasTestEvidence),
  },
  {
    key: "owner",
    label: "Owner 已明确",
    group: "资产治理",
    done: () => isFilled(state.owner),
  },
  {
    key: "businessDomain",
    label: "业务域已明确",
    group: "资产治理",
    done: () => isFilled(state.businessDomain),
  },
  {
    key: "category",
    label: "分类已明确",
    group: "资产治理",
    done: () => isFilled(state.category),
  },
];

function $(selector) {
  return document.querySelector(selector);
}

function $all(selector) {
  return Array.from(document.querySelectorAll(selector));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function presentText(value, fallback) {
  const text = String(value || "").trim();
  return text.length ? text : fallback;
}

function isFilled(value) {
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  return String(value || "").trim().length > 0;
}

function hasBoundKnowledge() {
  return (
    Array.isArray(state.selectedKnowledgeIds) && state.selectedKnowledgeIds.length > 0
  );
}

function isKnowledgeStateConfirmed() {
  return hasBoundKnowledge() || state.knowledgeMode === "unbound";
}

function knowledgeBoundaryDisplay() {
  if (!hasBoundKnowledge()) {
    return KNOWLEDGE_UNBOUND_MESSAGE;
  }
  return presentText(state.knowledgeBoundary, "待补齐知识边界。");
}

function selectedDataAssets() {
  return dataAssetCatalogState.filter((item) =>
    state.selectedDataAssetIds.includes(item.id),
  );
}

function hasBoundDataAssets() {
  return selectedDataAssets().length > 0;
}

function isDataAssetStateConfirmed() {
  return hasBoundDataAssets() || state.dataAssetMode === "unbound";
}

function dataAssetStateDisplay() {
  if (!hasBoundDataAssets()) {
    return DATA_ASSET_UNBOUND_MESSAGE;
  }
  const assets = selectedDataAssets();
  if (assets.length === 1) {
    return `${assets[0].displayName} 已授权`;
  }
  return `已授权 ${assets.length} 条数据资产`;
}

function isStructuredMode() {
  return state.outputMode === "structured";
}

function isStructuredContractReady() {
  if (!isStructuredMode()) {
    return true;
  }
  return Boolean(outputChoiceMeta[state.outputType]);
}

function outputModeLabel() {
  return outputModeMeta[state.outputMode]?.title || "待定输出方式";
}

function outputTypeLabel() {
  return outputChoiceMeta[state.outputType]?.title || "待定结构化模板";
}

function groupedKnowledgeItems() {
  const selected = knowledgeCatalog.filter((item) =>
    state.selectedKnowledgeIds.includes(item.id),
  );
  return Object.values(
    selected.reduce((acc, item) => {
      if (!acc[item.kbId]) {
        acc[item.kbId] = { kbId: item.kbId, kbName: item.kbName, items: [] };
      }
      acc[item.kbId].items.push(item);
      return acc;
    }, {}),
  );
}

function activeAdminDataAsset() {
  return (
    dataAssetCatalogState.find((item) => item.id === state.activeAdminDataAssetId) ||
    dataAssetCatalogState[0]
  );
}

function touchDraft() {
  if (!state.isPublished) {
    return;
  }
  state.isPublished = false;
  state.logs = [];
}

function markBriefingNeedsRefresh() {
  state.briefingNeedsRefresh = true;
}

function clearBriefingNeedsRefresh() {
  state.briefingNeedsRefresh = false;
}

function buildScenarioDraft() {
  if (state.scenarios.length > 0) {
    return [...new Set(state.scenarios)].slice(0, 5);
  }
  return scenarioSuggestions.slice(0, 3);
}

function buildUsageDraft() {
  const audience = hasBoundKnowledge() ? "角色 owner、消费方或外部 AI 环境" : "消费方或外部 AI 环境";
  const outputHint = isStructuredMode()
    ? `获得 ${outputTypeLabel()} 结果。`
    : "获得自由输出结果。";
  return `面向${audience}使用。调用前应提供业务背景、关键输入和明确问题，平台将按当前角色版本返回${outputHint}`;
}

function buildSupportDraft() {
  const knowledgeHint = hasBoundKnowledge()
    ? `已绑定 ${state.selectedKnowledgeIds.length} 条知识对象`
    : "当前未绑定真实知识";
  const dataHint = hasBoundDataAssets()
    ? `数据能力按当前生效配置读取 ${selectedDataAssets().length} 条数据资产`
    : "当前未授权结构化业务数据";
  const testHint = state.hasTestEvidence
    ? `已有验证摘要 ${state.testSummary}`
    : "当前暂无验证摘要";
  return `${knowledgeHint}；${dataHint}；${testHint}。`;
}

function regenerateBriefingDraft() {
  state.scenarios = buildScenarioDraft();
  state.usageNotes = buildUsageDraft();
  state.supportBasis = buildSupportDraft();
  clearBriefingNeedsRefresh();
  touchDraft();
  syncFieldsFromState();
}

function confirmBriefingText() {
  clearBriefingNeedsRefresh();
  syncDerivedViews();
}

function updateScreen(screen) {
  $all(".screen-chip").forEach((button) => {
    button.classList.toggle("active", button.dataset.screen === screen);
  });
  $all(".screen").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `screen-${screen}`);
  });
  $("#screenTitle").textContent = screenMeta[screen].title;
  $("#screenSubtitle").textContent = screenMeta[screen].subtitle;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function updateStep(step) {
  $all(".chapter-link").forEach((button) => {
    button.classList.toggle("active", button.dataset.step === step);
  });
  $all(".workspace-step").forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.stepPanel === step);
  });
}

function addScenario(rawValue) {
  const value = String(rawValue || "").trim();
  if (!value || state.scenarios.includes(value)) {
    return;
  }
  state.scenarios = [...state.scenarios, value];
  clearBriefingNeedsRefresh();
  touchDraft();
  renderScenarioTags();
  syncDerivedViews();
}

function removeScenario(index) {
  state.scenarios = state.scenarios.filter((_, current) => current !== index);
  clearBriefingNeedsRefresh();
  touchDraft();
  renderScenarioTags();
  syncDerivedViews();
}

function addEnterpriseRoleMapping(rawValue) {
  const value = String(rawValue || "").trim();
  if (!value || state.enterpriseRoleMappings.includes(value)) {
    return;
  }
  state.enterpriseRoleMappings = [...state.enterpriseRoleMappings, value];
  touchDraft();
  renderEnterpriseRoleMappings();
  syncDerivedViews();
}

function removeEnterpriseRoleMapping(index) {
  state.enterpriseRoleMappings = state.enterpriseRoleMappings.filter(
    (_, current) => current !== index,
  );
  touchDraft();
  renderEnterpriseRoleMappings();
  syncDerivedViews();
}

function renderTagEditor(targetId, values, placeholder, onAdd, onRemove) {
  const container = $(targetId);
  container.innerHTML = `
    ${values
      .map(
        (value, index) => `
          <span class="tag-chip">
            ${escapeHtml(value)}
            <button type="button" data-remove-index="${index}" aria-label="移除">×</button>
          </span>
        `,
      )
      .join("")}
    <div class="tag-editor-input">
      <input type="text" placeholder="${escapeHtml(placeholder)}" />
      <button class="tag-add" type="button">添加</button>
    </div>
  `;

  $all(`${targetId} [data-remove-index]`).forEach((button) => {
    button.addEventListener("click", () => onRemove(Number(button.dataset.removeIndex)));
  });

  const input = container.querySelector("input");
  const addButton = container.querySelector(".tag-add");
  const submit = () => {
    onAdd(input.value);
    input.value = "";
    input.focus();
  };
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      submit();
    }
  });
  addButton.addEventListener("click", submit);
}

function renderScenarioTags() {
  renderTagEditor(
    "#scenarioEditor",
    state.scenarios,
    "输入业务阶段/任务",
    addScenario,
    removeScenario,
  );

  const suggestions = $("#scenarioSuggestions");
  suggestions.innerHTML = `
    <span class="suggestion-label">常见场景</span>
    ${scenarioSuggestions
      .map(
        (item) => `
          <button class="suggestion-pill" type="button" data-suggestion="${escapeHtml(item)}">
            ${escapeHtml(item)}
          </button>
        `,
      )
      .join("")}
  `;
  $all("#scenarioSuggestions [data-suggestion]").forEach((button) => {
    button.addEventListener("click", () => addScenario(button.dataset.suggestion));
  });
}

function renderEnterpriseRoleMappings() {
  renderTagEditor(
    "#roleMappingEditor",
    state.enterpriseRoleMappings,
    "输入部门/岗位/职责角色",
    addEnterpriseRoleMapping,
    removeEnterpriseRoleMapping,
  );
}

function renderOutputModeChoices() {
  const container = $("#outputModeChoices");
  container.innerHTML = Object.entries(outputModeMeta)
    .map(
      ([key, meta]) => `
        <button type="button" class="choice-card${state.outputMode === key ? " active" : ""}" data-output-mode="${escapeHtml(key)}">
          <div>
            <strong>${escapeHtml(meta.title)}</strong>
            <p>${escapeHtml(meta.description)}</p>
          </div>
          <span class="token">${state.outputMode === key ? "当前选择" : "切换"}</span>
        </button>
      `,
    )
    .join("");

  $all("[data-output-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      const mode = button.dataset.outputMode;
      if (!mode || state.outputMode === mode) {
        return;
      }
      state.outputMode = mode;
      markBriefingNeedsRefresh();
      touchDraft();
      renderOutputModeChoices();
      renderOutputChoices();
      syncOutputSection();
      syncDerivedViews();
    });
  });
}

function renderOutputChoices() {
  const container = $("#outputChoices");
  container.innerHTML = Object.entries(outputChoiceMeta)
    .map(
      ([key, meta]) => `
        <button type="button" class="choice-card${state.outputType === key ? " active" : ""}" data-output-type="${escapeHtml(key)}">
          <div>
            <strong>${escapeHtml(meta.title)}</strong>
            <small>${escapeHtml(meta.code)}</small>
            <p>${escapeHtml(meta.description)}</p>
          </div>
          <span class="token">${state.outputType === key ? "当前模板" : "切换"}</span>
        </button>
      `,
    )
    .join("");

  $all("[data-output-type]").forEach((button) => {
    button.addEventListener("click", () => {
      const type = button.dataset.outputType;
      if (!type || state.outputType === type) {
        return;
      }
      state.outputType = type;
      markBriefingNeedsRefresh();
      touchDraft();
      renderOutputChoices();
      renderSchemaPreview();
      renderBusinessSchemaPreview();
      syncDerivedViews();
    });
  });
}

function renderSchemaPreview() {
  const preview = $("#schemaPreview");
  if (!isStructuredMode()) {
    preview.innerHTML = `
      <div class="knowledge-empty-inline">
        当前默认自由输出，暂不要求配置结构化模板。
      </div>
    `;
    return;
  }
  const meta = outputChoiceMeta[state.outputType];
  if (!meta) {
    preview.innerHTML = `
      <div class="knowledge-empty-inline">
        请选择结构化输出模板。
      </div>
    `;
    return;
  }
  preview.innerHTML = meta.schema
    .map(
      (item) => `
        <div class="schema-line">
          <strong>${escapeHtml(item.key)}</strong>
          <span>${escapeHtml(item.label)}</span>
        </div>
      `,
    )
    .join("");
}

function renderBusinessSchemaPreview() {
  const preview = $("#businessSchemaPreview");
  if (!isStructuredMode()) {
    preview.innerHTML = `
      <div class="knowledge-empty-inline">
        自由输出路径下，不要求配置角色级 schema 扩展。
      </div>
    `;
    return;
  }
  const meta = outputChoiceMeta[state.outputType];
  if (!meta) {
    preview.innerHTML = `
      <div class="knowledge-empty-inline">
        先选择结构化模板，再展示角色级业务字段扩展。
      </div>
    `;
    return;
  }
  preview.innerHTML = meta.businessFields
    .map(
      (item) => `
        <div class="business-schema-line">
          <strong>业务字段</strong>
          <span>${escapeHtml(item)}</span>
        </div>
      `,
    )
    .join("");
}

function syncOutputSection() {
  const structuredPanel = $("#structuredOutputPanel");
  structuredPanel.style.display = isStructuredMode() ? "grid" : "none";
  $("#outputModeTitle").textContent = isStructuredMode()
    ? `当前走结构化输出 · ${outputTypeLabel()}`
    : "当前默认自由输出";
  $("#outputModeBody").textContent = isStructuredMode()
    ? "当前角色会返回稳定模板结果；消费方应按平台模板和角色级业务字段扩展读取。"
    : "未进入结构化路径时，不要求配置输出类型与 schema；模型绑定仍可在高级区按需覆盖。";
}

function renderSelectedKnowledge() {
  const groups = groupedKnowledgeItems();
  const container = $("#selectedKnowledgeList");

  if (groups.length === 0) {
    container.innerHTML = `
      <div class="knowledge-empty-inline">
        当前已明确为“暂不绑定真实知识”。这是合法状态；消费侧必须如实表达为无知识追溯支撑。
      </div>
    `;
    return;
  }

  container.innerHTML = groups
    .map(
      (group) => `
        <section class="selected-knowledge-card">
          <header>
            <strong>${escapeHtml(group.kbName)}</strong>
            <span>${group.items.length} 条已选</span>
          </header>
          <div class="selected-knowledge-list-inner">
            ${group.items
              .map(
                (item) => `
                  <div>
                    <strong>${escapeHtml(item.title)}</strong>
                    <small>${escapeHtml(item.version)} · ${escapeHtml(item.path)}</small>
                    <span>${escapeHtml(item.summary)}</span>
                  </div>
                `,
              )
              .join("")}
          </div>
        </section>
      `,
    )
    .join("");
}

function renderKnowledgeDialog() {
  const groups = Object.values(
    knowledgeCatalog.reduce((acc, item) => {
      if (!acc[item.kbId]) {
        acc[item.kbId] = { kbId: item.kbId, kbName: item.kbName, items: [] };
      }
      acc[item.kbId].items.push(item);
      return acc;
    }, {}),
  );

  $("#knowledgeDialogCounter").textContent = `已选 ${state.selectedKnowledgeIds.length} 条`;
  $("#knowledgeDialogGrid").innerHTML = groups
    .map(
      (group) => `
        <section class="knowledge-kb-panel">
          <header>
            <strong>${escapeHtml(group.kbName)}</strong>
            <span>${group.items.length} 条可选</span>
          </header>
          <div class="knowledge-kb-list">
            ${group.items
              .map(
                (item) => `
                  <label class="knowledge-item-row">
                    <input type="checkbox" data-knowledge-id="${escapeHtml(item.id)}" ${state.selectedKnowledgeIds.includes(item.id) ? "checked" : ""}>
                    <div>
                      <strong>${escapeHtml(item.title)}</strong>
                      <small>${escapeHtml(item.version)} · ${escapeHtml(item.path)}</small>
                      <span>${escapeHtml(item.summary)}</span>
                    </div>
                  </label>
                `,
              )
              .join("")}
          </div>
        </section>
      `,
    )
    .join("");

  $all("[data-knowledge-id]").forEach((input) => {
    input.addEventListener("change", (event) => {
      const id = event.target.dataset.knowledgeId;
      if (!id) {
        return;
      }
      if (event.target.checked) {
        state.selectedKnowledgeIds = [...state.selectedKnowledgeIds, id];
        state.knowledgeMode = "bound";
      } else {
        state.selectedKnowledgeIds = state.selectedKnowledgeIds.filter(
          (current) => current !== id,
        );
        if (state.selectedKnowledgeIds.length === 0) {
          state.knowledgeMode = "unbound";
          state.knowledgeBoundary = "";
        }
      }
      markBriefingNeedsRefresh();
      touchDraft();
      renderKnowledgeDialog();
      renderSelectedKnowledge();
      syncDerivedViews();
    });
  });
}

function renderSelectedDataAssets() {
  const assets = selectedDataAssets();
  const container = $("#selectedDataAssetList");

  if (assets.length === 0) {
    container.innerHTML = `
      <div class="knowledge-empty-inline">
        当前未授权结构化业务数据。角色仍可成立，但消费侧和外供说明必须如实表达该状态。
      </div>
    `;
    return;
  }

  container.innerHTML = assets
    .map(
      (asset) => `
        <section class="selected-knowledge-card">
          <header>
            <strong>${escapeHtml(asset.displayName)}</strong>
            <span>${asset.status === "active" ? "启用" : "停用"}</span>
          </header>
          <div class="selected-knowledge-list-inner">
            <div>
              <span>${escapeHtml(asset.scopeSummary)}</span>
            </div>
          </div>
        </section>
      `,
    )
    .join("");
}

function renderDataAssetDialog() {
  $("#dataAssetDialogCounter").textContent = `已选 ${state.selectedDataAssetIds.length} 条`;
  $("#dataAssetDialogGrid").innerHTML = dataAssetCatalogState
    .map((asset) => {
      const selected = state.selectedDataAssetIds.includes(asset.id);
      const disabled = asset.status !== "active" && !selected;
      return `
        <label class="knowledge-item-row">
          <input type="checkbox" data-data-asset-id="${escapeHtml(asset.id)}" ${selected ? "checked" : ""} ${disabled ? "disabled" : ""}>
          <div>
            <strong>${escapeHtml(asset.displayName)}</strong>
            <small>${escapeHtml(asset.datasourceRef)} · ${escapeHtml(asset.databaseName)}.${escapeHtml(asset.tableName)}</small>
            <span>${escapeHtml(asset.scopeSummary)}</span>
            <small>${asset.status === "active" ? "启用，可绑定" : "停用，不可新绑定"}</small>
          </div>
        </label>
      `;
    })
    .join("");

  $all("[data-data-asset-id]").forEach((input) => {
    input.addEventListener("change", (event) => {
      const id = event.target.dataset.dataAssetId;
      if (!id) {
        return;
      }
      if (event.target.checked) {
        if (!state.selectedDataAssetIds.includes(id)) {
          state.selectedDataAssetIds = [...state.selectedDataAssetIds, id];
        }
        state.dataAssetMode = "bound";
      } else {
        state.selectedDataAssetIds = state.selectedDataAssetIds.filter(
          (current) => current !== id,
        );
        if (state.selectedDataAssetIds.length === 0) {
          state.dataAssetMode = "unbound";
        }
      }
      markBriefingNeedsRefresh();
      touchDraft();
      renderDataAssetDialog();
      renderSelectedDataAssets();
      syncDerivedViews();
    });
  });
}

function renderAdminDataAssetList() {
  const container = $("#dataAssetAdminList");
  container.innerHTML = dataAssetCatalogState
    .map(
      (asset) => `
        <button type="button" class="choice-card${state.activeAdminDataAssetId === asset.id ? " active" : ""}" data-admin-asset="${escapeHtml(asset.id)}">
          <div>
            <strong>${escapeHtml(asset.displayName)}</strong>
            <small>${escapeHtml(asset.datasourceRef)}</small>
            <p>${escapeHtml(asset.scopeSummary)}</p>
          </div>
          <span class="token">${asset.status === "active" ? "启用" : "停用"}</span>
        </button>
      `,
    )
    .join("");

  $all("[data-admin-asset]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeAdminDataAssetId = button.dataset.adminAsset;
      renderAdminDataAssetList();
      syncAdminAssetEditor();
    });
  });
}

function syncAdminAssetEditor() {
  const asset = activeAdminDataAsset();
  $("#dataAssetEditorTitle").textContent = asset.displayName;
  $("#data-asset-display-name").value = asset.displayName;
  $("#data-asset-datasource-ref").value = asset.datasourceRef;
  $("#data-asset-database-name").value = asset.databaseName;
  $("#data-asset-table-name").value = asset.tableName;
  $("#data-asset-freshness").value = asset.freshness || "";
  $("#data-asset-owner-team").value = asset.ownerTeam || "";
  $("#data-asset-scope-summary").value = asset.scopeSummary;
  $("#data-asset-status").value = asset.status;
}

function updateAdminAssetField(field, value) {
  const asset = activeAdminDataAsset();
  if (!asset || asset[field] === value) {
    return;
  }
  asset[field] = value;
  if (
    state.selectedDataAssetIds.includes(asset.id) &&
    ["displayName", "scopeSummary", "status"].includes(field)
  ) {
    markBriefingNeedsRefresh();
  }
  renderAdminDataAssetList();
  renderDataAssetDialog();
  renderSelectedDataAssets();
  syncAdminAssetEditor();
  syncDerivedViews();
}

function getStatusList(items) {
  return items.map((item) => ({
    ...item,
    satisfied: item.done(),
  }));
}

function getBaselineStatus() {
  return getStatusList(baselineRequirementMap);
}

function getAddedStatus() {
  return getStatusList(addedRequirementMap);
}

function getDefinitionStatus() {
  return getStatusList(definitionRequirementMap);
}

function getContractStatus() {
  return getStatusList(contractRequirementMap);
}

function getGovernanceStatus() {
  return getStatusList(governanceRequirementMap);
}

function getSoftStatus() {
  return getStatusList(softRequirementMap);
}

function getPublishHardStatus() {
  return [
    ...getBaselineStatus(),
    ...getAddedStatus(),
    ...getGovernanceStatus(),
  ];
}

function getStageStatus() {
  const draftReady =
    isFilled(state.name) && isFilled(state.bio) && isFilled(state.mainDuty);
  const briefingReady =
    draftReady &&
    Array.isArray(state.scenarios) &&
    state.scenarios.length > 0 &&
    isFilled(state.usageNotes) &&
    isFilled(state.supportBasis);
  const validationReady =
    briefingReady &&
    isKnowledgeStateConfirmed() &&
    isDataAssetStateConfirmed() &&
    isFilled(state.outputMode) &&
    isStructuredContractReady() &&
    Boolean(state.hasTestEvidence);
  const governanceReady =
    validationReady &&
    isFilled(state.owner) &&
    isFilled(state.businessDomain) &&
    isFilled(state.category) &&
    !state.briefingNeedsRefresh;
  const reuseReady = governanceReady && state.isPublished;

  return [
    { ...stageMeta[0], satisfied: draftReady },
    { ...stageMeta[1], satisfied: briefingReady },
    { ...stageMeta[2], satisfied: validationReady },
    { ...stageMeta[3], satisfied: governanceReady },
    { ...stageMeta[4], satisfied: reuseReady },
  ];
}

function getCurrentStageGuidance() {
  const stages = getStageStatus();
  if (!stages[0].satisfied) {
    return "当前应先完成角色本体最小骨架：名称、摘要和核心职责。治理字段还不需要一次性压满。";
  }
  if (!stages[1].satisfied) {
    return "当前已可形成 draft，下一步应补齐使用前说明，让别人先看懂这个角色适合干什么、怎么用、为什么可信。";
  }
  if (!stages[2].satisfied) {
    return "当前已完成角色定义和说明卡，下一步应进入试用与测试，先验证当前版本是否真的能跑起来。";
  }
  if (!stages[3].satisfied) {
    return "当前测试已通过，下一步应在治理与发布页补齐 Owner、业务域和分类，并确认说明卡仍是当前保存版。";
  }
  if (!stages[4].satisfied) {
    return "当前已闭合治理与发布准备，下一步应发布当前版本，然后进入正式消费或外供与追溯。";
  }
  return "当前角色已进入发布后复用阶段，可在平台内正式消费，也可生成外供物并继续回写追溯。";
}

function getFirstGapTarget() {
  const gap = getPublishHardStatus().find((item) => !item.satisfied);
  if (!gap) {
    return { screen: "workspace", step: "identity" };
  }
  return routeByRequirement[gap.key] || { screen: "workspace", step: "identity" };
}

function renderStatusList(items, targetId) {
  $(targetId).innerHTML = items
    .map(
      (item) => `
        <li>
          <span class="status-state ${item.satisfied ? "complete" : "pending"}">${item.satisfied ? "✓" : "!"}</span>
          <div>
            <strong>${escapeHtml(item.label)}</strong>
            <small>${escapeHtml(item.group)} · ${item.satisfied ? "已满足" : "仍需补齐"}</small>
          </div>
        </li>
      `,
    )
    .join("");
}

function renderStageList(targetId) {
  const target = $(targetId);
  const compact = targetId === "#stageJourney";
  target.innerHTML = getStageStatus()
    .map(
      (stage, index) => `
        <article class="stage-item ${compact ? "compact" : ""} ${stage.satisfied ? "complete" : ""}">
          <div class="stage-item-index">${index + 1}</div>
          <div>
            <strong>${escapeHtml(stage.title)}</strong>
            <small>${escapeHtml(compact ? (stage.satisfied ? "已就绪" : "待补齐") : stage.description)}</small>
          </div>
          ${compact ? "" : `<span class="stage-item-state">${stage.satisfied ? "已就绪" : "待补齐"}</span>`}
        </article>
      `,
    )
    .join("");
}

function syncProgressPanel() {
  const progressItems = [
    ...getDefinitionStatus(),
    ...getContractStatus(),
    ...getGovernanceStatus(),
  ];
  const doneCount = progressItems.filter((item) => item.satisfied).length;
  const progress = Math.round((doneCount / progressItems.length) * 100);

  $("#progressPercent").textContent = `${progress}%`;
  $("#donutMeter").style.strokeDasharray = `${progress} ${100 - progress}`;

  renderStatusList(getDefinitionStatus(), "#definitionRequirements");
  renderStatusList(getContractStatus(), "#contractRequirements");
  renderStatusList(getGovernanceStatus(), "#governanceRequirements");
  $("#softRequirements").innerHTML = getSoftStatus()
    .map(
      (item) => `
        <li>
          <span class="status-state ${item.satisfied ? "complete" : "soft"}">${item.satisfied ? "✓" : "i"}</span>
          <div>
            <strong>${escapeHtml(item.label)}</strong>
            <small>${item.satisfied ? "已补齐" : "建议补齐但不阻断"}</small>
          </div>
        </li>
      `,
    )
    .join("");
  renderStageList("#stageJourney");
  renderStageList("#summaryStageBoard");
  $("#stageGuidance").textContent = getCurrentStageGuidance();
  $("#summaryStageGuidance").textContent = getCurrentStageGuidance();
}

function syncPublishPanel() {
  const baseline = getBaselineStatus();
  const added = getAddedStatus();
  const governance = getGovernanceStatus();
  const soft = getSoftStatus();

  renderStatusList(baseline, "#publishBaselineList");
  renderStatusList(added, "#publishAddedList");
  renderStatusList(governance, "#publishGovernanceList");
  $("#publishSoftList").innerHTML = soft
    .map(
      (item) => `
        <li>
          <span class="status-state ${item.satisfied ? "complete" : "soft"}">${item.satisfied ? "✓" : "i"}</span>
          <div>
            <strong>${escapeHtml(item.label)}</strong>
            <small>${item.satisfied ? "已补齐" : "建议补齐但不阻断"}</small>
          </div>
        </li>
      `,
    )
    .join("");

  const blocker = getPublishHardStatus().find((item) => !item.satisfied);
  const publishButton = $("#publishButton");
  const publishState = $("#publishState");

  if (blocker) {
    publishButton.disabled = true;
    publishButton.textContent = "发布当前版本";
    publishState.className = "pill pill-danger";
    publishState.textContent = "当前阻断";
    $("#blockerReason").textContent = `当前角色尚未满足“${blocker.label}”，不能作为可复用资产发布。`;
    return;
  }

  publishButton.disabled = false;
  if (state.isPublished) {
    publishButton.textContent = "查看已发布版本外供";
    publishState.className = "pill pill-success";
    publishState.textContent = "已发布";
    $("#blockerReason").textContent =
      "当前工作副本已同时满足 v0.4 基线门禁、v0.5 补充要求和治理最小项，可按现有机制继续外供。";
    return;
  }

  publishButton.textContent = "发布当前版本";
  publishState.className = "pill pill-success";
  publishState.textContent = "可以发布";
  $("#blockerReason").textContent =
    "当前角色已满足 v0.4 基线门禁、v0.5 补充门禁和治理最小项，可在现有发布机制上继续发布。";
}

function syncKnowledgeStats() {
  const selectedItems = knowledgeCatalog.filter((item) =>
    state.selectedKnowledgeIds.includes(item.id),
  );
  const uniqueKbIds = new Set(selectedItems.map((item) => item.kbId));
  $("#knowledgeCountCard").textContent = hasBoundKnowledge()
    ? `已绑定 ${selectedItems.length} 条`
    : "暂不绑定";
  $("#knowledgeBaseCard").textContent = hasBoundKnowledge()
    ? Array.from(uniqueKbIds).join(" / ")
    : "当前未绑定真实知识";
  $("#testScoreCard").textContent = state.testScore;
  $("#testRecordCard").textContent = state.testSummary;
  $("#trustOutputTypeCard").textContent = isStructuredMode()
    ? outputTypeLabel()
    : outputModeLabel();
  $("#selectedKnowledgeCount").textContent = String(selectedItems.length);
  $("#selectedKbCount").textContent = String(uniqueKbIds.size);
  $("#selectedKnowledgeVersionState").textContent = selectedItems.length
    ? `${selectedItems.length} / ${selectedItems.length}`
    : "未生成";

  const knowledgeField = $("#field-kb");
  knowledgeField.disabled = !hasBoundKnowledge();
  if (!hasBoundKnowledge()) {
    knowledgeField.value = "";
  }
  $("#knowledgeBoundaryHelp").textContent = hasBoundKnowledge()
    ? "说明知识覆盖范围；应在完成知识绑定后再确认。"
    : "无知识绑定时不要求填写；系统会在消费侧明确显示“未绑定真实知识”。";
  $("#knowledgeCalloutTitle").textContent = hasBoundKnowledge()
    ? "先绑定，再确认边界"
    : "暂不绑定也合法";
  $("#knowledgeCalloutBody").textContent = hasBoundKnowledge()
    ? "知识边界应优先根据已绑定知识生成模板化初稿，再由用户补齐不覆盖范围。"
    : "知识绑定是可选增强。当前可以不绑定真实知识，但不能把这个角色误表述成有知识追溯支撑。";
  $("#knowledgePanelCopy").textContent = hasBoundKnowledge()
    ? "这里必须保留真实的知识绑定入口。v0.5 可以重做理解路径，但不能把已有的知识库绑定能力从角色定义主链拿掉。"
    : "这里仍保留真实的知识绑定入口；如果当前阶段不需要知识，也可以明确保持“暂不绑定真实知识”，稍后再补。";
}

function syncDataAssetPanel() {
  const assets = selectedDataAssets();
  $("#dataCapabilityStateCard").textContent = hasBoundDataAssets()
    ? "已授权"
    : "未授权";
  $("#dataCapabilitySummaryCard").textContent = dataAssetStateDisplay();
  $("#selectedDataAssetCount").textContent = String(assets.length);
  $("#dataAssetCalloutTitle").textContent = hasBoundDataAssets()
    ? "当前已授权结构化业务数据"
    : "未授权也是合法状态";
  $("#dataAssetCalloutBody").textContent = hasBoundDataAssets()
    ? "当前角色版本会通过平台服务端查询层使用这些数据资产；外部平台不会直接拿到底层连接。"
    : "当前不要求每个角色都绑定结构化业务数据。若未绑定，消费侧必须如实表达“当前未授权结构化业务数据”。";
  $("#dataAssetPanelCopy").textContent = hasBoundDataAssets()
    ? "这里展示当前角色版本已绑定的数据资产。若要新增或修改数据资产本身，请前往治理侧管理员页面维护。"
    : "当前角色页只绑定已配置的数据资产项，不现场填写数据库连接、账号密钥或 SQL 细节。";
}

function syncBriefingCard() {
  $("#briefingName").textContent = presentText(state.name, "未命名角色");
  $("#briefingStatus").textContent = state.isPublished
    ? `已发布 ${ROLE_SNAPSHOT_META.versionLabel}`
    : "草稿预演";
  $("#briefingKnowledgeState").textContent = hasBoundKnowledge()
    ? `知识已绑定 ${state.selectedKnowledgeIds.length} 条`
    : "未绑定真实知识";
  $("#briefingDataState").textContent = hasBoundDataAssets()
    ? `数据已授权 ${selectedDataAssets().length} 条`
    : "未授权结构化业务数据";
  $("#briefingOutputMode").textContent = outputModeLabel();
  $("#briefingSummary").textContent = presentText(
    state.usageNotes,
    "这页不定义角色本体，而定义别人怎么正确地选择、理解和调用这个角色。",
  );
  $("#briefingRefreshTitle").textContent = state.briefingNeedsRefresh
    ? "说明卡待确认更新"
    : "说明卡当前已确认";
  $("#briefingRefreshBody").textContent = state.briefingNeedsRefresh
    ? "角色来源已经变化。请根据最新角色信息重生成说明卡，或确认沿用当前文字后再发布 / 外供。"
    : "当前保存版会被使用台、测试台和外供包直接复用。";
  $("#briefingBio").textContent = presentText(state.bio, "待补齐一句话摘要。");
  $("#briefingDuty").textContent = presentText(
    state.mainDuty,
    "待补齐核心职责。",
  );
  $("#briefingScenarios").textContent = state.scenarios.length
    ? state.scenarios.join(" / ")
    : "待补齐适用场景";
  $("#briefingUsage").textContent = presentText(
    state.usageNotes,
    "待补齐使用说明，当前还不能让调用方正确选择和使用这个角色。",
  );
  $("#briefingCurrentRule").textContent = state.briefingNeedsRefresh
    ? "当前仍沿用上一次已保存说明；未重新确认前，不得发布 / 外供。"
    : "当前保存版已生效；后续若来源变化，将再次提示重新确认。";
  $("#briefingSupport").textContent = presentText(
    state.supportBasis,
    "待补齐可信依据摘要。",
  );
  $("#briefingKnowledgeMetric").textContent = hasBoundKnowledge()
    ? `${state.selectedKnowledgeIds.length} 条`
    : "未绑定";
  $("#briefingKnowledgeLabel").textContent = hasBoundKnowledge()
    ? "知识绑定"
    : "真实知识";
  $("#briefingDataMetric").textContent = hasBoundDataAssets()
    ? `${selectedDataAssets().length} 条`
    : "未授权";
  $("#briefingDataLabel").textContent = hasBoundDataAssets()
    ? "数据资产"
    : "数据能力";
  $("#briefingOutputMetric").textContent = isStructuredMode()
    ? `结构化 · ${outputTypeLabel()}`
    : outputModeLabel();
  $("#briefingKb").textContent = knowledgeBoundaryDisplay();
  $("#briefingData").textContent = hasBoundDataAssets()
    ? selectedDataAssets()
        .map((asset) => `${asset.displayName}（${asset.scopeSummary}）`)
        .join("；")
    : DATA_ASSET_UNBOUND_MESSAGE;
  $("#briefingOutput").textContent = isStructuredMode()
    ? `默认结构化输出：${outputTypeLabel()}。消费方应按平台模板读取结果。`
    : "默认自由输出；若后续切到结构化输出，应按模板消费结果。";
}

function buildPackageFiles() {
  const baseFiles = [
    {
      name: "package-manifest.json",
      desc: "固定包类型、角色身份和生成时点，不允许由接入方手工再拼核心契约。",
    },
    {
      name: "role-brief.md",
      desc: "复用说明卡当前保存版，包含核心职责、场景、怎么用、为什么可信。",
    },
    {
      name: "consume-contract.json",
      desc: "绑定 role_id / role_version_id 的调用契约与响应语义。",
    },
    {
      name: "output-contract.json",
      desc: isStructuredMode()
        ? `输出方式为 structured，默认模板为 ${outputTypeLabel()}。`
        : "输出方式为 freeform，不要求结构化模板。",
    },
    {
      name: "writeback-policy.md",
      desc: "约束外部调用后继续形成 usage_record 的回写说明。",
    },
  ];

  if (state.packageMode === "tool") {
    return [
      {
        name: "tool-manifest.json",
        desc: "Tool 形态入口定义；接入方只补环境配置即可调用。",
      },
      ...baseFiles,
    ];
  }

  return [
    {
      name: "SKILL.md",
      desc: "Skill 形态入口说明；接入方只补环境配置即可调用。",
    },
    ...baseFiles,
  ];
}

function syncPackagePanel() {
  const isTool = state.packageMode === "tool";
  $("#packageTitle").textContent = `${presentText(state.name, "未命名角色")} ${
    isTool ? "Tool Package" : "Skill Package"
  }`;
  $("#packageDuty").textContent = presentText(
    state.mainDuty,
    "待补齐核心职责",
  );
  $("#packageScenarios").textContent = state.scenarios.length
    ? state.scenarios.join(" / ")
    : "待补齐适用场景";
  $("#packageUsage").textContent = presentText(
    state.usageNotes,
    "待补齐使用说明",
  );
  $("#packageSupport").textContent = presentText(
    state.supportBasis,
    "待补齐可信依据",
  );
  $("#packageSummary").textContent = state.isPublished
    ? `面向${isTool ? "开放 Agent 平台" : "技能型 AI 环境"}，以稳定供给物方式复用该角色，并持续写回 usage_record。`
    : "当前只展示供给物结构预演；必须先通过发布门禁，才能真正绑定到单个已发布角色版本。";
  $("#packageSourceState").textContent = state.isPublished
    ? "published role version"
    : "draft preview only";
  $("#packageContract").textContent = `POST /role-assets/{role_id}/consume
role_version_id=${ROLE_SNAPSHOT_META.roleVersionId}
caller_type=${isTool ? "agent_platform" : "system"}

response:
- output_mode
- structured_result
- status
- boundary_status
- usage_record`;

  const banner = $("#packageStateBanner");
  if (state.isPublished) {
    banner.className = "package-state-banner ready";
    $("#packageBannerTitle").textContent = "当前已绑定到已发布角色版本";
    $("#packageBannerBody").textContent =
      "供给物绑定单个已发布版本，不漂向最新版本，并继续回写使用记录。数据能力按当前生效配置运行。";
    $("#packageGoPublish").hidden = true;
  } else {
    banner.className = "package-state-banner";
    $("#packageBannerTitle").textContent = "当前还是草稿预演";
    $("#packageBannerBody").textContent =
      "必须先完成发布门禁，供给物才成立。否则这里只能用于设计评审。";
    $("#packageGoPublish").hidden = false;
  }
  $("#packageDataPolicy").textContent = state.briefingNeedsRefresh
    ? "说明或数据摘要来源已变化。当前包需要重新生成后再对外分发。"
    : "当前外供冻结身份、说明卡和调用契约；数据能力按管理员当前生效配置运行，不承诺版本冻结复现。";

  const simulateButton = $("#simulateExternalUse");
  simulateButton.disabled = !state.isPublished;
  simulateButton.textContent = state.isPublished ? "模拟一次外部调用" : "需先完成发布";

  $("#packageFiles").innerHTML = buildPackageFiles()
    .map(
      (item) => `
        <li>
          <strong>${escapeHtml(item.name)}</strong>
          <span>${escapeHtml(item.desc)}</span>
        </li>
      `,
    )
    .join("");
}

function syncLogStream() {
  const container = $("#writebackLog");
  if (!state.isPublished) {
    container.innerHTML = `
      <div class="log-item">
        <strong>发布前不生成正式回写链</strong>
        <span>当前仍是草稿预演。只有绑定到已发布角色版本后，外部调用才应回写 usage_record。</span>
      </div>
    `;
    return;
  }

  if (state.logs.length === 0) {
    container.innerHTML = `
      <div class="log-item">
        <strong>等待外部调用</strong>
        <span>调用后平台侧必须继续形成 usage_record，并保留身份、版本、状态和边界语义。</span>
      </div>
    `;
    return;
  }

  container.innerHTML = state.logs
    .map(
      (log) => `
        <div class="log-item">
          <strong>${escapeHtml(log.title)}</strong>
          <span>${escapeHtml(log.body)}</span>
        </div>
      `,
    )
    .join("");
}

function syncFieldsFromState() {
  const mapping = {
    "#field-intent-description": state.intentDescription,
    "#field-name": state.name,
    "#field-bio": state.bio,
    "#field-duty": state.mainDuty,
    "#field-tags": state.tags,
    "#field-owner": state.owner,
    "#field-maintainer": state.maintainer,
    "#field-domain": state.businessDomain,
    "#field-identity-background": state.identityBackground,
    "#field-point-of-view": state.pointOfView,
    "#field-speaking-style": state.speakingStyle,
    "#field-usage": state.usageNotes,
    "#field-support": state.supportBasis,
    "#field-kb": state.knowledgeBoundary,
    "#field-model-provider": state.modelProvider,
    "#field-model-name": state.modelName,
    "#field-temperature": state.temperature,
    "#field-max-tokens": state.maxTokens,
  };

  Object.entries(mapping).forEach(([selector, value]) => {
    const element = $(selector);
    if (element) {
      element.value = value;
    }
  });

  $("#field-category").value = state.category;
  $("#field-visibility").value = state.visibility;
  $("#field-decision-style").value = state.decisionStyle;
  $("#draftIntentTextarea").value = state.intentDescription;

  $all(".toggle-pill[data-mode]").forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === state.mode);
  });
  $("#draftButton").textContent =
    state.mode === "ai" ? "套用 AI 草案" : "查看 AI 草案预演";
  $all(".toggle-pill[data-package-mode]").forEach((button) => {
    button.classList.toggle(
      "active",
      button.dataset.packageMode === state.packageMode,
    );
  });

  renderScenarioTags();
  renderEnterpriseRoleMappings();
  renderOutputModeChoices();
  renderOutputChoices();
  renderSchemaPreview();
  renderBusinessSchemaPreview();
  renderSelectedKnowledge();
  renderKnowledgeDialog();
  renderSelectedDataAssets();
  renderDataAssetDialog();
  renderAdminDataAssetList();
  syncAdminAssetEditor();
  syncOutputSection();
  syncDerivedViews();
}

function syncDerivedViews() {
  syncProgressPanel();
  syncPublishPanel();
  syncKnowledgeStats();
  syncDataAssetPanel();
  syncBriefingCard();
  syncPackagePanel();
  syncLogStream();
}

function updateField(key, value) {
  if (state[key] === value) {
    return;
  }
  state[key] = value;
  if (BRIEFING_SOURCE_FIELDS.has(key)) {
    markBriefingNeedsRefresh();
  }
  if (key === "usageNotes" || key === "supportBasis") {
    clearBriefingNeedsRefresh();
  }
  touchDraft();
  syncDerivedViews();
}

function bindFieldListeners() {
  [
    ["#field-intent-description", "intentDescription"],
    ["#field-name", "name"],
    ["#field-bio", "bio"],
    ["#field-duty", "mainDuty"],
    ["#field-tags", "tags"],
    ["#field-owner", "owner"],
    ["#field-maintainer", "maintainer"],
    ["#field-domain", "businessDomain"],
    ["#field-identity-background", "identityBackground"],
    ["#field-point-of-view", "pointOfView"],
    ["#field-speaking-style", "speakingStyle"],
    ["#field-usage", "usageNotes"],
    ["#field-support", "supportBasis"],
    ["#field-kb", "knowledgeBoundary"],
    ["#field-model-provider", "modelProvider"],
    ["#field-model-name", "modelName"],
    ["#field-temperature", "temperature"],
    ["#field-max-tokens", "maxTokens"],
  ].forEach(([selector, key]) => {
    $(selector).addEventListener("input", (event) =>
      updateField(key, event.target.value),
    );
  });

  [
    ["#field-category", "category"],
    ["#field-visibility", "visibility"],
    ["#field-decision-style", "decisionStyle"],
  ].forEach(([selector, key]) => {
    $(selector).addEventListener("change", (event) =>
      updateField(key, event.target.value),
    );
  });

  [
    ["#data-asset-display-name", "displayName"],
    ["#data-asset-datasource-ref", "datasourceRef"],
    ["#data-asset-database-name", "databaseName"],
    ["#data-asset-table-name", "tableName"],
    ["#data-asset-freshness", "freshness"],
    ["#data-asset-owner-team", "ownerTeam"],
    ["#data-asset-scope-summary", "scopeSummary"],
  ].forEach(([selector, field]) => {
    $(selector).addEventListener("input", (event) =>
      updateAdminAssetField(field, event.target.value),
    );
  });

  $("#data-asset-status").addEventListener("change", (event) => {
    updateAdminAssetField("status", event.target.value);
  });
}

function applyState(source) {
  Object.assign(state, structuredClone(source));
  state.logs = [];
  state.briefingNeedsRefresh = Boolean(source.briefingNeedsRefresh);
  syncFieldsFromState();
}

function openDraftDialog() {
  $("#draftIntentTextarea").value = state.intentDescription;
  $("#draftDialog").showModal();
}

function closeDraftDialog() {
  if ($("#draftDialog").open) {
    $("#draftDialog").close();
  }
}

function openKnowledgeDialog() {
  renderKnowledgeDialog();
  $("#knowledgeDialog").showModal();
}

function closeKnowledgeDialog() {
  if ($("#knowledgeDialog").open) {
    $("#knowledgeDialog").close();
  }
}

function openDataAssetDialog() {
  renderDataAssetDialog();
  $("#dataAssetDialog").showModal();
}

function closeDataAssetDialog() {
  if ($("#dataAssetDialog").open) {
    $("#dataAssetDialog").close();
  }
}

function simulateExternalUse() {
  if (!state.isPublished) {
    return;
  }
  const modeLabel =
    state.packageMode === "tool" ? "Tool package" : "Skill package";
  state.logs.unshift({
    title: `${modeLabel} 已调用`,
    body: `平台侧继续写入 usage_record，绑定 ${ROLE_SNAPSHOT_META.roleId} / ${ROLE_SNAPSHOT_META.roleVersionId}，保留 output_mode、status 和 boundary_status。`,
  });
  syncLogStream();
}

function publishCurrentVersion() {
  const blocker = getPublishHardStatus().find((item) => !item.satisfied);
  if (blocker) {
    return;
  }
  if (!state.isPublished) {
    state.isPublished = true;
    state.logs = [];
    syncDerivedViews();
  }
  updateScreen("package");
}

function initNavigation() {
  $all(".screen-chip").forEach((button) => {
    button.addEventListener("click", () => updateScreen(button.dataset.screen));
  });
  $all("[data-screen-jump]").forEach((button) => {
    button.addEventListener("click", () =>
      updateScreen(button.dataset.screenJump),
    );
  });
  $all(".chapter-link").forEach((button) => {
    button.addEventListener("click", () => updateStep(button.dataset.step));
  });
}

function initModeToggles() {
  $all(".toggle-pill[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      $all(".toggle-pill[data-mode]").forEach((item) => {
        item.classList.toggle("active", item === button);
      });
      $("#draftButton").textContent =
        state.mode === "ai" ? "套用 AI 草案" : "查看 AI 草案预演";
    });
  });

  $all(".toggle-pill[data-package-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.packageMode = button.dataset.packageMode;
      $all(".toggle-pill[data-package-mode]").forEach((item) => {
        item.classList.toggle("active", item === button);
      });
      syncPackagePanel();
      syncLogStream();
    });
  });
}

function initDialogControls() {
  $("#draftButton").addEventListener("click", openDraftDialog);
  $("#openDraftFromStarter").addEventListener("click", openDraftDialog);
  $("#switchToManualMode").addEventListener("click", () => {
    state.mode = "manual";
    $all(".toggle-pill[data-mode]").forEach((item) => {
      item.classList.toggle("active", item.dataset.mode === "manual");
    });
    $("#draftButton").textContent = "查看 AI 草案预演";
  });
  $("#closeDraftDialog").addEventListener("click", closeDraftDialog);
  $("#closeDraftSecondary").addEventListener("click", closeDraftDialog);
  $("#draftIntentTextarea").addEventListener("input", (event) => {
    state.intentDescription = event.target.value;
    $("#field-intent-description").value = state.intentDescription;
  });
  $("#insertDraft").addEventListener("click", () => {
    aiDraftState.intentDescription = $("#draftIntentTextarea").value;
    applyState(aiDraftState);
    closeDraftDialog();
    updateScreen("workspace");
    updateStep("identity");
  });
  $("#resetButton").addEventListener("click", () => {
    applyState(manualState);
    updateScreen("workspace");
    updateStep("identity");
  });

  $("#openKnowledgeDialog").addEventListener("click", openKnowledgeDialog);
  $("#closeKnowledgeDialog").addEventListener("click", closeKnowledgeDialog);
  $("#confirmKnowledgeSelection").addEventListener(
    "click",
    closeKnowledgeDialog,
  );
  $("#clearKnowledgeSelection").addEventListener("click", () => {
    state.knowledgeMode = "unbound";
    state.selectedKnowledgeIds = [];
    state.knowledgeBoundary = "";
    markBriefingNeedsRefresh();
    touchDraft();
    renderKnowledgeDialog();
    renderSelectedKnowledge();
    syncDerivedViews();
  });

  $("#openDataAssetDialog").addEventListener("click", openDataAssetDialog);
  $("#closeDataAssetDialog").addEventListener("click", closeDataAssetDialog);
  $("#confirmDataAssetSelection").addEventListener(
    "click",
    closeDataAssetDialog,
  );
  $("#clearDataAssetSelection").addEventListener("click", () => {
    state.dataAssetMode = "unbound";
    state.selectedDataAssetIds = [];
    markBriefingNeedsRefresh();
    touchDraft();
    renderDataAssetDialog();
    renderSelectedDataAssets();
    syncDerivedViews();
  });
  $("#regenerateBriefing").addEventListener("click", regenerateBriefingDraft);
  $("#confirmBriefing").addEventListener("click", confirmBriefingText);
}

function initPublishControls() {
  $("#publishButton").addEventListener("click", publishCurrentVersion);
  $("#returnToGap").addEventListener("click", () => {
    const target = getFirstGapTarget();
    updateScreen(target.screen);
    if (target.step) {
      updateStep(target.step);
    }
  });
  $("#packageGoPublish").addEventListener("click", () =>
    updateScreen("publish"),
  );
}

function init() {
  initNavigation();
  initModeToggles();
  initDialogControls();
  initPublishControls();
  bindFieldListeners();
  $("#simulateExternalUse").addEventListener("click", simulateExternalUse);
  applyState(manualState);
  updateScreen("workspace");
  updateStep("identity");
}

init();
