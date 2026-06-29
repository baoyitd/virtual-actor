import { ArrowLeft, CheckCircle2, ExternalLink, Package2, Save, ShieldAlert, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  api,
  categoryText,
  statusText,
  visibilityText,
  type RoleDetail,
} from '../api';
import { RoleStageNav } from '../components/RoleStageNav';

type BusinessDomain = { id: string; name: string };
type EnterpriseRole = { id: string; business_domain_id: string; name: string };
type StaffMember = { id: string; name: string; department: string | null };

export function RoleGovernancePage() {
  const { id = '' } = useParams();
  const [role, setRole] = useState<RoleDetail | null>(null);
  const [businessDomains, setBusinessDomains] = useState<BusinessDomain[]>([]);
  const [enterpriseRoles, setEnterpriseRoles] = useState<EnterpriseRole[]>([]);
  const [staffList, setStaffList] = useState<StaffMember[]>([]);
  const [form, setForm] = useState({
    owner: '',
    business_domain: '',
    category: '自定义',
    visibility: '内部',
    maintainer: '',
    tagsText: '',
    enterpriseRoleIds: [] as string[],
  });
  const [tagInput, setTagInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [publishSuccess, setPublishSuccess] = useState(false);
  const [showArchiveConfirm, setShowArchiveConfirm] = useState(false);

  const load = async () => {
    try {
      setError('');
      const [detail, domains, staff] = await Promise.all([
        api.getRole(id),
        api.listBusinessDomains(),
        api.listStaff(),
      ]);
      setRole(detail);
      setBusinessDomains(domains);
      setStaffList(staff);

      const selectedDomainId = domains.find(d => d.name === detail.business_domain)?.id || '';
      if (selectedDomainId) {
        const roles = await api.listEnterpriseRoles(selectedDomainId);
        setEnterpriseRoles(roles);
      }

      const savedRoleIds = (detail.enterprise_role_mapping || []) as string[];

      setForm({
        owner: detail.owner || '',
        business_domain: selectedDomainId,
        category: detail.category || '自定义',
        visibility: detail.visibility || '内部',
        maintainer: detail.maintainer || '',
        tagsText: detail.tags.join('、'),
        enterpriseRoleIds: savedRoleIds,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载治理页失败');
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const onBusinessDomainChange = async (domainId: string) => {
    setForm(prev => ({ ...prev, business_domain: domainId, enterpriseRoleIds: [] }));
    if (domainId) {
      const roles = await api.listEnterpriseRoles(domainId);
      setEnterpriseRoles(roles);
    } else {
      setEnterpriseRoles([]);
    }
  };

  const toggleEnterpriseRole = (roleId: string) => {
    setForm(prev => ({
      ...prev,
      enterpriseRoleIds: prev.enterpriseRoleIds.includes(roleId)
        ? prev.enterpriseRoleIds.filter(rid => rid !== roleId)
        : [...prev.enterpriseRoleIds, roleId],
    }));
  };

  const addTag = () => {
    const tag = tagInput.trim().replace(/[、,\n]/g, '');
    if (!tag) return;
    const currentTags = form.tagsText.split(/[、,]/).map(t => t.trim()).filter(Boolean);
    if (!currentTags.includes(tag)) {
      setForm(prev => ({ ...prev, tagsText: [...currentTags, tag].join('、') }));
    }
    setTagInput('');
  };

  const removeTag = (tag: string) => {
    const currentTags = form.tagsText.split(/[、,]/).map(t => t.trim()).filter(Boolean);
    setForm(prev => ({ ...prev, tagsText: currentTags.filter(t => t !== tag).join('、') }));
  };

  const buildUpdatePayload = () => {
    const domainName = businessDomains.find(d => d.id === form.business_domain)?.name || '';
    const selectedRoles = enterpriseRoles
      .filter(r => form.enterpriseRoleIds.includes(r.id))
      .map(r => r.name);
    return {
      owner: form.owner,
      business_domain: domainName || null,
      category: form.category,
      visibility: form.visibility,
      maintainer: form.maintainer || null,
      tags: form.tagsText.split(/[、,\n]/).map(item => item.trim()).filter(Boolean),
      enterprise_role_mapping: selectedRoles,
    };
  };

  const saveAndPublish = async () => {
    if (!role) return;
    setSaving(true);
    setError('');
    setPublishSuccess(false);
    try {
      await api.updateRole(role.role_id, buildUpdatePayload());
      const detail = await api.publish(role.role_id);
      setRole(detail);
      setPublishSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : '发布失败');
    } finally {
      setSaving(false);
    }
  };

  const saveOnly = async () => {
    if (!role) return;
    setSaving(true);
    setError('');
    try {
      const detail = await api.updateRole(role.role_id, buildUpdatePayload());
      setRole(detail);
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存治理项失败');
    } finally {
      setSaving(false);
    }
  };

  const confirmArchive = async () => {
    if (!role) return;
    setSaving(true);
    setError('');
    setShowArchiveConfirm(false);
    try {
      const detail = await api.archive(role.role_id);
      setRole(detail);
    } catch (err) {
      setError(err instanceof Error ? err.message : '归档失败');
    } finally {
      setSaving(false);
    }
  };

  if (!role) return <div className="page-loading">正在加载治理与发布...</div>;

  const currentTags = form.tagsText.split(/[、,]/).map(t => t.trim()).filter(Boolean);
  const selectedDomainName = businessDomains.find(d => d.id === form.business_domain)?.name || role.business_domain || '';
  const isPublished = role.status === 'published';
  const isArchived = role.status === 'archived';

  const publishReadinessItems = role.publish_readiness?.hard_requirements || [];
  const allReady = publishReadinessItems.every(item => item.status === 'met');

  return (
    <div className="page">
      <Link className="back-link" to={'/roles/' + role.role_id}><ArrowLeft size={16} />返回角色概览</Link>

      <div className="page-head">
        <div>
          <p className="eyebrow">Governance</p>
          <h1>治理与发布</h1>
          <p className="subtle">填写治理信息，确认发布前检查全部通过后，一键保存并发布。</p>
        </div>
      </div>

      {error && <div className="alert error"><ShieldAlert size={16} />{error}</div>}

      {publishSuccess && (
        <div className="alert success">
          <CheckCircle2 size={16} />
          <span>当前版本已发布成功。</span>
          <Link className="alert-link" to={'/roles/' + role.role_id + '/exports'}>前往外供与追溯生成导出包 →</Link>
        </div>
      )}

      {isArchived && (
        <div className="alert warning">
          当前角色已归档，不再参与活跃市场、正式消费和新外供。如需重新启用，请回 01 修改角色定义形成新的可编辑版本。
        </div>
      )}

      <div className="role-page-grid">
        <RoleStageNav roleId={role.role_id} />

        <div className="role-page-main">
          <div className="gov-status-bar">
            <strong>{role.name}</strong>
            <span className="sep">·</span>
            <span>状态 {statusText[role.status]}</span>
            <span className="sep">·</span>
            <span>版本 {role.role_version_id ? role.role_version_id.slice(0, 8) + '...' : '未生成'}</span>
            {role.published_version_id && (
              <>
                <span className="sep">·</span>
                <span>已发布 {role.published_version_id.slice(0, 8) + '...'}</span>
              </>
            )}
          </div>

          <section className="form-section">
            <div className="section-title-row">
              <div>
                <h2>治理主路径</h2>
                <p className="section-intro">这三项回答"谁负责 / 属于什么业务域 / 在平台里归到哪类资产"。</p>
              </div>
            </div>
            <div className="three-col">
              <label className="field-block">
                <span className="field-label">Owner</span>
                <select value={form.owner} onChange={e => setForm(prev => ({ ...prev, owner: e.target.value }))}>
                  <option value="">请选择</option>
                  {staffList.map(s => (
                    <option key={s.id} value={s.name}>{s.name}{s.department ? '（' + s.department + '）' : ''}</option>
                  ))}
                </select>
              </label>
              <label className="field-block">
                <span className="field-label">业务域</span>
                <select value={form.business_domain} onChange={e => onBusinessDomainChange(e.target.value)}>
                  <option value="">请选择</option>
                  {businessDomains.map(d => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </label>
              <label className="field-block">
                <span className="field-label">分类</span>
                <select value={form.category} onChange={e => setForm(prev => ({ ...prev, category: e.target.value }))}>
                  {Object.entries(categoryText).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </label>
            </div>
          </section>

          <section className="form-section">
            <div className="section-title-row">
              <div>
                <h2>补充治理项</h2>
                <p className="section-intro">治理补充项，不抢主路径。</p>
              </div>
              <Link className="text-link" to="/data-assets">
                <ExternalLink size={14} />
                数据资产管理
              </Link>
            </div>

            <div className="three-col">
              <label className="field-block">
                <span className="field-label">可见性</span>
                <select value={form.visibility} onChange={e => setForm(prev => ({ ...prev, visibility: e.target.value }))}>
                  {Object.entries(visibilityText).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </label>
              <label className="field-block">
                <span className="field-label">Maintainer</span>
                <select value={form.maintainer} onChange={e => setForm(prev => ({ ...prev, maintainer: e.target.value }))}>
                  <option value="">请选择</option>
                  {staffList.map(s => (
                    <option key={s.id} value={s.name}>{s.name}{s.department ? '（' + s.department + '）' : ''}</option>
                  ))}
                </select>
              </label>
              <label className="field-block">
                <span className="field-label">标签</span>
                <div className="tag-input-wrapper">
                  <div className="tag-chip-list">
                    {currentTags.map(tag => (
                      <span key={tag} className="tag-chip">
                        {tag}
                        <button type="button" onClick={() => removeTag(tag)} className="tag-chip-remove"><X size={12} /></button>
                      </span>
                    ))}
                    <input
                      className="tag-input"
                      value={tagInput}
                      onChange={e => setTagInput(e.target.value)}
                      onKeyDown={e => { if (e.key === 'Enter' || e.key === '、' || e.key === ',') { e.preventDefault(); addTag(); } }}
                      onBlur={addTag}
                      placeholder={currentTags.length === 0 ? '输入标签后回车' : '继续添加'}
                    />
                  </div>
                </div>
              </label>
            </div>

            <div className="field-block">
              <span className="field-label">企业实际角色映射（当前业务域：{selectedDomainName || '未选择'}）</span>
              {enterpriseRoles.length === 0 ? (
                <span className="muted-text">请先选择业务域，再选择对应的企业实际角色。</span>
              ) : (
                <div className="checkbox-grid">
                  {enterpriseRoles.map(r => (
                    <label key={r.id} className={'checkbox-card ' + (form.enterpriseRoleIds.includes(r.id) ? 'selected' : '')}>
                      <input
                        type="checkbox"
                        checked={form.enterpriseRoleIds.includes(r.id)}
                        onChange={() => toggleEnterpriseRole(r.id)}
                      />
                      <span>{r.name}</span>
                    </label>
                  ))}
                </div>
              )}
            </div>
          </section>

          <section className="detail-section">
            <div className="section-title-row">
              <div>
                <h2>发布前检查</h2>
                <p className="subtle">以下条件全部满足后才能发布当前版本。</p>
              </div>
              <Link className="text-link" to={'/roles/' + role.role_id + '/exports'}>
                <Package2 size={14} />
                查看外供与追溯
              </Link>
            </div>
            <div className="readiness-checklist">
              {publishReadinessItems.map(item => (
                <div key={item.key} className={'readiness-item ' + (item.status === 'met' ? 'met' : 'unmet')}>
                  <span className="readiness-dot" />
                  <div className="readiness-content">
                    <strong>{item.label}</strong>
                    {item.status === 'met' ? (
                      <small className="readiness-met-text">已满足</small>
                    ) : (
                      <small className="readiness-unmet-text">{item.message || '尚未满足'}</small>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="detail-section action-zone">
            <div className="button-row">
              <button className="secondary-btn" onClick={saveOnly} disabled={saving || isArchived}>
                <Save size={16} />
                仅保存
              </button>
              <button className="primary-btn" onClick={saveAndPublish} disabled={saving || isArchived || isPublished || !allReady}>
                <CheckCircle2 size={16} />
                {isPublished ? '当前版本已发布' : '保存并发布'}
              </button>
            </div>
            {isPublished && !isArchived && (
              <p className="subtle" style={{ marginTop: '8px' }}>
                当前版本已发布。如需发布新版本，请回 01 修改角色定义生成新草稿，经测试和说明卡确认后再来此处发布。
              </p>
            )}
            {!allReady && !isPublished && !isArchived && (
              <p className="subtle" style={{ marginTop: '8px' }}>
                仍有未满足的发布前检查项，请先补齐。
              </p>
            )}
          </section>

          <section className="detail-section">
            <h2>其他操作</h2>
            <div className="archive-zone">
              <div>
                <strong>归档当前角色</strong>
                <p className="subtle">归档后角色退出活跃市场，不再允许正式消费和生成新外供，历史记录保留。此操作不可逆。</p>
              </div>
              <button className="danger-btn" onClick={() => setShowArchiveConfirm(true)} disabled={isArchived}>
                归档
              </button>
            </div>
          </section>

          {showArchiveConfirm && (
            <div className="modal-overlay" onClick={() => setShowArchiveConfirm(false)}>
              <div className="modal-card" onClick={e => e.stopPropagation()}>
                <h3>确认归档</h3>
                <p>归档后，该角色将：</p>
                <ul>
                  <li>退出活跃市场，不再出现在角色列表中</li>
                  <li>不再允许正式消费和模拟外部调用</li>
                  <li>不再允许生成新的外供包</li>
                  <li>历史记录、已生成的外供包和回写记录保留可查</li>
                </ul>
                <p className="subtle">此操作不可逆。如需重新启用，需回 01 修改角色定义生成新版本。</p>
                <div className="modal-actions">
                  <button className="secondary-btn" onClick={() => setShowArchiveConfirm(false)}>取消</button>
                  <button className="danger-btn" onClick={confirmArchive} disabled={saving}>确认归档</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
