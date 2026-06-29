import { AlertTriangle, BarChart3, Layers, SendHorizonal, Sparkles, Users } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, briefingStatusText, categoryText, consumeStatusText, statusText, type DashboardStats, type RoleListItem } from '../api';

type QueueCard = {
  key: string;
  title: string;
  description: string;
  emptyText: string;
  roles: RoleListItem[];
  route: (roleId: string) => string;
  reason: (role: RoleListItem) => string;
};

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [roles, setRoles] = useState<RoleListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');
    Promise.all([api.dashboardStats(), api.listRoles()])
      .then(([dashboardStats, roleItems]) => {
        setStats(dashboardStats);
        setRoles(roleItems);
      })
      .catch(err => setError(err instanceof Error ? err.message : '当前无法加载运营统计。'))
      .finally(() => setLoading(false));
  }, []);

  const governanceGaps = roles.filter(role =>
    role.status !== 'draft' && (
      !role.owner?.trim() ||
      !role.business_domain?.trim() ||
      !role.category?.trim()
    ),
  );

  const briefingGaps = roles.filter(role => role.briefing_status !== 'fresh');

  const testingGaps = roles.filter(role => (role.status === 'test' || role.status === 'published') && !role.has_test_record);

  const recommendationGaps = roles.filter(role => role.status === 'published' && !role.recommend_pool_eligible);

  const legacyGaps = roles.filter(role => role.legacy_incomplete);

  const queues: QueueCard[] = [
    {
      key: 'governance',
      title: '治理主路径待补齐',
      description: '进入共享、发布和外供前，应先闭合 Owner、业务域和分类。',
      emptyText: '当前没有治理主路径缺口。',
      roles: governanceGaps,
      route: roleId => `/roles/${roleId}/governance`,
      reason: role => {
        const missing = [];
        if (!role.owner?.trim()) missing.push('Owner');
        if (!role.business_domain?.trim()) missing.push('业务域');
        if (!role.category?.trim()) missing.push('分类');
        return `待补齐：${missing.join(' / ')}`;
      },
    },
    {
      key: 'briefing',
      title: '说明卡待处理',
      description: '说明卡不新鲜时，会直接影响使用前判断、发布与外供复用。',
      emptyText: '当前说明卡都已保存且无需确认更新。',
      roles: briefingGaps,
      route: roleId => `/roles/${roleId}/briefing`,
      reason: role => role.briefing_status === 'stale'
        ? '来源已变化，待确认更新'
        : `说明卡状态：${briefingStatusText[role.briefing_status]}`,
    },
    {
      key: 'testing',
      title: '测试证据待补齐',
      description: '内部试用和已发布角色都应有可追溯的测试记录，不应靠猜测上线。',
      emptyText: '当前试用和已发布角色均已有测试记录。',
      roles: testingGaps,
      route: roleId => `/roles/${roleId}/test`,
      reason: role => role.status === 'published'
        ? '已发布但暂无测试记录'
        : '内部试用前建议先完成测试',
    },
    {
      key: 'recommendation',
      title: 'AI 推荐池待补齐',
      description: '已发布但未进入 AI 推荐池的角色，会削弱市场侧的发现效率。',
      emptyText: '当前已发布角色都可进入 AI 推荐池。',
      roles: recommendationGaps,
      route: roleId => `/roles/${roleId}`,
      reason: () => '说明卡或业务画像待补齐，暂不进入 AI 推荐池',
    },
  ];

  if (loading) return <div className="page-loading">正在加载运营看板...</div>;
  if (!stats) return <div className="empty-state">{error || '当前无法加载运营统计。'}</div>;

  return (
    <section className="page">
      <div className="page-head compact">
        <div>
          <p className="eyebrow">Operations</p>
          <h1>运营看板</h1>
          <p className="subtle">面向管理员与资产运营方，先看待处理缺口，再看资产、创建、消费、分类和风险统计。</p>
        </div>
      </div>

      <div className="dashboard-priority-grid">
        {queues.map(queue => (
          <article key={queue.key} className="dashboard-priority-card">
            <div className="dashboard-priority-head">
              <div>
                <h2>{queue.title}</h2>
                <p>{queue.description}</p>
              </div>
              <strong>{queue.roles.length}</strong>
            </div>

            {queue.roles.length > 0 ? (
              <div className="dashboard-queue">
                {queue.roles.slice(0, 3).map(role => (
                  <Link key={role.role_id} className="dashboard-queue-item" to={queue.route(role.role_id)}>
                    <div>
                      <strong>{role.role_name}</strong>
                      <span>{statusText[role.status]}</span>
                    </div>
                    <p>{queue.reason(role)}</p>
                  </Link>
                ))}
                {queue.roles.length > 3 && (
                  <div className="dashboard-overflow-note">还有 {queue.roles.length - 3} 个角色待处理，可从角色资产继续筛选。</div>
                )}
              </div>
            ) : (
              <div className="dashboard-empty-note">{queue.emptyText}</div>
            )}
          </article>
        ))}
      </div>

      {legacyGaps.length > 0 && (
        <div className="alert warning">
          <AlertTriangle size={16} />
          当前还有 {legacyGaps.length} 个 legacy 角色待补齐新 requirement，建议在角色资产中优先处理后再继续发布或外供。
        </div>
      )}

      <div className="dashboard-grid">
        <article className="dashboard-card">
          <Layers size={22} />
          <h2>资产概览</h2>
          <div className="dashboard-numbers">
            <div>
              <strong>{stats.total_roles}</strong>
              <span>角色总数</span>
            </div>
            {Object.entries(stats.by_status).map(([key, value]) => (
              <div key={key}>
                <strong>{value}</strong>
                <span>{statusText[key] || key}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="dashboard-card">
          <Sparkles size={22} />
          <h2>创建运营</h2>
          <div className="dashboard-numbers">
            {Object.entries(stats.creation_by_source).map(([key, value]) => (
              <div key={key}>
                <strong>{value}</strong>
                <span>{key === 'ai_assisted' ? 'AI 协作创建' : '手工创建'}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="dashboard-card">
          <SendHorizonal size={22} />
          <h2>消费运营</h2>
          <div className="dashboard-numbers">
            <div>
              <strong>{stats.total_consume_calls}</strong>
              <span>总消费次数</span>
            </div>
            {Object.entries(stats.consume_by_status).map(([key, value]) => (
              <div key={key}>
                <strong>{value}</strong>
                <span>{consumeStatusText[key] || key}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="dashboard-card">
          <Users size={22} />
          <h2>资产分类</h2>
          <div className="dashboard-numbers">
            {Object.entries(stats.by_category).map(([key, value]) => (
              <div key={key}>
                <strong>{value}</strong>
                <span>{categoryText[key] || key}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="dashboard-card">
          <AlertTriangle size={22} />
          <h2>风险运营</h2>
          <div className="dashboard-numbers">
            <div>
              <strong>{(stats.boundary_blocked_ratio * 100).toFixed(1)}%</strong>
              <span>边界阻断占比</span>
            </div>
            <div>
              <strong>{(stats.undefined_ratio * 100).toFixed(1)}%</strong>
              <span>未定义占比</span>
            </div>
          </div>
        </article>

        <article className="dashboard-card">
          <BarChart3 size={22} />
          <h2>当前判断</h2>
          <p className="subtle">
            如果边界阻断和未定义比例持续抬升，应回到角色定义、说明卡和治理链路复盘是否存在职责、知识或输入前提不清的问题。
          </p>
        </article>
      </div>
    </section>
  );
}
