import { briefingStatusText, consumeStatusText, outputModeText, outputTypeText, type RoleDetail } from '../api';

interface RoleBriefingCardProps {
  role: RoleDetail;
  title?: string;
  compact?: boolean;
}

export function RoleBriefingCard({
  role,
  title = '使用前说明与调用预览',
  compact = false,
}: RoleBriefingCardProps) {
  const preview = role.briefing.output_preview;

  return (
    <section className={`briefing-card ${compact ? 'compact' : ''}`}>
      <div className="briefing-card-header">
        <div>
          <p className="eyebrow">Briefing Card</p>
          <h2>{title}</h2>
          <p className="subtle">{role.briefing.source_hint}</p>
        </div>
        <div className="briefing-chip-row">
          <span className={`tag-pill ${role.briefing.status === 'fresh' ? 'success' : 'warning'}`}>
            {briefingStatusText[role.briefing.status]}
          </span>
          <span className="tag-pill">{outputModeText[preview.output_mode]}</span>
          <span className="tag-pill">{preview.output_type ? (outputTypeText[preview.output_type] || preview.output_type) : '自由输出'}</span>
        </div>
      </div>

      <div className="briefing-summary-row">
        <div>
          <span>角色</span>
          <strong>{role.name}</strong>
        </div>
        <div>
          <span>当前版本</span>
          <strong>{role.role_version_id || '未生成'}</strong>
        </div>
        <div>
          <span>知识状态</span>
          <strong>{role.briefing.knowledge_status.label}</strong>
        </div>
        <div>
          <span>数据能力</span>
          <strong>{role.briefing.data_capability_status.label}</strong>
        </div>
      </div>

      <div className="briefing-grid">
        <article className="briefing-module">
          <h3>这个角色适合干什么</h3>
          <div className="briefing-readonly">
            <strong>一句话摘要</strong>
            <p>{role.bio}</p>
          </div>
          <div className="briefing-readonly">
            <strong>核心职责</strong>
            <p>{role.main_duty_cluster || '当前尚未补齐核心职责。'}</p>
          </div>
          <div className="briefing-readonly">
            <strong>适用场景</strong>
            {role.briefing.applicable_scenarios.length > 0 ? (
              <ul className="briefing-list">
                {role.briefing.applicable_scenarios.map(item => <li key={item}>{item}</li>)}
              </ul>
            ) : (
              <p>当前尚未保存适用场景。</p>
            )}
          </div>
        </article>

        <article className="briefing-module">
          <h3>怎么正确使用</h3>
          <p>{role.briefing.usage_notes || '当前尚未保存使用说明。'}</p>
        </article>

        <article className="briefing-module">
          <h3>你将得到什么</h3>
          <p>{preview.summary}</p>
          {preview.schema_preview && (
            <pre className="json-preview">{JSON.stringify(preview.schema_preview, null, 2)}</pre>
          )}
        </article>

        <article className="briefing-module">
          <h3>为什么可信 / 当前限制</h3>
          <p>{role.briefing.support_basis_summary || '当前尚未保存可信依据摘要。'}</p>
          <div className="briefing-evidence-list">
            <div>
              <strong>{role.briefing.knowledge_status.label}</strong>
              <span>{role.briefing.knowledge_status.detail}</span>
            </div>
            <div>
              <strong>{role.briefing.data_capability_status.label}</strong>
              <span>{role.briefing.data_capability_status.detail}</span>
            </div>
            <div>
              <strong>最近验证</strong>
              <span>
                {role.briefing.validation_summary.has_record
                  ? `累计 ${role.briefing.validation_summary.total_count} 次，最近状态 ${consumeStatusText[role.briefing.validation_summary.latest_status || ''] || '已记录'}`
                  : '当前暂无验证记录'}
              </span>
            </div>
          </div>
        </article>
      </div>
    </section>
  );
}
