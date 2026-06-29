const BASE = '';
const TOKEN_KEY = 'virtual_actor_token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(url: string, opts?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(BASE + url, { ...opts, headers: { ...headers, ...(opts?.headers || {}) } });
  if (!response.ok) {
    const err = await response.json().catch(() => ({})) as { detail?: string };
    throw new Error(err.detail || `HTTP ${response.status}`);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export interface User {
  username: string;
}

export type OutputMode = 'freeform' | 'structured';
export type RoleStatus = 'draft' | 'test' | 'published' | 'archived';
export type BriefingStatus = 'missing' | 'fresh' | 'stale';

export interface ModelBinding {
  model_provider?: string | null;
  model_name?: string | null;
  temperature: number;
  max_tokens: number;
  fallback_enabled?: boolean;
  inherited?: boolean;
}

export interface KnowledgeRef {
  id: string;
  role_id: string;
  kb_id: string;
  knowledge_object_id: string;
  knowledge_version_id: string | null;
  title?: string | null;
  type?: string | null;
  knowledge_source?: string;
  bound_at?: string | null;
}

export interface KnowledgeBaseItem {
  kb_id: string;
  name: string;
}

export interface KnowledgeItem {
  kb_id: string;
  knowledge_object_id: string;
  knowledge_version_id: string | null;
  title: string;
  type?: string | null;
  tags: string[];
  summary: string;
  source_id?: string | null;
}

export interface KnowledgeBindingInput {
  kb_id: string | null;
  knowledge_object_id: string;
  knowledge_version_id?: string | null;
  title?: string | null;
  type?: string | null;
}

export interface DataAssetSummary {
  id: string;
  display_name: string;
  datasource_ref: string;
  database_name: string;
  table_name: string;
  scope_summary: string;
  freshness?: string | null;
  owner_team?: string | null;
  status: string;
}

export interface StatusSummary {
  state: string;
  label: string;
  detail: string;
}

export interface ValidationSummary {
  has_record: boolean;
  latest_status: string | null;
  latest_tested_at: string | null;
  total_count: number;
}

export interface OutputPreview {
  output_mode: OutputMode;
  output_type: string | null;
  summary: string;
  schema_preview: Record<string, unknown> | null;
}

export interface RoleBriefingView {
  status: BriefingStatus;
  applicable_scenarios: string[];
  usage_notes: string;
  support_basis_summary: string;
  knowledge_status: StatusSummary;
  data_capability_status: StatusSummary;
  validation_summary: ValidationSummary;
  output_preview: OutputPreview;
  source_hint: string;
  source_changed: boolean;
  saved_at: string | null;
}

export interface ProgressItem {
  key: string;
  label: string;
  state: string;
  detail: string;
}

export interface RequirementItem {
  key: string;
  label: string;
  status: string;
  message: string;
  route_screen: string | null;
  route_step: string | null;
}

export interface ReadinessPanel {
  stage: string;
  ready: boolean;
  hard_requirements: RequirementItem[];
  soft_hints: RequirementItem[];
}

export interface LegacyInfo {
  is_legacy: boolean;
  missing_requirements: string[];
  legacy_fields: Record<string, unknown>;
}

export interface RoleListItem {
  role_id: string;
  role_version_id: string | null;
  published_version_id: string | null;
  role_name: string;
  bio: string;
  tags: string[];
  status: RoleStatus;
  summary: string;
  model_binding: ModelBinding | null;
  has_test_record: boolean;
  latest_test_rating: number | null;
  latest_tested_at: string | null;
  test_run_count: number;
  updated_at: string | null;
  category: string;
  owner: string;
  visibility: string;
  business_domain: string | null;
  creation_source: string;
  output_mode: OutputMode;
  output_type: string | null;
  briefing_status: BriefingStatus;
  recommend_pool_eligible: boolean;
  legacy_incomplete: boolean;
}

export interface RoleDetail {
  role_id: string;
  role_version_id: string | null;
  published_version_id: string | null;
  name: string;
  bio: string;
  tags: string[];
  status: RoleStatus;
  category: string;
  owner: string;
  maintainer: string | null;
  business_domain: string | null;
  visibility: string;
  creation_source: string;
  enterprise_role_mapping: string[];
  main_duty_cluster: string | null;
  point_of_view: string | null;
  decision_style: string | null;
  identity_background: string | null;
  speaking_style: string | null;
  knowledge_boundary: string | null;
  output_mode: OutputMode;
  output_type: string | null;
  output_schema: Record<string, unknown> | null;
  model_binding: ModelBinding | null;
  knowledge_refs: KnowledgeRef[];
  validated_knowledge_versions: { knowledge_object_id: string; knowledge_version_id: string }[];
  data_asset_bindings: DataAssetSummary[];
  briefing: RoleBriefingView;
  definition_progress: ProgressItem[];
  share_readiness: ReadinessPanel;
  publish_readiness: ReadinessPanel;
  legacy: LegacyInfo;
  has_test_record: boolean;
  latest_test_rating: number | null;
  latest_tested_at: string | null;
  latest_validation_status: string | null;
  test_run_count: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface RoleWorkspaceSummary {
  role_id: string;
  role_version_id: string | null;
  status: RoleStatus;
  definition_progress: ProgressItem[];
  share_readiness: ReadinessPanel;
  publish_readiness: ReadinessPanel;
  legacy: LegacyInfo;
}

export interface RoleVersionPublicResponse {
  role_id: string;
  role_version_id: string;
  name: string;
  summary: string;
  main_duty_cluster: string | null;
  point_of_view: string | null;
  knowledge_boundary: string | null;
  output_mode: OutputMode;
  output_type: string | null;
  output_schema: Record<string, unknown> | null;
  model_binding: ModelBinding | null;
  data_asset_bindings: DataAssetSummary[];
  briefing: RoleBriefingView;
  knowledge_refs: KnowledgeRef[];
  validated_knowledge_versions: { knowledge_object_id: string; knowledge_version_id: string }[];
  has_test_record: boolean;
  latest_tested_at: string | null;
  test_run_count: number;
}

export interface VersionItem {
  role_version_id: string;
  version_number: number;
  status: string;
  published_at: string | null;
}

export interface PublishedVersion {
  role_id: string;
  role_version_id: string;
  published_at: string | null;
  published_by: string | null;
}

export interface ConsumeRecord {
  id: string;
  role_asset_id: string;
  role_version_id: string;
  caller_id: string | null;
  caller_type: string;
  query: string;
  context: string | null;
  answer: string;
  structured_result: Record<string, unknown> | null;
  output_type: string | null;
  status: string;
  status_reason: string | null;
  boundary_status: Record<string, string> | null;
  sources: Array<Record<string, unknown>> | null;
  created_at: string | null;
}

export interface ConsumeResponse {
  status: string;
  status_reason: string;
  answer: string;
  boundary_status: Record<string, string>;
  structured_result: Record<string, unknown>;
  output_type: string | null;
  sources: Array<Record<string, unknown>>;
  role_id: string;
  role_version_id: string;
  usage_record_id: string;
  created_at: string;
}

export interface TestConsumeResponse {
  status: string;
  status_reason: string;
  answer: string;
  boundary_status: Record<string, string>;
  structured_result: Record<string, unknown>;
  output_type: string | null;
  sources: Array<Record<string, unknown>>;
  role_id: string;
  role_version_id: string;
  validation_record_id: string;
  created_at: string;
}

export interface TestValidationRecord {
  validation_record_id: string;
  role_id: string;
  role_version_id: string;
  query: string;
  context: string | null;
  answer: string;
  structured_result: Record<string, unknown> | null;
  output_type: string | null;
  status: string;
  status_reason: string;
  boundary_status: Record<string, string> | null;
  sources: Array<Record<string, unknown>>;
  created_at: string | null;
}

export interface TestResult {
  id: string;
  role_id: string;
  version_id: string | null;
  test_input: string;
  test_output: string;
  knowledge_retrieved: Array<{ source: string; score: number }>;
  human_rating: number | null;
  tested_at: string | null;
}

export interface AIDraftResponse {
  name: string;
  bio: string;
  tags: string[];
  main_duty_cluster: string | null;
  point_of_view: string | null;
  decision_style: string | null;
  identity_background: string | null;
  speaking_style: string | null;
  knowledge_boundary: string | null;
  output_mode: OutputMode;
  output_type: string | null;
  output_schema: Record<string, unknown> | null;
  category: string;
  business_domain: string | null;
  applicable_scenarios: string[];
  usage_notes: string | null;
  support_basis_summary: string | null;
  ai_generation_note: string | null;
}

export interface DashboardStats {
  total_roles: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  total_consume_calls: number;
  consume_by_status: Record<string, number>;
  creation_by_source: Record<string, number>;
  boundary_blocked_ratio: number;
  undefined_ratio: number;
}

export interface RecommendItem {
  role_id: string;
  role_version_id: string | null;
  role_name: string;
  bio: string;
  recommendation_reason: string;
  reason_summary: string;
  reason_evidence: string[];
  matched_dimensions: string[];
  caution: string | null;
  applicable_problems: string[];
  applicable_scenarios_label: string;
  output_type: string | null;
  knowledge_boundary: string | null;
  version_number: number | null;
  version_status: string | null;
  tags: string[];
  match_score: number | null;
}

export interface RecommendResponse {
  matched: boolean;
  result_type: 'matched' | 'no_match' | 'out_of_scope' | 'service_error';
  recommendations: RecommendItem[];
  unmatched_intent_summary: string | null;
  service_error_message: string | null;
}

export interface ExportFile {
  path: string;
  content: string;
}

export interface ExportPackage {
  package_id: string;
  package_type: 'tool' | 'skill';
  role_id: string;
  role_version_id: string;
  is_stale: boolean;
  created_at: string | null;
  files: ExportFile[];
  stale_reason: string | null;
}

export const statusText: Record<string, string> = {
  draft: '草稿',
  test: '测试中',
  published: '已发布',
  archived: '已归档',
};

export const outputModeText: Record<OutputMode, string> = {
  freeform: '自由输出',
  structured: '结构化输出',
};

export const briefingStatusText: Record<BriefingStatus, string> = {
  missing: '待保存',
  fresh: '已保存',
  stale: '待确认更新',
};

export const consumeStatusText: Record<string, string> = {
  success: '成功返回',
  insufficient_context: '上下文不足',
  insufficient_knowledge: '知识不足',
  boundary_blocked: '触发边界限制',
  system_failed: '系统失败',
  undefined: '未定义',
};

export const boundaryDimensionText: Record<string, string> = {
  within_boundary: '边界内',
  near_boundary: '接近边界',
  out_of_scope: '超出范围',
  not_applicable: '不适用',
};

export const outputTypeText: Record<string, string> = {
  decision_advice: '决策建议',
  risk_analysis: '风险分析',
  policy_explanation: '制度解释',
  review_findings: '专业审查',
};

export const categoryText: Record<string, string> = {
  行业专家: '行业专家',
  职能助手: '职能助手',
  制度顾问: '制度顾问',
  项目管理: '项目管理',
  自定义: '自定义',
};

export const visibilityText: Record<string, string> = {
  内部: '内部',
  部门: '部门',
  公开: '公开',
};

export const decisionStyleText: Record<string, string> = {
  balanced: '平衡型',
  directive: '指令型',
  analytical: '分析型',
  consultative: '咨询型',
  collaborative: '协作型',
  delegatable: '可委派型',
};

export const collaborationModeText: Record<string, string> = {
  delegatable: '可委派',
  autonomous: '自主决策',
  collaborative: '协同决策',
  advisory: '顾问式',
};

export const api = {
  login: (username: string, password: string) =>
    request<{ access_token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),
  me: () => request<User>('/auth/me'),
  logout: () => request<{ status: string }>('/auth/logout', { method: 'POST' }),

  listRoles: (params?: { status?: string; category?: string; owner?: string; business_domain?: string; visibility?: string }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value) query.set(key, value);
    });
    const qs = query.toString();
    return request<RoleListItem[]>(`/role-assets${qs ? `?${qs}` : ''}`);
  },
  getRole: (id: string) => request<RoleDetail>(`/role-assets/${id}`),
  getWorkspace: (id: string) => request<RoleWorkspaceSummary>(`/role-assets/${id}/workspace`),
  createRole: (data: Record<string, unknown>, creationSourceHint?: string) => {
    const url = creationSourceHint ? `/role-assets?creation_source_hint=${encodeURIComponent(creationSourceHint)}` : '/role-assets';
    return request<RoleDetail>(url, { method: 'POST', body: JSON.stringify(data) });
  },
  updateRole: (id: string, data: Record<string, unknown>) =>
    request<RoleDetail>(`/role-assets/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  saveBriefing: (id: string, data: Record<string, unknown>) =>
    request<RoleDetail>(`/role-assets/${id}/briefing`, { method: 'PATCH', body: JSON.stringify(data) }),
  regenerateBriefing: (id: string) =>
    request<RoleDetail>(`/role-assets/${id}/briefing/regenerate`, { method: 'POST' }),
  toTest: (id: string) => request<RoleDetail>(`/role-assets/${id}/to-test`, { method: 'POST' }),
  publish: (id: string) => request<RoleDetail>(`/role-assets/${id}/publish`, { method: 'POST' }),
  archive: (id: string) => request<RoleDetail>(`/role-assets/${id}/archive`, { method: 'POST' }),
  deleteRole: (id: string) => request<void>(`/role-assets/${id}`, { method: 'DELETE' }),

  listVersions: (id: string) => request<VersionItem[]>(`/role-assets/${id}/versions`),
  getPublishedVersion: (id: string) => request<PublishedVersion>(`/role-assets/${id}/published-version`),
  getVersionDetail: (versionId: string) => request<RoleVersionPublicResponse>(`/role-versions/${versionId}`),

  knowledgeBases: () => request<KnowledgeBaseItem[]>('/knowledge/bases'),
  knowledgeCatalog: (kbId?: string) => request<KnowledgeItem[]>(`/knowledge/catalog${kbId ? `?kb_id=${encodeURIComponent(kbId)}` : ''}`),
  listKnowledge: (id: string) => request<KnowledgeRef[]>(`/role-assets/${id}/knowledge`),
  bindKnowledge: (id: string, data: Record<string, unknown>) =>
    request<KnowledgeRef>(`/role-assets/${id}/knowledge`, { method: 'POST', body: JSON.stringify(data) }),
  unbindKnowledge: (roleId: string, refId: string) =>
    request<void>(`/role-assets/${roleId}/knowledge/${refId}`, { method: 'DELETE' }),

  listDataAssets: (status?: string) =>
    request<DataAssetSummary[]>(`/data-assets${status ? `?status=${encodeURIComponent(status)}` : ''}`),
  createDataAsset: (data: Record<string, unknown>) =>
    request<DataAssetSummary>('/data-assets', { method: 'POST', body: JSON.stringify(data) }),
  updateDataAsset: (id: string, data: Record<string, unknown>) =>
    request<DataAssetSummary>(`/data-assets/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  aiDraft: (description: string, category?: string, businessDomain?: string) =>
    request<AIDraftResponse>('/role-assets/ai-draft', {
      method: 'POST',
      body: JSON.stringify({ description, category, business_domain: businessDomain }),
    }),
  listOutputTemplates: () => request<Record<string, unknown>>('/role-assets/output-templates'),

  consumeRole: (roleId: string, data: Record<string, unknown>) =>
    request<ConsumeResponse>(`/role-assets/${roleId}/consume`, { method: 'POST', body: JSON.stringify(data) }),
  testConsumeRole: (roleId: string, data: Record<string, unknown>) =>
    request<TestConsumeResponse>(`/role-assets/${roleId}/test-consume`, { method: 'POST', body: JSON.stringify(data) }),
  getConsumeRecords: (roleId: string) => request<ConsumeRecord[]>(`/role-assets/${roleId}/consume-records`),
  getTestValidationRecords: (roleId: string, params?: { versionId?: string; offset?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.versionId) query.set('version_id', params.versionId);
    if (params?.offset !== undefined) query.set('offset', String(params.offset));
    if (params?.limit !== undefined) query.set('limit', String(params.limit));
    const qs = query.toString();
    return request<TestValidationRecord[]>(`/role-assets/${roleId}/test-validations${qs ? `?${qs}` : ''}`);
  },
  runLegacyTest: (roleId: string, testInput: string) =>
    request<TestResult>(`/role-assets/${roleId}/test`, { method: 'POST', body: JSON.stringify({ test_input: testInput }) }),
  getTestHistory: (roleId: string) => request<TestResult[]>(`/role-assets/${roleId}/tests`),
  rateTest: (testId: string, humanRating: number) =>
    request<TestResult>(`/test-runs/${testId}/rate`, { method: 'POST', body: JSON.stringify({ human_rating: humanRating }) }),

  dashboardStats: () => request<DashboardStats>('/dashboard/stats'),
  marketplaceList: (params?: { category?: string; business_domain?: string; output_type?: string }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value) query.set(key, value);
    });
    const qs = query.toString();
    return request<RoleListItem[]>(`/marketplace${qs ? `?${qs}` : ''}`);
  },
  marketplaceRecommend: (intent: string, category?: string, businessDomain?: string) =>
    request<RecommendResponse>('/marketplace/recommend', {
      method: 'POST',
      body: JSON.stringify({ intent, category, business_domain: businessDomain }),
    }),

  listExportPackages: (roleId: string) => request<ExportPackage[]>(`/role-assets/${roleId}/export-packages`),
  generateExportPackage: (roleId: string, packageType: 'tool' | 'skill') =>
    request<ExportPackage>(`/role-assets/${roleId}/export-packages/${packageType}`, { method: 'POST' }),
  exportPackageDownloadUrl: (roleId: string, packageId: string) =>
    `/role-assets/${roleId}/export-packages/${packageId}/download`,

  listBusinessDomains: () =>
    request<{ id: string; name: string; sort_order: number; is_active: boolean }[]>('/config/business-domains?active_only=true'),
  listEnterpriseRoles: (businessDomainId?: string) => {
    const qs = businessDomainId ? `?business_domain_id=${encodeURIComponent(businessDomainId)}&active_only=true` : '?active_only=true';
    return request<{ id: string; business_domain_id: string; name: string; business_domain_name: string; sort_order: number; is_active: boolean }[]>(`/config/enterprise-roles${qs}`);
  },
  listStaff: () =>
    request<{ id: string; name: string; department: string | null; email: string | null }[]>('/config/staff?active_only=true'),
};
