import { Archive, CheckCircle2, Clock3, Edit3, Plus, Search, ShieldAlert, TestTube2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, statusText } from '../api';
import type { RoleListItem } from '../api';

const filters = [
  { key: '', label: '全部' },
  { key: 'draft', label: '草稿' },
  { key: 'test', label: '测试中' },
  { key: 'published', label: '已发布' },
  { key: 'archived', label: '已归档' },
];

function statusIcon(status: string) {
  if (status === 'published') return <CheckCircle2 size={15} />;
  if (status === 'test') return <TestTube2 size={15} />;
  if (status === 'archived') return <Archive size={15} />;
  return <Edit3 size={15} />;
}

export function RoleList() {
  const [roles, setRoles] = useState<RoleListItem[]>([]);
  const [filter, setFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async (status = filter) => {
    setLoading(true);
    setError('');
    try {
      setRoles(await api.listRoles(status || undefined));
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载角色失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(''); }, []);

  const filtered = useMemo(() => roles.filter(r => {
    const keyword = search.trim().toLowerCase();
    if (!keyword) return true;
    return `${r.role_name} ${r.bio} ${r.tags.join(' ')}`.toLowerCase().includes(keyword);
  }), [roles, search]);

  const counts = useMemo(() => ({
    total: roles.length,
    published: roles.filter(r => r.status === 'published').length,
    test: roles.filter(r => r.status === 'test').length,
    draft: roles.filter(r => r.status === 'draft').length,
  }), [roles]);

  return (
    <section className="page">
      <div className="page-head">
        <div>
          <p className="eyebrow">角色资产</p>
          <h1>企业虚拟专家管理</h1>
          <p className="subtle">统一创建、测试、绑定知识并发布可调用的角色资产。</p>
        </div>
        <Link to="/create" className="primary-btn"><Plus size={17} />新建角色</Link>
      </div>

      <div className="metric-row">
        <div><strong>{counts.total}</strong><span>角色总数</span></div>
        <div><strong>{counts.published}</strong><span>已发布</span></div>
        <div><strong>{counts.test}</strong><span>测试中</span></div>
        <div><strong>{counts.draft}</strong><span>草稿</span></div>
      </div>

      <div className="toolbar">
        <div className="segmented">
          {filters.map(item => (
            <button key={item.key || 'all'} className={filter === item.key ? 'active' : ''} onClick={() => { setFilter(item.key); load(item.key); }}>
              {item.label}
            </button>
          ))}
        </div>
        <label className="search-box"><Search size={17} /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="搜索角色名称、简介、标签" /></label>
      </div>

      {error && <div className="alert error"><ShieldAlert size={17} />{error}</div>}
      {loading && <div className="page-loading">正在加载角色资产...</div>}
      {!loading && filtered.length === 0 && <div className="empty-state">暂无符合条件的角色资产</div>}
      {!loading && filtered.length > 0 && (
        <div className="data-table">
          <div className="table-row table-head-row">
            <span>角色</span><span>状态</span><span>模型</span><span>测试</span><span>更新时间</span><span>操作</span>
          </div>
          {filtered.map(role => (
            <div className="table-row" key={role.role_id}>
              <div>
                <Link to={`/roles/${role.role_id}`} className="entity-title">{role.role_name}</Link>
                <p>{role.bio || '暂无简介'}</p>
                <div className="tag-line">{role.tags.map(tag => <span key={tag}>{tag}</span>)}</div>
              </div>
              <span className={`status-pill ${role.status}`}>{statusIcon(role.status)}{statusText[role.status] || role.status}</span>
              <span>{role.model_binding?.model_name || '未配置'}</span>
              <span>{role.has_test_record ? `${role.test_run_count} 次` : '未测试'}</span>
              <span>{role.updated_at ? new Date(role.updated_at).toLocaleString('zh-CN') : '-'}</span>
              <span className="row-actions">
                <Link to={`/roles/${role.role_id}/edit`}>编辑</Link>
                <Link to={`/roles/${role.role_id}/test`}><Clock3 size={14} />测试</Link>
              </span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
