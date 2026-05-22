/**
 * Virtual Actor — API 集成层 v2
 * 覆盖原型所有页面函数，接入后端真实数据
 */
(async function() {
  const API = 'http://localhost:8000';
  let online = false;
  try { const r = await fetch(API+'/health'); online = r.ok; } catch(e) { online = false; }

  // 状态指示器
  const dot = document.createElement('div');
  dot.style.cssText = 'position:fixed;bottom:16px;right:16px;padding:5px 14px;border-radius:20px;font-size:11px;font-family:Inter,sans-serif;z-index:99999;';
  dot.style.background = online ? '#22C55E18' : '#EF444418';
  dot.style.color = online ? '#16A34A' : '#DC2626';
  dot.style.border = '1px solid ' + (online ? '#22C55E44' : '#EF444444');
  dot.textContent = online ? '🟢 API 已连接' : '🔴 离线（demo 数据）';
  document.body.appendChild(dot);
  if (!online) return;

  // ── 工具 ──
  const avatar = n => (n||'??').slice(0,2).toUpperCase();
  const labels = {draft:'草稿',test:'测试中',published:'已发布',archived:'已归档'};
  const colors = {draft:'#94A3B8',test:'#F59E0B',published:'#22C55E',archived:'#6B7280'};
  const badge = s => `<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;color:#fff;background:${colors[s]||'#94A3B8'};">${labels[s]||s}</span>`;
  const G = id => document.getElementById(id);

  // ── API 调用 ──
  const api = {
    list: async () => (await fetch(API+'/role-assets')).json(),
    get: async id => (await fetch(API+'/role-assets/'+id)).json(),
    create: async d => (await fetch(API+'/role-assets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)})).json(),
    update: async (id,d) => (await fetch(API+'/role-assets/'+id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)})).json(),
    publish: async id => (await fetch(API+'/role-assets/'+id+'/publish?published_by=admin',{method:'POST'})).json(),
    archive: async id => fetch(API+'/role-assets/'+id+'/archive',{method:'POST'}),
    test: async (id,input) => (await fetch(API+'/role-assets/'+id+'/test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({test_input:input})})).json(),
    knowledge: async id => (await fetch(API+'/role-assets/'+id+'/knowledge')).json(),
    versions: async id => (await fetch(API+'/role-assets/'+id+'/versions')).json(),
  };

  // ── 数据转换：后端 → 完整原型格式 ──
  function toProto(r) {
    const mb = r.model_binding || {};
    return {
      id: r.role_id,
      name: r.role_name || r.name,
      status: r.status,
      bio: r.bio,
      tags: r.tags || [],
      avatar_initials: avatar(r.role_name || r.name),
      updated_at: r.updated_at,
      created_at: r.created_at,
      current_version: r.role_version_id || r.current_version_id,
      // L2 心智
      identity_background: r.identity_background || '',
      point_of_view: r.point_of_view || '',
      decision_style: r.decision_style || 'balanced',
      responsibility_boundary: r.responsibility_boundary || '',
      speaking_style: r.speaking_style || '',
      // L3 知识
      knowledge_refs: (r.knowledge_refs||[]).map(k => k.knowledge_object_id),
      validated_knowledge_versions: r.validated_knowledge_versions || [],
      // L4
      collaboration_mode: r.collaboration_mode || 'independent',
      capability_boundary: r.capability_boundary || '',
      // L5
      model_binding: {
        provider: mb.model_provider || 'openai',
        model: mb.model_name || 'gpt-4o',
        temperature: mb.temperature || 0.7,
        max_tokens: mb.max_tokens || 4096,
      },
      // 质量信号
      has_test_record: r.has_test_record,
      latest_test_rating: r.latest_test_rating,
      versions: [],
      _raw: r,
    };
  }

  // ── 同步函数：从 API 拉取并存入 appState ──
  async function syncRoles() {
    try { const list = await api.list(); appState.roles = list.map(toProto); } catch(e) { console.warn(e); }
  }
  async function syncRole(id) {
    try {
      const r = await api.get(id);
      const p = toProto(r);
      const idx = appState.roles.findIndex(x => x.id === id);
      if (idx >= 0) appState.roles[idx] = p; else appState.roles.unshift(p);
      return p;
    } catch(e) { console.warn(e); }
  }

  // ═══════════════════ 角色列表 ═══════════════════
  window.renderRoleList = async function(filterStatus) {
    filterStatus = filterStatus || appState._listFilter || 'all';
    appState._listFilter = filterStatus;
    await syncRoles();
    const roles = filterStatus === 'all' ? appState.roles : appState.roles.filter(r => r.status === filterStatus);
    const sts = ['all','draft','test','published','archived'];
    const cnt = {}; sts.forEach(s => { cnt[s] = s==='all' ? appState.roles.length : appState.roles.filter(r=>r.status===s).length; });
    const body = G('roleListBody'); if (!body) return;
    let h = '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;"><div class="filter-tabs">';
    sts.forEach(s => h += `<div class="filter-tab ${filterStatus===s?'active':''}" onclick="setListFilter('${s}')">${labels[s]||'全部'} <span style="opacity:0.7;font-size:11px;">${cnt[s]}</span></div>`);
    h += '</div><button class="btn btn-primary btn-lg" onclick="navigate(\'role-create\')">➕ 新建角色</button></div>';
    if (roles.length === 0) {
      h += '<div class="empty-state card"><div class="empty-icon">🎭</div><h3>还没有角色</h3><p>创建你的第一个虚拟角色</p><button class="btn btn-primary" onclick="navigate(\'role-create\')">创建角色</button></div>';
    } else {
      h += '<div class="role-grid">';
      roles.forEach(r => {
        const kc = (r.knowledge_refs||[]).length;
        h += `<div class="card role-card" onclick="navigate('role-detail','${r.id}')"><div class="role-card-inner"><div class="role-card-header">`;
        h += `<div class="role-card-avatar">${r.avatar_initials}</div>`;
        h += `<div style="flex:1;min-width:0;"><div style="display:flex;align-items:center;gap:8px;"><span class="role-card-title">${r.name}</span>${badge(r.status)}</div>`;
        h += `<div class="role-card-bio">${r.bio||'暂无简介'}</div></div></div>`;
        h += `<div class="role-card-meta"><span>📚 ${kc} 条知识</span><span>🕐 ${new Date(r.updated_at).toLocaleDateString('zh-CN')}</span></div>`;
        h += `<div class="role-card-actions" onclick="event.stopPropagation()">`;
        h += `<button class="btn btn-ghost btn-sm" onclick="navigate('role-edit','${r.id}')">编辑</button>`;
        if (r.status !== 'published') h += `<button class="btn btn-ghost btn-sm" onclick="navigate('role-test','${r.id}')">测试</button>`;
        if (r.status === 'test') h += `<button class="btn btn-primary btn-sm" onclick="navigate('role-publish','${r.id}')">发布</button>`;
        if (r.status === 'published') h += `<button class="btn btn-secondary btn-sm" onclick="apiArchive('${r.id}')">归档</button>`;
        h += '</div></div></div>';
      });
      h += '</div>';
    }
    body.innerHTML = h;
  };
  window.setListFilter = s => { appState._listFilter = s; window.renderRoleList(s); };

  // ═══════════════════ 归档 ═══════════════════
  window.apiArchive = async function(id) { await api.archive(id); window.renderRoleList(appState._listFilter); };

  // ═══════════════════ 角色详情 ═══════════════════
  window.getRoleById = function(id) {
    let r = appState.roles.find(x => x.id === id);
    if (!r && appState._roleCache && appState._roleCache[id]) r = appState._roleCache[id];
    return r;
  };

  const origHandleRoute = window.handleRoute;
  window.handleRoute = async function() {
    const hash = window.location.hash.replace('#','');
    const parts = hash.split('/');
    const page = parts[1] || 'role-list';
    const roleId = parts[2];

    // 如果进入详情/编辑/测试页，预加载完整角色数据 + 知识绑定
    if (roleId && ['role-detail','role-edit','role-test','role-publish'].includes(page)) {
      await syncRole(roleId);
      // 加载该角色的真实知识绑定，替换 demo 数据供编辑页展示
      if (page === 'role-edit') {
        try {
          const kList = await api.knowledge(roleId);
          appState.knowledgeItems = kList.map(k => ({
            id: k.knowledge_object_id,
            title: k.title || k.knowledge_object_id,
            type: k.type || 'knowledge',
            tags: [],
          }));
        } catch(e) { appState.knowledgeItems = []; }
      }
    }

    // 调用原始路由
    origHandleRoute();

    // 如果进入详情页且 API 在线，替换为异步渲染
    if (page === 'role-detail' && roleId) {
      const r = window.getRoleById(roleId);
      if (r) renderDetailAsync(r);
    }
  };

  async function renderDetailAsync(r) {
    const body = G('roleDetailBody'); if (!body) return;
    const kList = await api.knowledge(r.id).catch(() => []);
    const vList = await api.versions(r.id).catch(() => []);
    const ds = {conservative:'保守型',balanced:'平衡型',aggressive:'激进型'};
    const mb = r.model_binding || {};

    let h = '';
    // L1 身份
    h += `<div class="card"><h3>📋 基本信息</h3><div class="kv-grid">`;
    h += `<div class="kv-item"><span class="kv-label">名称</span><span class="kv-value">${r.name}</span></div>`;
    h += `<div class="kv-item"><span class="kv-label">状态</span><span class="kv-value">${badge(r.status)}</span></div>`;
    h += `<div class="kv-item"><span class="kv-label">标签</span><span class="kv-value">${(r.tags||[]).join(', ')||'—'}</span></div>`;
    h += `<div class="kv-item"><span class="kv-label">简介</span><span class="kv-value">${r.bio||'—'}</span></div>`;
    h += `</div></div>`;

    // L2 心智
    h += `<div class="card"><h3>🧠 心智层</h3><div class="kv-grid">`;
    h += kv('背景',r.identity_background); h += kv('立场',r.point_of_view);
    h += kv('决策风格',ds[r.decision_style]||r.decision_style); h += kv('职责边界',r.responsibility_boundary);
    h += kv('表达风格',r.speaking_style);
    h += `</div></div>`;

    // L3 知识
    h += `<div class="card"><h3>📚 知识层</h3>`;
    if (kList.length === 0) h += '<p style="color:var(--text-light);">未绑定知识</p>';
    else { h += '<ul>'; kList.forEach(k => h += `<li>${k.title||k.knowledge_object_id} <span style="color:var(--text-light);font-size:12px;">(${k.type||'—'})</span></li>`); h += '</ul>'; }
    h += `</div>`;

    // L5 配置
    h += `<div class="card"><h3>⚙️ 模型配置</h3><div class="kv-grid">`;
    h += kv('模型',mb.model||'—'); h += kv('温度',mb.temperature||'—');
    h += `</div></div>`;

    // 版本
    if (vList.length > 0) {
      h += `<div class="card"><h3>📜 版本历史</h3><ul>`;
      vList.forEach(v => h += `<li>v${v.version_number} — ${v.status} ${v.published_at ? new Date(v.published_at).toLocaleString('zh-CN') : ''}</li>`);
      h += `</ul></div>`;
    }

    // 操作
    h += `<div style="display:flex;gap:8px;margin-top:16px;">`;
    h += `<button class="btn btn-ghost" onclick="navigate('role-edit','${r.id}')">编辑</button>`;
    if (r.status !== 'published') h += `<button class="btn btn-primary" onclick="navigate('role-test','${r.id}')">测试</button>`;
    if (r.status === 'test') h += `<button class="btn btn-primary" onclick="navigate('role-publish','${r.id}')">发布</button>`;
    if (r.status === 'published') h += `<button class="btn btn-secondary" onclick="apiArchive('${r.id}')">归档</button>`;
    h += `</div>`;

    body.innerHTML = h;
  }
  function kv(label,val) { return `<div class="kv-item"><span class="kv-label">${label}</span><span class="kv-value">${val||'—'}</span></div>`; }

  // ═══════════════════ 保存角色（创建/编辑） ═══════════════════
  window.saveRole = async function() {
    const getVal = id => { const el = G(id); return el ? el.value : ''; };
    const name = getVal('roleName'); const bio = getVal('roleBio');
    const isEdit = !!appState.editingRoleId;

    const data = {
      name, bio,
      tags: getVal('roleTags').split(',').map(s=>s.trim()).filter(Boolean),
      identity_background: getVal('roleBackground'),
      point_of_view: getVal('rolePOV'),
      decision_style: getVal('roleDecisionStyle'),
      responsibility_boundary: getVal('roleResponsibility'),
      speaking_style: getVal('roleSpeakingStyle'),
      model_binding: {
        model_provider: getVal('modelProvider')||'openai',
        model_name: getVal('modelName')||'gpt-4o',
        temperature: parseFloat(getVal('modelTemperature')||'0.7'),
        max_tokens: parseInt(getVal('modelMaxTokens')||'4096'),
      },
    };

    try {
      if (isEdit) {
        await api.update(appState.editingRoleId, data);
      } else {
        await api.create(data);
      }
    } catch(e) { console.error(e); alert('保存失败: '+e.message); return; }

    appState.editingRoleId = null;
    navigate('role-list');
  };

  // ═══════════════════ 角色测试 ═══════════════════
  window.sendTestMessage = async function() {
    const roleId = appState.editingRoleId || (appState.roles[0] && appState.roles[0].id);
    const inputEl = G('testInput'); const container = G('chatMessages');
    if (!inputEl || !container || !inputEl.value.trim()) return;
    const text = inputEl.value.trim();
    inputEl.value = '';
    container.innerHTML += `<div class="chat-bubble user"><div class="chat-bubble-header">🧑 你</div>${text}</div>`;
    const loading = document.createElement('div');
    loading.className = 'chat-bubble role';
    loading.innerHTML = '<div class="chat-bubble-header">🎭 角色</div>⏳ 思考中...';
    container.appendChild(loading);
    container.scrollTop = container.scrollHeight;

    try {
      const result = await api.test(roleId, text);
      loading.innerHTML = `<div class="chat-bubble-header">🎭 角色</div><div style="white-space:pre-wrap;">${result.test_output||'无回复'}</div>`;
    } catch(e) {
      loading.innerHTML = `<div class="chat-bubble-header">🎭 角色</div>❌ 测试失败: ${e.message}`;
    }
    container.scrollTop = container.scrollHeight;
  };

  // ═══════════════════ 发布 ═══════════════════
  window.publishRole = async function() {
    const roleId = appState.editingRoleId;
    if (!roleId) { alert('未找到要发布的角色'); return; }
    try {
      await api.publish(roleId);
      navigate('role-list');
    } catch(e) { alert('发布失败: '+e.message); }
  };

  // ═══════════════════ 编辑/测试/发布上下文 ═══════════════════
  // 当进入编辑/测试/发布页时，记录当前操作的 roleId
  const origRenderEdit = window.renderRoleEdit;
  if (origRenderEdit) {
    window.renderRoleEdit = function(roleId) {
      appState.editingRoleId = roleId;
      return origRenderEdit(roleId);
    };
  }
  const origRenderTest = window.renderRoleTest;
  if (origRenderTest) {
    window.renderRoleTest = function(roleId) {
      appState.editingRoleId = roleId;
      return origRenderTest(roleId);
    };
  }
  const origRenderPublish = window.renderRolePublish;
  if (origRenderPublish) {
    window.renderRolePublish = function(roleId) {
      appState.editingRoleId = roleId;
      return origRenderPublish(roleId);
    };
  }

  // ═══════════════════ 首次加载 ═══════════════════
  window.renderRoleList('all');
  console.log('✅ API 集成层 v2 已激活 — 详情/编辑/测试/发布页均接入后端');
})();