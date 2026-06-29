import { ArrowLeft } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, briefingStatusText, outputModeText, outputTypeText, statusText, type RoleDetail, type RoleVersionPublicResponse, type VersionItem } from '../api';

export function RoleVersions() {
  const { id = '' } = useParams<{ id: string }>();
  const [role, setRole] = useState<RoleDetail | null>(null);
  const [versions, setVersions] = useState<VersionItem[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<RoleVersionPublicResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([api.getRole(id), api.listVersions(id)])
      .then(([detail, items]) => {
        setRole(detail);
        setVersions(items);
      })
      .catch(err => setError(err instanceof Error ? err.message : '加载版本记录失败'))
      .finally(() => setLoading(false));
  }, [id]);

  const loadVersion = async (versionId: string) => {
    try {
      setSelectedVersion(await api.getVersionDetail(versionId));
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载版本详情失败');
    }
  };

  if (loading) return <div className="page-loading">正在加载版本记录...</div>;
  if (!role) return <div className="empty-state">当前角色不存在。</div>;

  return (
    <section className="page">
      <div className="page-head compact">
        <div>
          <Link to={`/roles/${role.role_id}`} className="back-link"><ArrowLeft size={16} />返回角色概览</Link>
          <h1>版本记录</h1>
          <p className="subtle">查看角色版本、发布状态以及对外公开可见的版本内容。</p>
        </div>
      </div>

      {error && <div className="alert error">{error}</div>}

      <div className="version-layout">
        <section className="detail-section">
          <h2>{role.name} 的版本列表</h2>
          <div className="record-list">
            {versions.map(version => (
              <button key={version.role_version_id} className={`record-item selectable ${selectedVersion?.role_version_id === version.role_version_id ? 'active' : ''}`} onClick={() => loadVersion(version.role_version_id)}>
                <strong>v{version.version_number}</strong>
                <span>{statusText[version.status] || version.status}</span>
                <small>{version.published_at || '未发布'}</small>
              </button>
            ))}
            {versions.length === 0 && <div className="empty-state">当前还没有版本记录。</div>}
          </div>
        </section>

        <aside className="version-detail-panel">
          <h2>版本内容</h2>
          {selectedVersion ? (
            <div className="version-detail-grid">
              <div className="overview-card">
                <strong>版本 ID</strong>
                <span>{selectedVersion.role_version_id}</span>
                <small>{selectedVersion.name}</small>
              </div>
              <div className="overview-card">
                <strong>输出方式</strong>
                <span>{outputModeText[selectedVersion.output_mode]}</span>
                <small>{selectedVersion.output_type ? (outputTypeText[selectedVersion.output_type] || selectedVersion.output_type) : '自由输出'}</small>
              </div>
              <div className="overview-card">
                <strong>核心职责</strong>
                <span>{selectedVersion.main_duty_cluster || '待补齐'}</span>
              </div>
              <div className="overview-card">
                <strong>分析视角</strong>
                <span>{selectedVersion.point_of_view || '待补齐'}</span>
              </div>
              <div className="overview-card">
                <strong>知识边界</strong>
                <span>{selectedVersion.knowledge_boundary || '当前未单独声明知识边界'}</span>
              </div>
              <div className="overview-card">
                <strong>说明卡状态</strong>
                <span>{briefingStatusText[selectedVersion.briefing.status] || selectedVersion.briefing.status}</span>
              </div>
              <div className="overview-card">
                <strong>知识引用</strong>
                <span>{selectedVersion.knowledge_refs.length > 0 ? `${selectedVersion.knowledge_refs.length} 篇文档已绑定` : '未绑定知识'}</span>
              </div>
              <div className="overview-card">
                <strong>数据资产</strong>
                <span>{selectedVersion.data_asset_bindings.length > 0 ? `${selectedVersion.data_asset_bindings.length} 条资产已绑定` : '未绑定数据资产'}</span>
              </div>
              <div className="overview-card">
                <strong>验证记录</strong>
                <span>{selectedVersion.has_test_record ? `已完成 ${selectedVersion.test_run_count} 次测试` : '当前暂无测试记录'}</span>
              </div>
            </div>
          ) : (
            <div className="empty-state">选择一个版本查看详情。</div>
          )}
        </aside>
      </div>
    </section>
  );
}
