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
  const r = await fetch(BASE + url, { ...opts, headers: { ...headers, ...(opts?.headers || {}) } });
  if (!r.ok) {
    const err = await r.json().catch(() => ({})) as { detail?: string };
    throw new Error(err.detail || `HTTP ${r.status}`);
  }
  if (r.status === 204) return undefined as T;
  return r.json();
}

export interface User { username: string }

export interface ModelBinding {
  model_provider: string;
  model_name: string;
  temperature: number;
  max_tokens: number;
  fallback_enabled?: boolean;
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

export interface RoleListItem {
  role_id: string;
  role_version_id: string | null;
  role_name: string;
  bio: string;
  tags: string[];
  status: string;
  summary: string;
  model_binding: ModelBinding | null;
  has_test_record: boolean;
  latest_test_rating: number | null;
  latest_tested_at: string | null;
  test_run_count: number;
  updated_at: string | null;
}

export interface RoleDetail {
  role_id: string;
  role_version_id: string | null;
  name: string;
  bio: string;
  tags: string[];
  status: string;
  identity_background?: string | null;
  point_of_view?: string | null;
  decision_style?: string | null;
  responsibility_boundary?: string | null;
  speaking_style?: string | null;
  collaboration_mode?: string | null;
  capability_boundary?: string | null;
  model_binding?: ModelBinding | null;
  knowledge_refs: KnowledgeRef[];
  validated_knowledge_versions: { knowledge_object_id: string; knowledge_version_id: string }[];
  has_test_record: boolean;
  latest_test_rating: number | null;
  latest_tested_at: string | null;
  test_run_count: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface TestResult {
  id: string;
  role_id: string;
  version_id: string | null;
  test_input: string;
  test_output: string;
  knowledge_retrieved: { source: string; score: number }[];
  human_rating: number | null;
  tested_at: string | null;
}

export interface VersionItem {
  role_version_id: string;
  version_number: number;
  status: string;
  published_at: string | null;
}

export const statusText: Record<string, string> = {
  draft: '草稿',
  test: '测试中',
  published: '已发布',
  archived: '已归档',
};

export const api = {
  login: (username: string, password: string) => request<{ access_token: string; user: User }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  }),
  me: () => request<User>('/auth/me'),
  logout: () => request<{ status: string }>('/auth/logout', { method: 'POST' }),

  listRoles: (status?: string) => request<RoleListItem[]>(`/role-assets${status ? `?status=${status}` : ''}`),
  getRole: (id: string) => request<RoleDetail>(`/role-assets/${id}`),
  createRole: (data: Record<string, unknown>) => request<RoleDetail>('/role-assets', { method: 'POST', body: JSON.stringify(data) }),
  updateRole: (id: string, data: Record<string, unknown>) => request<RoleDetail>(`/role-assets/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteRole: (id: string) => request<void>(`/role-assets/${id}`, { method: 'DELETE' }),
  toTest: (id: string) => request<RoleDetail>(`/role-assets/${id}/to-test`, { method: 'POST' }),
  publish: (id: string) => request<RoleDetail>(`/role-assets/${id}/publish`, { method: 'POST' }),
  archive: (id: string) => request<RoleDetail>(`/role-assets/${id}/archive`, { method: 'POST' }),

  versions: (id: string) => request<VersionItem[]>(`/role-assets/${id}/versions`),
  publishedVersion: (id: string) => request<{ role_version_id: string; published_at: string | null }>(`/role-assets/${id}/published-version`),
  versionDetail: (vid: string) => request<Record<string, unknown>>(`/role-versions/${vid}`),

  knowledgeBases: () => request<KnowledgeBaseItem[]>('/knowledge/bases'),
  catalog: (kbId?: string) => request<KnowledgeItem[]>(`/knowledge/catalog${kbId ? `?kb_id=${encodeURIComponent(kbId)}` : ''}`),
  listKnowledge: (roleId: string) => request<KnowledgeRef[]>(`/role-assets/${roleId}/knowledge`),
  bindKnowledge: (roleId: string, data: Record<string, unknown>) => request<KnowledgeRef>(`/role-assets/${roleId}/knowledge`, { method: 'POST', body: JSON.stringify(data) }),
  unbindKnowledge: (roleId: string, refId: string) => request<void>(`/role-assets/${roleId}/knowledge/${refId}`, { method: 'DELETE' }),

  runTest: (roleId: string, testInput: string) => request<TestResult>(`/role-assets/${roleId}/test`, { method: 'POST', body: JSON.stringify({ test_input: testInput }) }),
  testHistory: (roleId: string) => request<TestResult[]>(`/role-assets/${roleId}/tests`),
  rateTest: (testId: string, human_rating: number) => request<TestResult>(`/test-runs/${testId}/rate`, { method: 'POST', body: JSON.stringify({ human_rating }) }),

  health: () => request<{ status: string }>('/health'),
  knowledgeHealth: () => request<{ knowledge_platform: string }>('/health/knowledge-platform'),
};
