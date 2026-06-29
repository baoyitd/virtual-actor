import { ArrowLeft, ChevronDown, RefreshCcw, Save } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, briefingStatusText, type RoleDetail } from '../api';
import { RoleBriefingCard } from '../components/RoleBriefingCard';
import { RoleStageNav } from '../components/RoleStageNav';

export function RoleBriefingPage() {
  const { id = '' } = useParams();
  const [role, setRole] = useState<RoleDetail | null>(null);
  const [scenarioText, setScenarioText] = useState('');
  const [usageNotes, setUsageNotes] = useState('');
  const [supportSummary, setSupportSummary] = useState('');
  const [showEditor, setShowEditor] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const detail = await api.getRole(id);
      setRole(detail);
      setScenarioText(detail.briefing.applicable_scenarios.join('\n'));
      setUsageNotes(detail.briefing.usage_notes);
      setSupportSummary(detail.briefing.support_basis_summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载使用前说明失败');
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const save = async (confirmCurrent = false) => {
    if (!role) return;
    setSaving(true);
    setError('');
    try {
      const detail = await api.saveBriefing(role.role_id, {
        applicable_scenarios: scenarioText.split('\n').map(item => item.trim()).filter(Boolean),
        usage_notes: usageNotes,
        support_basis_summary: supportSummary,
        confirm_current: confirmCurrent,
      });
      setRole(detail);
      setScenarioText(detail.briefing.applicable_scenarios.join('\n'));
      setUsageNotes(detail.briefing.usage_notes);
      setSupportSummary(detail.briefing.support_basis_summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存说明卡失败');
    } finally {
      setSaving(false);
    }
  };

  const regenerate = async () => {
    if (!role) return;
    setSaving(true);
    setError('');
    try {
      const detail = await api.regenerateBriefing(role.role_id);
      setRole(detail);
      setScenarioText(detail.briefing.applicable_scenarios.join('\n'));
      setUsageNotes(detail.briefing.usage_notes);
      setSupportSummary(detail.briefing.support_basis_summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : '重新生成说明卡失败');
    } finally {
      setSaving(false);
    }
  };

  if (!role) return <div className="page-loading">正在加载使用前说明与调用预览...</div>;

  const saveLabel =
    role.status === 'draft' || role.status === 'archived'
      ? '保存当前说明并进入测试'
      : '保存当前说明';

  return (
    <div className="page">
      <Link className="back-link" to={`/roles/${role.role_id}`}><ArrowLeft size={16} />返回角色概览</Link>

      <div className="page-head">
        <div>
          <p className="eyebrow">Briefing Workflow</p>
          <h1>使用前说明与调用预览</h1>
          <p className="subtle">系统先生成当前保存版说明卡，角色 owner 再做轻量修订；首次保存当前说明后，这个可编辑版本进入测试态。</p>
        </div>
        <div className="button-row">
          <button className="primary-btn" onClick={() => save(false)} disabled={saving}>
            <Save size={16} />
            {saving ? '保存中...' : saveLabel}
          </button>
        </div>
      </div>

      {error && <div className="alert error">{error}</div>}
      {role.briefing.status === 'stale' && (
        <>
          <div className="alert warning">
            当前来源已变化，说明卡处于“{briefingStatusText[role.briefing.status]}”状态。未确认更新前，不能发布或生成外供。
          </div>
          <section className="detail-section">
            <div className="section-title-row">
              <div>
                <h2>待确认更新</h2>
                <p className="subtle">这里承接 stale 状态下的专属动作。你可以按最新角色信息重生成说明卡，也可以沿用当前文字并重新确认。</p>
              </div>
              <div className="button-row">
                <button className="secondary-btn" onClick={regenerate} disabled={saving}>
                  <RefreshCcw size={16} />
                  根据最新角色信息重生成说明卡
                </button>
                <button className="secondary-btn" onClick={() => save(true)} disabled={saving}>
                  沿用当前文字并确认
                </button>
              </div>
            </div>
          </section>
        </>
      )}

      <div className="role-page-grid">
        <RoleStageNav roleId={role.role_id} />

        <div className="role-page-main">
          <RoleBriefingCard role={role} />

          <section className="detail-section">
            <div className="section-title-row">
              <div>
                <h2>轻量修订</h2>
                <p className="subtle">默认先看系统生成的说明卡；只有需要人工微调时，再展开这组编辑项。</p>
              </div>
              <button className="secondary-btn small-btn" onClick={() => setShowEditor(prev => !prev)}>
                <ChevronDown size={14} />
                {showEditor ? '收起修订区' : '展开修订区'}
              </button>
            </div>

            {showEditor ? (
              <div className="briefing-editor-grid">
                <label className="field-block">
                  <span className="field-label">适用场景（每行一条）</span>
                  <textarea rows={7} value={scenarioText} onChange={e => setScenarioText(e.target.value)} />
                </label>
                <label className="field-block">
                  <span className="field-label">使用说明</span>
                  <textarea rows={9} value={usageNotes} onChange={e => setUsageNotes(e.target.value)} />
                </label>
                <label className="field-block span-2">
                  <span className="field-label">可信依据摘要</span>
                  <textarea rows={8} value={supportSummary} onChange={e => setSupportSummary(e.target.value)} />
                </label>
              </div>
            ) : (
              <div className="collapsed-note">
                说明卡已经在上方首屏展示；若要修改 `applicable_scenarios / usage_notes / support_basis_summary`，再展开修订区处理。
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
