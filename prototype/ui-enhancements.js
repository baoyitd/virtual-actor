/**
 * Virtual Actor — UI 增强层 v1
 * Toast + Loading + 校验 + 搜索 + 测试页优化
 */
(function() {
  if (typeof appState === 'undefined') return;

  // ═══════════════════ 1. Toast 通知系统 ═══════════════════
  const toastContainer = document.createElement('div');
  toastContainer.id = 'va-toasts';
  toastContainer.style.cssText = 'position:fixed;top:16px;right:16px;z-index:99999;display:flex;flex-direction:column;gap:8px;';
  document.body.appendChild(toastContainer);

  window.showToast = function(msg, type = 'success') {
    const colors = { success: '#22C55E', error: '#EF4444', warning: '#F59E0B', info: '#3B82F6' };
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const t = document.createElement('div');
    t.style.cssText = `background:var(--card,#fff);color:var(--text,#1E293B);padding:10px 16px;border-radius:8px;font-size:13px;font-family:Inter,sans-serif;box-shadow:0 4px 20px rgba(0,0,0,0.12);border-left:3px solid ${colors[type]};display:flex;align-items:center;gap:8px;animation:va-slide-in 0.3s ease;min-width:260px;`;
    t.innerHTML = `<span>${icons[type]}</span><span style="flex:1;">${msg}</span>`;
    toastContainer.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transition = 'opacity 0.3s'; setTimeout(() => t.remove(), 300); }, 3000);
  };

  // 动画
  const style = document.createElement('style');
  style.textContent = '@keyframes va-slide-in { from{opacity:0;transform:translateX(40px)} to{opacity:1;transform:translateX(0)} }';
  document.head.appendChild(style);

  // ═══════════════════ 2. 按钮 Loading ═══════════════════
  window.showLoading = function(el) {
    if (!el) return;
    el.disabled = true;
    el._origText = el.textContent;
    el.innerHTML = '<span style="display:inline-block;width:14px;height:14px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:va-spin 0.6s linear infinite;vertical-align:middle;margin-right:6px;"></span>' + el._origText;
  };
  window.hideLoading = function(el) {
    if (!el || !el._origText) return;
    el.disabled = false;
    el.textContent = el._origText;
  };
  style.textContent += '@keyframes va-spin { to{transform:rotate(360deg)} }';

  // ═══════════════════ 3. 表单校验提示 ═══════════════════
  window.validateField = function(el, msg) {
    if (!el) return true;
    el.style.borderColor = msg ? '#EF4444' : '';
    const exist = el.parentElement.querySelector('.va-error');
    if (exist) exist.remove();
    if (msg) {
      const err = document.createElement('div');
      err.className = 'va-error';
      err.style.cssText = 'color:#EF4444;font-size:11px;margin-top:4px;';
      err.textContent = msg;
      el.parentElement.appendChild(err);
      return false;
    }
    return true;
  };
  window.validForm = function(el, v) { return validateField(document.getElementById(el), v); };

  // ═══════════════════ 4. 搜索框（注入到角色列表页） ═══════════════════
  const origRenderList = window.renderRoleList;
  if (origRenderList) {
    window.renderRoleList = async function(filterStatus) {
      await origRenderList(filterStatus);
      const body = document.getElementById('roleListBody');
      if (!body) return;
      // 在筛选标签下方插入搜索框
      const searchHtml = `<div style="margin-bottom:16px;"><input type="text" id="va-role-search" placeholder="🔍 搜索角色名称..." style="width:100%;max-width:400px;padding:8px 14px;border:1px solid #E2E8F0;border-radius:8px;font-size:14px;font-family:Inter,sans-serif;outline:none;" oninput="vaFilterRoles()"></div>`;
      body.insertAdjacentHTML('afterbegin', searchHtml);
    };
  }

  window.vaFilterRoles = function() {
    const q = (document.getElementById('va-role-search')?.value || '').toLowerCase();
    const cards = document.querySelectorAll('.role-card');
    cards.forEach(c => {
      const title = c.querySelector('.role-card-title')?.textContent?.toLowerCase() || '';
      c.style.display = title.includes(q) ? '' : 'none';
    });
  };

  // ═══════════════════ 5. Toast 注入 save/archive/publish ═══════════════════
  const origSave = window.saveRole;
  if (origSave) {
    window.saveRole = async function() {
      const name = document.getElementById('roleName')?.value?.trim();
      if (!name) { showToast('请输入角色名称', 'error'); return; }
      const btn = document.querySelector('button[onclick*="saveRole"]');
      if (btn) showLoading(btn);
      try { await origSave(); showToast(appState.editingRoleId ? '角色已更新' : '角色已创建', 'success'); }
      catch(e) { showToast('保存失败: ' + e.message, 'error'); if(btn) hideLoading(btn); }
      finally { if(btn) hideLoading(btn); }
    };
  }

  // 为 apiArchive 加 toast
  const origArchive = window.apiArchive;
  if (origArchive) {
    window.apiArchive = async function(id) {
      try { await origArchive(id); showToast('角色已归档', 'success'); }
      catch(e) { showToast('归档失败', 'error'); }
    };
  }

  // 为 publish 加 toast
  const origPublish = window.publishRole;
  if (origPublish) {
    window.publishRole = async function() {
      try { await origPublish(); showToast('角色已发布', 'success'); }
      catch(e) { showToast('发布失败', 'error'); }
    };
  }

  // ═══════════════════ 6. 测试页优化（聊天历史 + 上下文 + 快捷问题） ═══════════════════
  const origTest = window.renderRoleTest;
  if (origTest) {
    window.renderRoleTest = function(roleId) {
      origTest(roleId);
      setTimeout(async () => {
        const role = appState.roles.find(r => r.id === roleId);
        const body = document.getElementById('roleTestBody');
        if (!body || !role) return;

        // 角色上下文卡片
        const ctx = document.createElement('div');
        ctx.style.cssText = 'display:flex;align-items:center;gap:12px;padding:10px 14px;background:#F8FAFC;border-radius:8px;margin-bottom:12px;font-size:12px;color:#64748B;font-family:Inter,sans-serif;';
        const mb = role.model_binding || {};
        ctx.innerHTML = `<div class="role-card-avatar" style="width:32px;height:32px;font-size:14px;">${(role.name||'??').slice(0,2)}</div>
          <div><strong style="color:#1E293B;">${role.name}</strong> · ${mb.model||'gpt-4o'} · ${role.status} ${role.has_test_record?'· ⭐'+role.latest_test_rating+'/5':''}</div>`;
        body.insertBefore(ctx, body.firstChild);

        // 快捷问题
        const quick = document.createElement('div');
        quick.style.cssText = 'display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;';
        const prompts = ['介绍你的专业背景', '你的核心观点是什么', '分析当前市场趋势'];
        quick.innerHTML = prompts.map(p => `<button class="btn btn-ghost btn-sm" onclick="vaQuickTest('${p}')" style="font-size:12px;">💬 ${p}</button>`).join('');
        body.insertBefore(quick, body.querySelector('input,textarea'));

        // 加载历史
        await loadTestHistory(roleId, body);

        // 输入框增强
        const inp = document.getElementById('testInput');
        if (inp) {
          inp.placeholder = '输入问题... Ctrl+Enter 发送';
          inp.addEventListener('keydown', e => { if (e.key === 'Enter' && (e.ctrlKey||e.metaKey)) window.sendTestMessage(); });
        }
      }, 300);
    };
  }

  window.vaQuickTest = function(prompt) {
    const inp = document.getElementById('testInput');
    if (inp) { inp.value = prompt; window.sendTestMessage(); }
  };

  async function loadTestHistory(roleId, body) {
    try {
      const r = await fetch(`http://localhost:8000/role-assets/${roleId}/tests`);
      if (!r.ok) return;
      const tests = await r.json();
      if (tests.length === 0) return;
      const container = document.getElementById('chatMessages');
      if (!container) return;
      container.innerHTML = ''; // 清空原有 demo 消息
      tests.reverse().forEach(t => {
        container.innerHTML += `<div class="chat-bubble user"><div class="chat-bubble-header">🧑 你 · ${new Date(t.tested_at).toLocaleTimeString('zh-CN')}</div>${t.test_input}</div>`;
        container.innerHTML += `<div class="chat-bubble role"><div class="chat-bubble-header">🎭 角色 · ${t.human_rating?'⭐'+t.human_rating+'/5':''}</div><div style="white-space:pre-wrap;">${t.test_output||'无回复'}</div></div>`;
      });
      container.scrollTop = container.scrollHeight;
    } catch(e) {}
  }

  console.log('✅ UI 增强层已激活 — Toast + Loading + 搜索 + 校验');

  // ═══════════════════ 清理 demo 知识数据 ═══════════════════
  appState.knowledgeItems = [];

  // ═══════════════════ 7. 覆盖原型知识弹窗（统一用真实API） ═══════════════════
  window.openKnowledgeModal = function() {
    window.openKnowledgeBrowser(appState.editingRoleId || '');
  };

  window.renderKnowledgeModal = function() {}; // 废弃，不再用demo渲染

  window.toggleKnowledgeSelect = function(kid) {
    const idx = (appState.tempKnowledgeSelection||[]).indexOf(kid);
    if (idx >= 0) appState.tempKnowledgeSelection.splice(idx, 1);
    else appState.tempKnowledgeSelection.push(kid);
  };

  window.confirmKnowledgeBinding = async function() {
    // 关闭弹窗
    const modal = document.getElementById('va-kb-modal');
    if (modal) modal.remove();

    const roleId = appState.editingRoleId;
    if (!roleId) return;

    // 真正调用后端绑定
    const checks = document.querySelectorAll('.va-kb-check:checked');
    let ok = 0;
    for (const c of checks) {
      try {
        await fetch(`http://localhost:8000/role-assets/${roleId}/knowledge`, {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({ knowledge_object_id: c.value, title: c.value, type: 'reference' })
        });
        appState.tempKnowledgeSelection.push(c.value);
        ok++;
      } catch(e) {}
    }

    // 刷新编辑页知识列表
    const listEl = document.getElementById('ef-knowledge-list');
    if (listEl && ok > 0) {
      const refs = await fetch(`http://localhost:8000/role-assets/${roleId}/knowledge`).then(r=>r.json()).catch(()=>[]);
      listEl.innerHTML = refs.length === 0
        ? '<div style="color:var(--text-light);font-size:13px;padding:8px 0;">暂未绑定知识</div>'
        : refs.map(k => `<div class="knowledge-item" style="cursor:default;border-color:var(--accent);background:rgba(14,165,233,0.03);"><div class="check" style="background:var(--accent);border-color:var(--accent);color:#fff;font-size:10px;">✓</div><div class="knowledge-info"><div class="knowledge-title">${k.title||k.knowledge_object_id}</div><div class="knowledge-meta"><span class="tag green">${k.type||'knowledge'}</span></div></div></div>`).join('');
    }

    window.showToast(`已绑定 ${ok} 条知识`, 'success');
  };

  // ═══════════════════ 8. 知识浏览面板（真实API） ═══════════════════
  window.openKnowledgeBrowser = function(roleId) {
    // 移除已有面板
    const exist = document.getElementById('va-kb-modal');
    if (exist) exist.remove();

    const modal = document.createElement('div');
    modal.id = 'va-kb-modal';
    modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:99998;display:flex;align-items:center;justify-content:center;';
    modal.innerHTML = `<div style="position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.4);" onclick="this.parentElement.remove()"></div>
    <div style="position:relative;background:#fff;border-radius:12px;width:90%;max-width:640px;max-height:80vh;display:flex;flex-direction:column;box-shadow:0 8px 40px rgba(0,0,0,0.15);">
      <div style="padding:16px 20px;border-bottom:1px solid #E2E8F0;display:flex;align-items:center;justify-content:space-between;">
        <h3 style="margin:0;font-size:16px;font-weight:600;">📚 知识浏览</h3>
        <button onclick="document.getElementById('va-kb-modal').remove()" style="background:none;border:none;font-size:20px;cursor:pointer;color:#94A3B8;">✕</button>
      </div>
      <div style="padding:12px 20px;"><input type="text" id="va-kb-search" placeholder="🔍 搜索知识..." style="width:100%;padding:8px 12px;border:1px solid #E2E8F0;border-radius:6px;font-size:13px;" oninput="vaFilterKnowledge()"></div>
      <div id="va-kb-list" style="flex:1;overflow-y:auto;padding:0 20px 16px;"><div style="text-align:center;padding:40px;color:var(--text-light);">⏳ 加载中...</div></div>
      <div style="padding:12px 20px;border-top:1px solid #E2E8F0;display:flex;gap:8px;justify-content:flex-end;">
        <button class="btn btn-secondary btn-sm" onclick="document.getElementById('va-kb-modal').remove()">取消</button>
        <button class="btn btn-primary btn-sm" onclick="vaBindSelected('${roleId}')">绑定选中</button>
      </div>
    </div>`;
    document.body.appendChild(modal);

    // 加载知识列表
    loadKnowledgeList();
  };

  async function loadKnowledgeList() {
    const list = document.getElementById('va-kb-list');
    if (!list) return;
    let items = [];
    const KB_API = 'http://localhost:3099/api/public';
    try {
      const r1 = await fetch(KB_API + '/packages');
      if (r1.ok) {
        const kbs = await r1.json();
        for (const kb of kbs) {
          const pid = kb.package_id || kb.id;
          const r2 = await fetch(`${KB_API}/packages/${pid}/manifest`);
          if (r2.ok) {
            const manifest = await r2.json();
            (manifest.documents || []).forEach(f => items.push({ ...f, kb_name: kb.name || pid, kb_id: pid }));
          }
        }
      }
    } catch(e) {}
    window._vaKnowledgeCache = items;
    renderKnowledgeItems(items);
  }

  function renderKnowledgeItems(items) {
    const list = document.getElementById('va-kb-list');
    if (!list) return;
    if (items.length === 0) {
      list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-light);">📭 知识库暂无可浏览的文档<br><span style="font-size:12px;">请在 Knowledge Workbench 中导入文档</span></div>';
      return;
    }
    const typeColors = { note: '#3B82F6', reference: '#22C55E', decision: '#F59E0B', thesis: '#8B5CF6', summary: '#EC4899' };
    list.innerHTML = items.map(k => {
      const tc = typeColors[k.type] || '#94A3B8';
      const tags = (k.tags||[]).slice(0,3).map(t => `<span style="background:#F1F5F9;color:#64748B;padding:1px 6px;border-radius:4px;font-size:10px;">${t}</span>`).join('');
      const summary = (k.summary||'').slice(0,80);
      return `<label style="display:flex;align-items:flex-start;gap:8px;padding:10px 12px;border-bottom:1px solid #F1F5F9;cursor:pointer;border-radius:6px;margin-bottom:2px;" onmouseenter="this.style.background='#F8FAFC'" onmouseleave="this.style.background=''">
        <input type="checkbox" value="${k.id}" class="va-kb-check" style="accent-color:var(--accent,#0EA5E9);margin-top:3px;">
        <div style="flex:1;min-width:0;">
          <div style="display:flex;align-items:center;gap:6px;">
            <span style="font-size:13px;font-weight:500;">${k.filename||k.title||'未命名'}</span>
            <span style="background:${tc}18;color:${tc};padding:1px 6px;border-radius:4px;font-size:10px;flex-shrink:0;">${k.type||'unknown'}</span>
          </div>
          ${summary ? `<div style="font-size:11px;color:#94A3B8;margin-top:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${summary}</div>` : ''}
          ${tags ? `<div style="margin-top:4px;display:flex;gap:4px;flex-wrap:wrap;">${tags}</div>` : ''}
          <div style="font-size:10px;color:#CBD5E0;margin-top:2px;">📁 ${k.kb_name||'knowledge-eve'}</div>
        </div>
      </label>`;
    }).join('');
  }

  window.vaFilterKnowledge = function() {
    const q = (document.getElementById('va-kb-search')?.value||'').toLowerCase();
    const items = window._vaKnowledgeCache || [];
    renderKnowledgeItems(items.filter(k => (k.title||k.filename||'').toLowerCase().includes(q) || (k.tags||[]).some(t=>t.toLowerCase().includes(q))));
  };

  window.vaBindSelected = async function(roleId) {
    const checks = document.querySelectorAll('.va-kb-check:checked');
    if (checks.length === 0) { showToast('请先选中知识', 'warning'); return; }
    let ok = 0;
    for (const c of checks) {
      try {
        await fetch(`http://localhost:8000/role-assets/${roleId}/knowledge`, {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({ knowledge_object_id: c.value, title: c.getAttribute('data-filename')||c.value, type: 'reference' })
        });
        ok++;
      } catch(e) {}
    }
    document.getElementById('va-kb-modal')?.remove();
    // 刷新 L3 展示
    if (ok > 0) {
      const refs = await fetch(`http://localhost:8000/role-assets/${roleId}/knowledge`).then(r=>r.json()).catch(()=>[]);
      const listEl = document.getElementById('ef-knowledge-list');
      if (listEl) {
        listEl.innerHTML = refs.length === 0
          ? '<div style="color:var(--text-light);font-size:13px;padding:8px 0;">暂未绑定知识</div>'
          : refs.map(k => `<div class="knowledge-item" style="cursor:default;border-color:var(--accent);background:rgba(14,165,233,0.03);"><div class="check" style="background:var(--accent);border-color:var(--accent);color:#fff;font-size:10px;">✓</div><div class="knowledge-info"><div class="knowledge-title">${k.title||k.knowledge_object_id}</div><div class="knowledge-meta"><span class="tag green">${k.type||'knowledge'}</span></div></div></div>`).join('');
      }
      appState.tempKnowledgeSelection = refs.map(k => k.knowledge_object_id);
    }
    showToast(`已绑定 ${ok} 条知识`, 'success');
  };

  // ═══════════════════ 8. 角色列表页 + 搜索状态 ═══════════════════
  window.vaFilterRoles = function() {
    const q = (document.getElementById('va-role-search')?.value||'').toLowerCase();
    document.querySelectorAll('.role-card').forEach(c => {
      c.style.display = (c.querySelector('.role-card-title')?.textContent||'').toLowerCase().includes(q) ? '' : 'none';
    });
  };

// ═══════════════════ 9. 编辑页注入「浏览知识」按钮 ═══════════════════
  const origRenderEdit = window.renderRoleEdit;
  if (origRenderEdit) {
    window.renderRoleEdit = function(roleId) {
      origRenderEdit(roleId);
      setTimeout(() => {
        const container = document.getElementById('roleEditBody') || document.getElementById('roleEditKnowledge');
        if (!container) return;
        const btn = document.createElement('button');
        btn.className = 'btn btn-secondary';
        btn.textContent = '📚 浏览知识库';
        btn.style.cssText = 'margin-top:8px;';
        btn.onclick = () => window.openKnowledgeBrowser(roleId || '');
        // 插入到知识区域
        const knowledgeSection = container.querySelector('.form-group')?.parentElement;
        if (knowledgeSection) knowledgeSection.appendChild(btn);
        else container.appendChild(btn);
      }, 200);
    };
  }

})();