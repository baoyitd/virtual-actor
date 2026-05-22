import { Archive, ArrowLeft, CheckCircle2, Edit3, Send, ShieldAlert, TestTube2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, statusText } from '../api';
import type { RoleDetail as RoleDetailType, VersionItem } from '../api';

export function RoleDetail() {
  const { id } = useParams<{ id: string }>();
  const [role, setRole] = useState<RoleDetailType | null>(null);
  const [versions, setVersions] = useState<VersionItem[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    if (!id) return;
    setLoading(true);
    setError('');
    try {
      const [r, v] = await Promise.all([api.getRole(id), api.versions(id)]);
      setRole(r);
      setVersions(v);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载角色详情失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const action = async (type: 'test' | 'publish' | 'archive') => {
    if (!id) return;
    setError('');
    try {
      if (type === 'test') await api.toTest(id);
      if (type === 'publish') await api.publish(id);
      if (type === 'archive') await api.archive(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : '操作失败');
    }
  };

  if (loading) return <div className="page-loading">正在加载角色详情...</div>;
  if (!role) return <div className="empty-state">角色不存在或无权访问</div>;

  return (
    <section className="page">
      <div className="page-head compact">
        <div>
          <Link to="/" className="back-link"><ArrowLeft size={16} />返回角色列表</Link>
          <h1>{role.name}</h1>
          <p className="subtle">{role.bio}</p>
        </div>
        <div className="button-row">
          <Link className="secondary-btn" to={`/roles/${role.role_id}/edit`}><Edit3 size={16} />编辑</Link>
          <Link className="secondary-btn" to={`/roles/${role.role_id}/test`}><TestTube2 size={16} />测试</Link>
          {role.status === 'draft' && <button className="secondary-btn" onClick={() => action('test')}><Send size={16} />进入测试</button>}
          {role.status === 'test' && <button className="primary-btn" onClick={() => action('publish')}><CheckCircle2 size={16} />发布</button>}
          {role.status === 'published' && <button className="secondary-btn" onClick={() => action('archive')}><Archive size={16} />归档</button>}
        </div>
      </div>
      {error && <div className="alert error"><ShieldAlert size={17} />{error}</div>}

      <div className="detail-layout">
        <section className="detail-main">
          <div className="info-band">
            <span className={`status-pill ${role.status}`}>{statusText[role.status] || role.status}</span>
            <span>当前版本：{role.role_version_id || '未生成'}</span>
            <span>测试次数：{role.test_run_count}</span>
            <span>最新评分：{role.latest_test_rating || '-'}</span>
          </div>

          <section className="detail-section"><h2>心智配置</h2>
            <dl>
              <dt>身份背景</dt><dd>{role.identity_background || '-'}</dd>
              <dt>核心立场</dt><dd>{role.point_of_view || '-'}</dd>
              <dt>决策风格</dt><dd>{role.decision_style || '-'}</dd>
              <dt>职责边界</dt><dd>{role.responsibility_boundary || '-'}</dd>
              <dt>表达风格</dt><dd>{role.speaking_style || '-'}</dd>
            </dl>
          </section>

          <section className="detail-section"><h2>知识绑定</h2>
            {role.knowledge_refs.length === 0 ? <p className="subtle">尚未绑定知识，发布前需要至少绑定 1 条。</p> : (
              <div className="knowledge-summary">
                {role.knowledge_refs.map(ref => <div key={ref.id}><strong>{ref.title || ref.knowledge_object_id}</strong><span>{ref.type || 'knowledge'} · {ref.knowledge_version_id || '未标记版本'}</span></div>)}
              </div>
            )}
          </section>

          <section className="detail-section"><h2>能力与模型</h2>
            <dl>
              <dt>协作模式</dt><dd>{role.collaboration_mode || '-'}</dd>
              <dt>能力边界</dt><dd>{role.capability_boundary || '-'}</dd>
              <dt>模型</dt><dd>{role.model_binding ? `${role.model_binding.model_provider} / ${role.model_binding.model_name}` : '-'}</dd>
              <dt>参数</dt><dd>{role.model_binding ? `temperature=${role.model_binding.temperature}, max_tokens=${role.model_binding.max_tokens}` : '-'}</dd>
            </dl>
          </section>
        </section>

        <aside className="detail-aside">
          <section className="detail-section"><h2>版本记录</h2>
            <div className="timeline">
              {versions.map(version => (
                <div key={version.role_version_id}>
                  <strong>v{version.version_number}</strong>
                  <span>{statusText[version.status] || version.status}</span>
                  <small>{version.published_at ? new Date(version.published_at).toLocaleString('zh-CN') : '未发布'}</small>
                </div>
              ))}
            </div>
          </section>
          <section className="detail-section"><h2>发布追溯</h2>
            {role.validated_knowledge_versions.length === 0 ? <p className="subtle">发布后会记录知识版本追溯。</p> : role.validated_knowledge_versions.map(item => <p key={`${item.knowledge_object_id}-${item.knowledge_version_id}`}>{item.knowledge_object_id}<br /><span>{item.knowledge_version_id}</span></p>)}
          </section>
        </aside>
      </div>
    </section>
  );
}
