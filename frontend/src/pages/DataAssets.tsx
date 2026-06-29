import { Database, Plus, Save, Search, ShieldAlert } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { api, type DataAssetSummary } from '../api';

type AssetForm = {
  display_name: string;
  datasource_ref: string;
  database_name: string;
  table_name: string;
  scope_summary: string;
  freshness: string;
  owner_team: string;
  status: string;
};

const EMPTY_FORM: AssetForm = {
  display_name: '',
  datasource_ref: '',
  database_name: '',
  table_name: '',
  scope_summary: '',
  freshness: '',
  owner_team: '',
  status: 'active',
};

export function DataAssetsPage() {
  const [assets, setAssets] = useState<DataAssetSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [form, setForm] = useState<AssetForm>(EMPTY_FORM);
  const [statusFilter, setStatusFilter] = useState('');
  const [keyword, setKeyword] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const load = async (status = statusFilter) => {
    try {
      const result = await api.listDataAssets(status || undefined);
      setAssets(result);
      if (selectedId) {
        const selected = result.find(item => item.id === selectedId);
        if (selected) {
          hydrateForm(selected);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载数据资产失败');
    }
  };

  useEffect(() => {
    load('');
  }, []);

  const hydrateForm = (asset: DataAssetSummary) => {
    setSelectedId(asset.id);
    setForm({
      display_name: asset.display_name,
      datasource_ref: asset.datasource_ref,
      database_name: asset.database_name,
      table_name: asset.table_name,
      scope_summary: asset.scope_summary,
      freshness: asset.freshness || '',
      owner_team: asset.owner_team || '',
      status: asset.status,
    });
  };

  const resetForm = () => {
    setSelectedId(null);
    setForm(EMPTY_FORM);
  };

  const filtered = useMemo(() => {
    const lowered = keyword.trim().toLowerCase();
    if (!lowered) return assets;
    return assets.filter(item => `${item.display_name} ${item.scope_summary} ${item.table_name}`.toLowerCase().includes(lowered));
  }, [assets, keyword]);

  const save = async () => {
    setSaving(true);
    setError('');
    try {
      if (selectedId) {
        const updated = await api.updateDataAsset(selectedId, {
          ...form,
          freshness: form.freshness || null,
          owner_team: form.owner_team || null,
        });
        hydrateForm(updated);
      } else {
        const created = await api.createDataAsset({
          ...form,
          freshness: form.freshness || null,
          owner_team: form.owner_team || null,
        });
        hydrateForm(created);
      }
      await load(statusFilter);
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存数据资产失败');
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="page">
      <div className="page-head">
        <div>
          <p className="eyebrow">Data Capability Registry</p>
          <h1>数据资产管理</h1>
          <p className="subtle">管理员在这里维护可被角色版本绑定的数据资产项；角色页只选择绑定，不在现场创建。</p>
        </div>
        <button className="primary-btn" onClick={resetForm}><Plus size={16} />新增数据资产</button>
      </div>

      {error && <div className="alert error"><ShieldAlert size={16} />{error}</div>}

      <div className="asset-management-grid">
        <aside className="detail-section asset-list-panel">
          <div className="section-title-row">
            <h2><Database size={16} />资产列表</h2>
            <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); load(e.target.value); }}>
              <option value="">全部状态</option>
              <option value="active">启用</option>
              <option value="inactive">停用</option>
            </select>
          </div>

          <label className="search-box asset-search-box">
            <Search size={16} />
            <input value={keyword} onChange={e => setKeyword(e.target.value)} placeholder="搜索展示名称、范围说明、表名" />
          </label>

          <div className="asset-list">
            {filtered.map(asset => (
              <button key={asset.id} className={`asset-list-item ${selectedId === asset.id ? 'active' : ''}`} onClick={() => hydrateForm(asset)}>
                <strong>{asset.display_name}</strong>
                <small>{asset.database_name}.{asset.table_name}</small>
                <span>{asset.scope_summary}</span>
                <em>{asset.status === 'active' ? '启用' : '停用'}</em>
              </button>
            ))}
            {filtered.length === 0 && <div className="empty-state">当前没有数据资产项。</div>}
          </div>
        </aside>

        <section className="form-section">
          <div className="section-title-row">
            <div>
              <h2>{selectedId ? '编辑数据资产' : '新增数据资产'}</h2>
              <p className="section-intro">最小必填仅保留 display_name / datasource_ref / database_name / table_name / scope_summary。</p>
            </div>
            <button className="primary-btn" onClick={save} disabled={saving}>
              <Save size={16} />
              {saving ? '保存中...' : '保存数据资产'}
            </button>
          </div>

          <div className="two-col">
            <label className="field-block">
              <span className="field-label">展示名称</span>
              <input value={form.display_name} onChange={e => setForm(prev => ({ ...prev, display_name: e.target.value }))} />
            </label>
            <label className="field-block">
              <span className="field-label">数据源引用</span>
              <input value={form.datasource_ref} onChange={e => setForm(prev => ({ ...prev, datasource_ref: e.target.value }))} placeholder="如：warehouse.main" />
            </label>
            <label className="field-block">
              <span className="field-label">数据库名</span>
              <input value={form.database_name} onChange={e => setForm(prev => ({ ...prev, database_name: e.target.value }))} />
            </label>
            <label className="field-block">
              <span className="field-label">表名</span>
              <input value={form.table_name} onChange={e => setForm(prev => ({ ...prev, table_name: e.target.value }))} />
            </label>
          </div>

          <label className="field-block">
            <span className="field-label">范围说明</span>
            <textarea rows={5} value={form.scope_summary} onChange={e => setForm(prev => ({ ...prev, scope_summary: e.target.value }))} placeholder="可读取【业务对象/指标】，粒度到【组织/周期】；不包含【明显不含范围】。" />
          </label>

          <div className="three-col">
            <label className="field-block">
              <span className="field-label">时效说明（可选）</span>
              <input value={form.freshness} onChange={e => setForm(prev => ({ ...prev, freshness: e.target.value }))} placeholder="如：T+1 / 每日 08:00 更新" />
            </label>
            <label className="field-block">
              <span className="field-label">Owner Team（可选）</span>
              <input value={form.owner_team} onChange={e => setForm(prev => ({ ...prev, owner_team: e.target.value }))} placeholder="如：经营数据中台" />
            </label>
            <label className="field-block">
              <span className="field-label">状态</span>
              <select value={form.status} onChange={e => setForm(prev => ({ ...prev, status: e.target.value }))}>
                <option value="active">启用</option>
                <option value="inactive">停用</option>
              </select>
            </label>
          </div>
        </section>
      </div>
    </section>
  );
}
