import { ArrowLeft, PlayCircle, ShieldAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  api,
  briefingStatusText,
  consumeStatusText,
  outputModeText,
  outputTypeText,
  statusText,
  type RoleDetail,
  type TestValidationRecord,
} from '../api';
import { ConsumeResultPanel } from '../components/ConsumeResultPanel';
import { RoleStageNav } from '../components/RoleStageNav';

function shortId(value: string | null | undefined) {
  if (!value) return '未生成';
  return `${value.slice(0, 8)}...`;
}

export function RoleTest() {
  const { id = '' } = useParams<{ id: string }>();
  const [role, setRole] = useState<RoleDetail | null>(null);
  const [results, setResults] = useState<TestValidationRecord[]>([]);
  const [query, setQuery] = useState('请基于当前角色给出一份判断。');
  const [context, setContext] = useState('');
  const [working, setWorking] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      setError('');
      const detail = await api.getRole(id);
      setRole(detail);
      const history = await api.getTestValidationRecords(detail.role_id, {
        versionId: detail.role_version_id || undefined,
        limit: 20,
      });
      setResults(history);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载试用与测试失败');
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const run = async () => {
    if (!role || !query.trim() || role.status !== 'test') return;
    const submittedQuery = query.trim();
    const submittedContext = context.trim() || null;
    setWorking(true);
    setError('');
    try {
      const result = await api.testConsumeRole(role.role_id, {
        query: submittedQuery,
        context: submittedContext,
        role_version_id: role.role_version_id,
      });
      const latestRecord: TestValidationRecord = {
        ...result,
        query: submittedQuery,
        context: submittedContext,
      };
      setResults(prev => [latestRecord, ...prev.filter(item => item.validation_record_id !== latestRecord.validation_record_id)]);
      const refreshedRole = await api.getRole(role.role_id);
      setRole(refreshedRole);
      const refreshedHistory = await api.getTestValidationRecords(role.role_id, {
        versionId: refreshedRole.role_version_id || undefined,
        limit: 20,
      });
      setResults(refreshedHistory);
    } catch (err) {
      setError(err instanceof Error ? err.message : '执行测试失败');
    } finally {
      setWorking(false);
    }
  };

  if (!role) return <div className="page-loading">正在加载试用与测试...</div>;

  const latestResult = results[0] || null;
  const historyResults = results.slice(1);

  return (
    <div className="page">
      <div className="test-back-bar">
        <Link className="back-link" to={'/roles/' + role.role_id}><ArrowLeft size={16} />返回角色概览</Link>
        <Link className="back-link subtle" to={'/roles/' + role.role_id + '/briefing'}>使用前说明</Link>
      </div>

      <div className="page-head">
        <div>
          <p className="eyebrow">Validation Desk</p>
          <h1>试用与测试</h1>
          <p className="subtle">这里的唯一目标，是快速判断这个角色在当前版本下是否按预期工作。</p>
        </div>
      </div>

      {error && <div className="alert error"><ShieldAlert size={16} />{error}</div>}
      {role.status === 'draft' && (
        <div className="alert warning">
          当前角色仍是草稿。请先回 02 保存当前说明卡，进入测试态后再来这里开始测试。
        </div>
      )}
      {role.status !== 'draft' && role.status !== 'test' && (
        <div className="alert warning">
          当前角色状态为 {statusText[role.status] || role.status}。这里仅面向测试态角色；若要正式使用已发布版本，请改走正式消费。
        </div>
      )}

      <div className="role-page-grid">
        <RoleStageNav roleId={role.role_id} />

        <div className="role-page-main">
          <div className="test-role-bar">
            <div className="test-role-info">
              <strong>{role.name}</strong>
              <span className="sep">·</span>
              <span>版本 {shortId(role.role_version_id)}</span>
              <span className="sep">·</span>
              <span>{outputModeText[role.output_mode]}</span>
              {role.output_type && (
                <>
                  <span className="sep">·</span>
                  <span>{outputTypeText[role.output_type] || role.output_type}</span>
                </>
              )}
              <span className="sep">·</span>
              <span>{briefingStatusText[role.briefing.status]}</span>
              <span className="sep">·</span>
              <span>{role.briefing.knowledge_status.label} / {role.briefing.data_capability_status.label}</span>
            </div>
          </div>

          <section className="consume-input-section">
            <div className="section-title-row">
              <div>
                <h2>测试查询</h2>
                <p className="subtle">用能暴露角色能力的问题来测，重点看它是否真的用了你绑定的知识、数据和输出契约。</p>
              </div>
            </div>
            <label className="field-block">
              <span className="field-label">问题</span>
              <textarea rows={3} value={query} onChange={e => setQuery(e.target.value)} placeholder="输入业务问题，验证该角色在当前知识 / 数据 / 输出配置下的表现。" />
            </label>
            <label className="field-block">
              <span className="field-label">业务上下文（可选）</span>
              <textarea rows={3} value={context} onChange={e => setContext(e.target.value)} placeholder="补充业务背景、目标对象或关键约束。" />
            </label>
            {role.status === 'draft' && (
              <div className="collapsed-note">
                当前页不再负责切状态。先回 02 保存当前说明卡，当前版本进入测试态后再回来开始测试。
              </div>
            )}
            <div className="button-row">
              <button className="primary-btn" onClick={run} disabled={working || !query.trim() || role.status !== 'test'}>
                <PlayCircle size={16} />
                {working ? '测试中...' : latestResult ? '再次测试' : '开始测试'}
              </button>
            </div>
          </section>

          <section className="detail-section">
            <div className="section-title-row">
              <div>
                <h2>测试结果</h2>
                <p className="subtle">先看这次是否命中，再决定是回去补角色定义，还是继续进入治理与发布。</p>
              </div>
            </div>
            {latestResult ? (
              <ConsumeResultPanel title="本次测试问题" result={latestResult} />
            ) : (
              <div className="empty-state">当前还没有测试结果，输入问题后开始测试。</div>
            )}
          </section>

          {historyResults.length > 0 && (
            <section className="detail-section">
              <div className="section-title-row">
                <div>
                  <h2>历史测试记录</h2>
                  <p className="subtle">历史记录默认收起，避免抢占主屏；只有需要回看时再展开具体细节。</p>
                </div>
              </div>
              <div className="result-history-list">
                {historyResults.map(item => {
                  const statusClass = item.status === 'success' ? 'success' : item.status === 'undefined' ? 'muted' : 'warning';
                  return (
                  <details key={item.validation_record_id} className="result-history-item">
                    <summary className="result-history-summary">
                      <div>
                        <strong>{item.query}</strong>
                        <small>{item.created_at ? new Date(item.created_at).toLocaleString('zh-CN', { hour12: false }) : '未记录时间'}</small>
                      </div>
                      <div className="result-history-meta">
                        <span className={'tag-pill ' + statusClass}>{consumeStatusText[item.status] || item.status}</span>
                        <span className="tag-pill muted">{item.output_type ? (outputTypeText[item.output_type] || item.output_type) : '自由输出'}</span>
                      </div>
                    </summary>
                    <div className="result-history-body">
                      <ConsumeResultPanel title="当时测试问题" result={item} />
                    </div>
                  </details>
                  );
                })}
              </div>
            </section>
          )}

          <div className="test-next-row">
            {latestResult?.status === 'success' ? (
              <Link className="primary-btn" to={'/roles/' + role.role_id + '/governance'}>下一步：去治理与发布</Link>
            ) : (
              <>
                <Link className="back-link" to={'/roles/' + role.role_id + '/edit'}>回 01 补角色定义</Link>
                <Link className="back-link" to={'/roles/' + role.role_id + '/briefing'}>回 02 确认说明卡</Link>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
