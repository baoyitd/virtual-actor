import { ArrowRight, CheckCircle2, Plus, Search, ShieldAlert, TestTube2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, briefingStatusText, categoryText, outputModeText, outputTypeText, statusText, type RoleListItem } from '../api';

const STATUS_FILTERS = [
  { key: '', label: '全部状态' },
  { key: 'draft', label: '草稿' },
  { key: 'test', label: '测试中' },
  { key: 'published', label: '已发布' },
  { key: 'archived', label: '已归档' },
];

const CATEGORY_FILTERS = [
  { key: '', label: '全分类' },
  ...Object.entries(categoryText).map(([key, label]) => ({ key, label })),
];

export function RoleList() {
  const [roles, setRoles] = useState<RoleListItem[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async (status = statusFilter, category = categoryFilter) => {
    setLoading(true);
    setError('');
    try {
      const items = await api.listRoles({
        status: status || undefined,
        category: category || undefined,
      });
      setRoles(items);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载角色资产失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load('', '');
  }, []);

  const filtered = useMemo(() => {
    const keyword = search.trim().toLowerCase();
    if (!keyword) return roles;
    return roles.filter(item =>
      `${item.role_name} ${item.bio} ${item.summary} ${item.tags.join(' ')}`.toLowerCase().includes(keyword),
    );
  }, [roles, search]);

  const summary = useMemo(() => ({
    total: roles.length,
    published: roles.filter(item => item.published_version_id && item.status !== 'archived').length,
    testing: roles.filter(item => item.status === 'test').length,
    briefingReady: roles.filter(item => item.briefing_status === 'fresh').length,
  }), [roles]);

  const applyFilters = (status: string, category: string) => {
    setStatusFilter(status);
    setCategoryFilter(category);
    load(status, category);
  };

  return (
    <section className="page">
      <div className="page-head">
        <div>
          <p className="eyebrow">v0.5 Workbench</p>
          <h1>角色资产工作区</h1>
          <p className="subtle">
            围绕 L1-L4 角色定义、使用前说明与调用预览、治理发布和外供复用，统一管理企业数字角色资产。
          </p>
        </div>
        <div className="button-row">
          <Link to="/create" className="primary-btn"><Plus size={16} />新建角色</Link>
        </div>
      </div>

      <div className="metric-row">
        <div>
          <strong>{summary.total}</strong>
          <span>角色总数</span>
        </div>
        <div>
          <strong>{summary.published}</strong>
          <span>已发布版本</span>
        </div>
        <div>
          <strong>{summary.testing}</strong>
          <span>测试态角色</span>
        </div>
        <div>
          <strong>{summary.briefingReady}</strong>
          <span>说明卡已保存</span>
        </div>
      </div>

      <div className="toolbar">
        <div className="toolbar-filter-group">
          <div className="segmented">
            {STATUS_FILTERS.map(item => (
              <button
                key={item.key || 'all-status'}
                className={statusFilter === item.key ? 'active' : ''}
                onClick={() => applyFilters(item.key, categoryFilter)}
              >
                {item.label}
              </button>
            ))}
          </div>
          <select className="category-select" value={categoryFilter} onChange={e => applyFilters(statusFilter, e.target.value)}>
            {CATEGORY_FILTERS.map(item => (
              <option key={item.key || 'all-category'} value={item.key}>{item.label}</option>
            ))}
          </select>
        </div>

        <label className="search-box">
          <Search size={16} />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="搜索角色名称、职责、标签"
          />
        </label>
      </div>

      {error && <div className="alert error"><ShieldAlert size={16} />{error}</div>}
      {loading && <div className="page-loading">正在加载角色资产...</div>}

      {!loading && filtered.length === 0 && (
        <div className="empty-state">当前没有符合筛选条件的角色资产。</div>
      )}

      {!loading && filtered.length > 0 && (
        <div className="role-card-grid">
          {filtered.map(role => (
            <article key={role.role_id} className="role-card">
              <div className="role-card-header">
                <div>
                  <Link to={`/roles/${role.role_id}`} className="entity-title">{role.role_name}</Link>
                  <p>{role.bio}</p>
                </div>
                <span className={`status-pill ${role.status}`}>{statusText[role.status]}</span>
              </div>

              <div className="tag-line">
                <span>{categoryText[role.category] || role.category}</span>
                <span>{outputModeText[role.output_mode]}</span>
                {role.output_type && <span className="tag-pill accent">{outputTypeText[role.output_type] || role.output_type}</span>}
                <span>{briefingStatusText[role.briefing_status]}</span>
              </div>

              <div className="role-card-body">
                <div className="role-card-row">
                  <strong>职责摘要</strong>
                  <span>{role.summary || '待补齐核心职责'}</span>
                </div>
                <div className="role-card-row">
                  <strong>Owner</strong>
                  <span>{role.owner || '待补齐'}</span>
                </div>
                <div className="role-card-row">
                  <strong>业务域</strong>
                  <span>{role.business_domain || '待补齐'}</span>
                </div>
                <div className="role-card-row">
                  <strong>测试记录</strong>
                  <span>{role.has_test_record ? `${role.test_run_count} 次` : '暂无'}</span>
                </div>
              </div>

              <div className="role-card-foot">
                <div className="role-card-flags">
                  {role.briefing_status === 'fresh' && <span className="flag success"><CheckCircle2 size={14} />说明卡已确认</span>}
                  {role.status === 'test' && <span className="flag warning"><TestTube2 size={14} />可进入试用与测试</span>}
                  {!role.recommend_pool_eligible && <span className="flag muted">AI 推荐池待补齐</span>}
                  {role.legacy_incomplete && <span className="flag muted">legacy 待补齐</span>}
                </div>
                <div className="button-row">
                  <Link className="secondary-btn small-btn" to={`/roles/${role.role_id}/edit`}>继续编辑</Link>
                  <Link className="secondary-btn small-btn" to={`/roles/${role.role_id}/governance`}>治理与发布</Link>
                  {role.published_version_id && role.status !== 'archived' && (
                    <Link className="primary-btn small-btn" to={'/roles/' + role.role_id + '/exports'}>
                      正式消费
                      <ArrowRight size={14} />
                    </Link>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
