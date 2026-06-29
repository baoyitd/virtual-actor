import { ArrowLeft, Bot, CheckCircle2, Code2, Download, PlayCircle, RefreshCcw, ShieldAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  api,
  briefingStatusText,
  consumeStatusText,
  getToken,
  outputModeText,
  outputTypeText,
  type ConsumeRecord,
  type ConsumeResponse,
  type RoleDetail,
  type RoleVersionPublicResponse,
} from '../api';
import { ConsumeResultPanel } from '../components/ConsumeResultPanel';
import { RoleStageNav } from '../components/RoleStageNav';

const CALLER_OPTIONS = [
  { value: 'human', label: '平台内调用（human）' },
  { value: 'external_tool', label: 'Dify Tool（external_tool）' },
  { value: 'external_skill', label: 'Codex Skill（external_skill）' },
] as const;

export function RoleExportsPage() {
  const { id = '' } = useParams();
  const [role, setRole] = useState<RoleDetail | null>(null);
  const [publishedView, setPublishedView] = useState<RoleVersionPublicResponse | null>(null);
  const [lastGenerated, setLastGenerated] = useState<{ type: 'tool' | 'skill'; packageId: string; fileCount: number } | null>(null);
  const [records, setRecords] = useState<ConsumeRecord[]>([]);
  const [simulateQuery, setSimulateQuery] = useState('请基于当前角色给出一份结构化业务判断。');
  const [simulateContext, setSimulateContext] = useState('');
  const [simulateCaller, setSimulateCaller] = useState<'human' | 'external_tool' | 'external_skill'>('external_tool');
  const [simulateResult, setSimulateResult] = useState<ConsumeResponse | null>(null);
  const [lastRequest, setLastRequest] = useState<{ query: string; context: string | null } | null>(null);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const [detail, usageRecords] = await Promise.all([
        api.getRole(id),
        api.getConsumeRecords(id).catch(() => []),
      ]);
      const published = detail.published_version_id
        ? await api.getVersionDetail(detail.published_version_id).catch(() => null)
        : null;
      setRole(detail);
      setPublishedView(published);
      setRecords(usageRecords);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载外供与调用页失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const canExport = Boolean(role?.published_version_id) && role?.status !== 'archived';

  const generatePackage = async (packageType: 'tool' | 'skill') => {
    if (!canExport) return;
    setWorking(true);
    setError('');
    try {
      const created = await api.generateExportPackage(id, packageType);
      setLastGenerated({ type: packageType, packageId: created.package_id, fileCount: created.files.length });
      if (!role) return;
      setRole(await api.getRole(role.role_id));
    } catch (err) {
      setError(err instanceof Error ? err.message : '生成外供包失败');
    } finally {
      setWorking(false);
    }
  };

  const downloadPackage = async () => {
    if (!lastGenerated) return;
    const token = getToken();
    const resp = await fetch(api.exportPackageDownloadUrl(id, lastGenerated.packageId), {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!resp.ok) throw new Error('下载失败');
    const blob = await resp.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    const label = lastGenerated.type === 'tool' ? 'tool' : 'skill';
    a.download = `${role?.name || 'role'}-${label}-package.zip`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const runCall = async () => {
    if (!role || !canExport) return;
    const submittedQuery = simulateQuery.trim();
    const submittedContext = simulateContext.trim() || null;
    setWorking(true);
    setError('');
    try {
      const callerIdMap = {
        human: 'usage-desk',
        external_tool: 'simulated-dify-tool',
        external_skill: 'simulated-codex-skill',
      };
      const result = await api.consumeRole(role.role_id, {
        query: submittedQuery,
        context: submittedContext,
        caller_type: simulateCaller,
        caller_id: callerIdMap[simulateCaller],
        role_version_id: role.published_version_id,
      });
      setSimulateResult(result);
      setLastRequest({ query: submittedQuery, context: submittedContext });
      setRecords(await api.getConsumeRecords(role.role_id));
    } catch (err) {
      setError(err instanceof Error ? err.message : '调用失败');
    } finally {
      setWorking(false);
    }
  };

  if (loading || !role) return <div className="page-loading">正在加载外供与调用...</div>;

  const isUsingPublishedSnapshot = Boolean(
    role.published_version_id && role.role_version_id && role.role_version_id !== role.published_version_id,
  );
  const latestResultView = simulateResult
    ? { ...simulateResult, query: lastRequest?.query || '', context: lastRequest?.context || null }
    : null;

  return (
    <div className="page">
      <div className="test-back-bar">
        <Link className="back-link" to={'/roles/' + role.role_id}><ArrowLeft size={16} />返回角色概览</Link>
        <Link className="back-link subtle" to={'/roles/' + role.role_id + '/briefing'}>使用前说明</Link>
        <button className="back-link subtle" onClick={load}>
          <RefreshCcw size={14} />刷新
        </button>
      </div>

      <div className="page-head">
        <div>
          <p className="eyebrow">Export & Call</p>
          <h1>外供与调用</h1>
          <p className="subtle">角色已发布后，这里负责生成外供包供外部系统使用，并验证调用是否正常。</p>
        </div>
      </div>

      {error && <div className="alert error"><ShieldAlert size={16} />{error}</div>}
      {!role.published_version_id && (
        <div className="alert warning">当前还没有可用的已发布版本，外供和调用暂不可用。请先在 04 治理与发布中发布当前版本。</div>
      )}
      {role.status === 'archived' && (
        <div className="alert warning">当前角色已归档，不再允许生成新外供或执行调用；历史包和调用记录仍可查看。</div>
      )}
      {isUsingPublishedSnapshot && (
        <div className="collapsed-note">
          当前你正在编辑一个未发布的新草稿；本页仍绑定最近已发布版本 {role.published_version_id}。
        </div>
      )}

      <div className="role-page-grid">
        <RoleStageNav roleId={role.role_id} />

        <div className="role-page-main">
          <div className="gov-status-bar">
            <strong>{role.name}</strong>
            <span className="sep">·</span>
            <span>状态 {role.status === 'published' ? '已发布' : role.status === 'archived' ? '已归档' : '未发布'}</span>
            {role.published_version_id && (
              <>
                <span className="sep">·</span>
                <span>版本 {role.published_version_id.slice(0, 8) + '...'}</span>
              </>
            )}
            {publishedView && (
              <>
                <span className="sep">·</span>
                <span>说明卡 {briefingStatusText[publishedView.briefing.status]}</span>
                <span className="sep">·</span>
                <span>{publishedView.output_type ? (outputTypeText[publishedView.output_type] || publishedView.output_type) : '自由输出'}（{outputModeText[publishedView.output_mode]}）</span>
              </>
            )}
          </div>

          <section className="detail-section">
            <div className="section-title-row">
              <div>
                <h2>生成外供包</h2>
                <p className="subtle">生成后自动下载 zip 文件，导入外部系统使用。同类型包只保留最新一个。</p>
              </div>
            </div>
            <div className="button-row">
              <button className="secondary-btn" onClick={() => generatePackage('tool')} disabled={working || !canExport}>
                <Bot size={16} />
                {working ? '生成中...' : '生成 Tool 包（Dify）'}
              </button>
              <button className="primary-btn" onClick={() => generatePackage('skill')} disabled={working || !canExport}>
                <Code2 size={16} />
                {working ? '生成中...' : '生成 Skill 包（Codex）'}
              </button>
            </div>

            {lastGenerated && (
              <div className="alert success" style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                <CheckCircle2 size={18} />
                <span>{lastGenerated.type === 'tool' ? 'Tool 包' : 'Skill 包'}已生成，包含 {lastGenerated.fileCount} 个文件。</span>
                <button className="primary-btn small-btn" onClick={downloadPackage}>
                  <Download size={14} />
                  下载
                </button>
              </div>
            )}
          </section>

          <section className="detail-section">
            <div className="section-title-row">
              <div>
                <h2>调用方式说明</h2>
                <p className="subtle">外部系统通过以下方式调用该角色。</p>
              </div>
            </div>
            <div className="call-guide">
              <div className="call-guide-item">
                <strong>API 地址</strong>
                <code>{'POST {VIRTUAL_ACTOR_BASE_URL}/role-assets/{role_id}/consume'}</code>
              </div>
              <div className="call-guide-item">
                <strong>认证</strong>
                <code>{'Authorization: Bearer {VIRTUAL_ACTOR_TOKEN}'}</code>
              </div>
              <div className="call-guide-item">
                <strong>请求参数</strong>
                <pre className="code-preview">{`{
  "query": "业务问题",
  "context": "可选业务上下文",
  "caller_type": "external_tool 或 external_skill",
  "caller_id": "你的调用方标识",
  "role_version_id": "${role.published_version_id || '已发布版本ID'}"
}`}</pre>
              </div>
              <div className="call-guide-item">
                <strong>使用引导</strong>
                <ul>
                  <li><strong>Dify</strong>：生成 Tool 包后，将包内 <code>dify-openapi.json</code> 和 <code>dify-provider-template.json</code> 导入 Dify，配置 <code>VIRTUAL_ACTOR_BASE_URL</code> 和 <code>VIRTUAL_ACTOR_TOKEN</code> 即可调用。</li>
                  <li><strong>Codex</strong>：生成 Skill 包后，将 <code>SKILL.md</code> 和包内文件复制到 Codex 项目，配置环境变量即可调用。</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="detail-section">
            <div className="section-title-row">
              <div>
                <h2>验证调用</h2>
                <p className="subtle">选择调用方式，输入问题，验证已发布版本能正常响应。</p>
              </div>
            </div>
            <div className="two-col">
              <label className="field-block">
                <span className="field-label">调用方式</span>
                <select value={simulateCaller} onChange={e => setSimulateCaller(e.target.value as 'human' | 'external_tool' | 'external_skill')}>
                  {CALLER_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </label>
              <label className="field-block">
                <span className="field-label">查询问题</span>
                <input value={simulateQuery} onChange={e => setSimulateQuery(e.target.value)} />
              </label>
            </div>
            <label className="field-block">
              <span className="field-label">业务上下文（可选）</span>
              <textarea rows={3} value={simulateContext} onChange={e => setSimulateContext(e.target.value)} />
            </label>
            <div className="button-row">
              <button className="primary-btn" onClick={runCall} disabled={working || !canExport || !simulateQuery.trim()}>
                <PlayCircle size={16} />
                {working ? '调用中...' : '执行调用'}
              </button>
            </div>

            {latestResultView && (
              <div style={{ marginTop: '16px' }}>
                <ConsumeResultPanel title="本次调用问题" result={latestResultView} />
              </div>
            )}
          </section>

          <section className="detail-section">
            <div className="section-title-row">
              <div>
                <h2>调用记录</h2>
                <p className="subtle">全部调用记录，按调用方式区分。</p>
              </div>
            </div>
            <div className="record-list">
              {records.map(record => (
                <div key={record.id} className="record-item">
                  <div className="record-item-header">
                    <span className={'caller-badge caller-' + record.caller_type}>{record.caller_type}</span>
                    <strong>{consumeStatusText[record.status] || record.status}</strong>
                  </div>
                  <span>{record.query}</span>
                  <small>{record.role_version_id ? record.role_version_id.slice(0, 8) + '...' : ''} · {record.output_type ? (outputTypeText[record.output_type] || record.output_type) : '自由输出'}</small>
                </div>
              ))}
              {records.length === 0 && <div className="empty-state">当前还没有调用记录。</div>}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
