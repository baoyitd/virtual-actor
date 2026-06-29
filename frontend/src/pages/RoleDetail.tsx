import { ArrowLeft, ExternalLink, Package2, ShieldCheck, TestTube2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, briefingStatusText, outputModeText, outputTypeText, statusText, type RoleDetail as RoleDetailType } from '../api';
import { ReadinessPanelCard } from '../components/ReadinessPanelCard';
import { RoleBriefingCard } from '../components/RoleBriefingCard';
import { RoleStageNav } from '../components/RoleStageNav';

export function RoleDetail() {
  const { id = '' } = useParams();
  const [role, setRole] = useState<RoleDetailType | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getRole(id).then(setRole).catch(err => setError(err instanceof Error ? err.message : '加载失败'));
  }, [id]);

  if (error) return <div className="alert error">{error}</div>;
  if (!role) return <div className="page-loading">正在加载角色概览...</div>;

  return (
    <div className="page">
      <Link className="back-link" to="/"><ArrowLeft size={16} />返回角色列表</Link>

      <div className="page-head">
        <div>
          <p className="eyebrow">Role Overview</p>
          <h1>{role.name}</h1>
          <p className="subtle">{role.bio}</p>
        </div>
        <div className="button-row">
          <Link className="secondary-btn" to={`/roles/${role.role_id}/edit`}>角色定义工作台</Link>
          <Link className="secondary-btn" to={`/roles/${role.role_id}/briefing`}>使用前说明与调用预览</Link>
          <Link className="primary-btn" to={`/roles/${role.role_id}/governance`}>治理与发布</Link>
        </div>
      </div>

      <div className="role-page-grid">
        <RoleStageNav roleId={role.role_id} />

        <div className="role-page-main">
          <section className="metric-row">
            <div>
              <span>当前状态</span>
              <strong>{statusText[role.status]}</strong>
            </div>
            <div>
              <span>说明卡状态</span>
              <strong>{briefingStatusText[role.briefing.status]}</strong>
            </div>
            <div>
              <span>输出方式</span>
              <strong>{outputModeText[role.output_mode]}</strong>
            </div>
            <div>
              <span>最近验证</span>
              <strong>{role.latest_tested_at ? '已验证' : '暂无'}</strong>
            </div>
          </section>

          <section className="detail-section">
            <div className="section-title-row">
              <div>
                <h2>当前版本概览</h2>
                <p className="subtle">总览角色定义、说明卡、治理和外供当前状态。</p>
              </div>
              <Link className="text-link" to={`/roles/${role.role_id}/versions`}>
                <ExternalLink size={14} />
                查看版本记录
              </Link>
            </div>

            <div className="overview-grid">
              <div className="overview-card">
                <strong>L1 身份与判断</strong>
                <span>{role.main_duty_cluster || '待补齐核心职责'}</span>
                <small>{role.point_of_view || '分析视角待补齐'}</small>
              </div>
              <div className="overview-card">
                <strong>L2 知识依据</strong>
                <span>{role.briefing.knowledge_status.label}</span>
                <small>{role.knowledge_boundary || '当前未单独声明知识边界'}</small>
              </div>
              <div className="overview-card">
                <strong>L3 数据能力</strong>
                <span>{role.briefing.data_capability_status.label}</span>
                <small>{role.data_asset_bindings.length > 0 ? `${role.data_asset_bindings.length} 条资产已绑定` : '当前未授权结构化业务数据'}</small>
              </div>
              <div className="overview-card">
                <strong>L4 输出方式</strong>
                <span>{outputModeText[role.output_mode]}</span>
                <small>{role.output_type ? (outputTypeText[role.output_type] || role.output_type) : '自由输出'}</small>
              </div>
            </div>
          </section>

          <section className="detail-section">
            <h2>工作区进度</h2>
            <div className="check-grid">
              {role.definition_progress.map(item => (
                <article key={item.key} className={`check-card ${item.state}`}>
                  <strong>{item.label}</strong>
                  <span>{item.detail}</span>
                </article>
              ))}
            </div>
          </section>

          <RoleBriefingCard role={role} compact />

          <div className="two-col">
            <ReadinessPanelCard roleId={role.role_id} title="可供他人消费准备度" panel={role.share_readiness} />
            <ReadinessPanelCard roleId={role.role_id} title="正式发布准备度" panel={role.publish_readiness} />
          </div>

          <section className="two-col role-overview-panels">
            <article className="detail-section">
              <div className="section-title-row">
                <div>
                  <h2>治理与发布</h2>
                  <p className="subtle">治理主路径和门禁已独立收口，不再混在角色定义页。</p>
                </div>
                <Link className="text-link" to={`/roles/${role.role_id}/governance`}>
                  <ShieldCheck size={14} />
                  打开治理页
                </Link>
              </div>
              <div className="mini-check-list">
                <div className={`mini-check ${role.owner ? 'met' : 'missing'}`}>
                  <div>
                    <strong>Owner</strong>
                    <span>{role.owner || '待补齐'}</span>
                  </div>
                </div>
                <div className={`mini-check ${role.business_domain ? 'met' : 'missing'}`}>
                  <div>
                    <strong>业务域</strong>
                    <span>{role.business_domain || '待补齐'}</span>
                  </div>
                </div>
                <div className={`mini-check ${role.category ? 'met' : 'missing'}`}>
                  <div>
                    <strong>分类</strong>
                    <span>{role.category || '待补齐'}</span>
                  </div>
                </div>
              </div>
            </article>

            <article className="detail-section">
              <div className="section-title-row">
                <div>
                  <h2>外供与追溯</h2>
                  <p className="subtle">已发布版本才能生成 Tool / Skill 包，并复用同一张说明卡。</p>
                </div>
                <Link className="text-link" to={`/roles/${role.role_id}/exports`}>
                  <Package2 size={14} />
                  打开外供页
                </Link>
              </div>
              <div className="mini-check-list">
                <div className={`mini-check ${role.published_version_id ? 'met' : 'missing'}`}>
                  <div>
                    <strong>Published version</strong>
                    <span>{role.published_version_id || '当前尚无已发布版本'}</span>
                  </div>
                </div>
                <div className={`mini-check ${role.briefing.status === 'fresh' ? 'met' : 'missing'}`}>
                  <div>
                    <strong>说明卡状态</strong>
                    <span>{briefingStatusText[role.briefing.status]}</span>
                  </div>
                </div>
                <div className={`mini-check ${role.latest_tested_at ? 'met' : 'missing'}`}>
                  <div>
                    <strong>验证记录</strong>
                    <span>{role.latest_tested_at ? `${role.test_run_count} 次` : '当前还没有测试记录'}</span>
                  </div>
                </div>
              </div>
            </article>
          </section>

          <section className="detail-section">
            <div className="section-title-row">
              <div>
                <h2>试用与正式消费</h2>
                <p className="subtle">内部测试与正式消费分开承接，分别对应验证阶段和正式使用阶段。</p>
              </div>
              <div className="button-row">
                <Link className="secondary-btn" to={`/roles/${role.role_id}/test`}>
                  <TestTube2 size={14} />
                  去测试台
                </Link>
                {role.published_version_id && role.status !== 'archived' && (
                  <Link className="primary-btn" to={'/roles/' + role.role_id + '/exports'}>去外供与调用</Link>
                )}
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
