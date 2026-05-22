/**
 * Virtual Actor — 前端 API 客户端
 * 注入到 prototype/index.html 中，连接后端 API
 */
const API_BASE = "http://localhost:8000";

const api = {
  // ── 角色 CRUD ──
  async listRoles(status = "") {
    const q = status ? `?status=${status}` : "";
    const r = await fetch(`${API_BASE}/role-assets${q}`);
    return r.json();
  },
  async getRole(roleId) {
    const r = await fetch(`${API_BASE}/role-assets/${roleId}`);
    return r.json();
  },
  async createRole(data) {
    const r = await fetch(`${API_BASE}/role-assets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return r.json();
  },
  async updateRole(roleId, data) {
    const r = await fetch(`${API_BASE}/role-assets/${roleId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return r.json();
  },
  async deleteRole(roleId) {
    await fetch(`${API_BASE}/role-assets/${roleId}`, { method: "DELETE" });
  },

  // ── 状态迁移 ──
  async publishRole(roleId, by = "admin") {
    const r = await fetch(`${API_BASE}/role-assets/${roleId}/publish?published_by=${by}`, { method: "POST" });
    return r.json();
  },
  async archiveRole(roleId) {
    const r = await fetch(`${API_BASE}/role-assets/${roleId}/archive`, { method: "POST" });
    return r.json();
  },
  async toTest(roleId) {
    const r = await fetch(`${API_BASE}/role-assets/${roleId}/to-test`, { method: "POST" });
    return r.json();
  },

  // ── 版本 ──
  async publishedVersion(roleId) {
    const r = await fetch(`${API_BASE}/role-assets/${roleId}/published-version`);
    return r.json();
  },
  async versionDetail(versionId) {
    const r = await fetch(`${API_BASE}/role-versions/${versionId}`);
    return r.json();
  },
  async versionList(roleId) {
    const r = await fetch(`${API_BASE}/role-assets/${roleId}/versions`);
    return r.json();
  },

  // ── 测试 ──
  async runTest(roleId, testInput) {
    const r = await fetch(`${API_BASE}/role-assets/${roleId}/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ test_input: testInput }),
    });
    return r.json();
  },
  async testHistory(roleId) {
    const r = await fetch(`${API_BASE}/role-assets/${roleId}/tests`);
    return r.json();
  },
  async rateTest(testId, rating) {
    const r = await fetch(`${API_BASE}/test-runs/${testId}/rate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ human_rating: rating }),
    });
    return r.json();
  },

  // ── 知识绑定 ──
  async listKnowledge(roleId) {
    const r = await fetch(`${API_BASE}/role-assets/${roleId}/knowledge`);
    return r.json();
  },
  async bindKnowledge(roleId, data) {
    const r = await fetch(`${API_BASE}/role-assets/${roleId}/knowledge`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return r.json();
  },
  async unbindKnowledge(roleId, refId) {
    await fetch(`${API_BASE}/role-assets/${roleId}/knowledge/${refId}`, { method: "DELETE" });
  },

  // ── 健康检查 ──
  async health() {
    const r = await fetch(`${API_BASE}/health`);
    return r.json();
  },
};

console.log("✅ Virtual Actor API client loaded. Base:", API_BASE);