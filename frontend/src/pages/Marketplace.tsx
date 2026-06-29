import { BookOpen, ClipboardCheck, Scale, ShieldAlert, ShoppingBag } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, categoryText, outputModeText, outputTypeText, type RecommendResponse, type RoleListItem } from '../api';

const SCENARIO_CARDS = [
  { label: '决策支持', icon: Scale, outputType: 'decision_advice', description: '重大事项决策前的立场、理由和风险判断' },
  { label: '风险分析', icon: ShieldAlert, outputType: 'risk_analysis', description: '风险识别、评估和缓解建议' },
  { label: '制度合规', icon: BookOpen, outputType: 'policy_explanation', description: '制度条款解释与行为边界说明' },
  { label: '审查评审', icon: ClipboardCheck, outputType: 'review_findings', description: '审查意见、问题发现和修改建议' },
];

export function Marketplace() {
  const [roles, setRoles] = useState<RoleListItem[]>([]);
  const [category, setCategory] = useState('');
  const [outputTypeFilter, setOutputTypeFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [recommendIntent, setRecommendIntent] = useState('');
  const [recommendLoading, setRecommendLoading] = useState(false);
  const [recommendResult, setRecommendResult] = useState<RecommendResponse | null>(null);

  const load = async (nextCategory = category, nextOutputType = outputTypeFilter) => {
    setLoading(true);
    try {
      const result = await api.marketplaceList({
        category: nextCategory || undefined,
        output_type: nextOutputType || undefined,
      });
      setRoles(result);
    } catch {
      setRoles([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [category, outputTypeFilter]);

  const handleRecommend = async () => {
    if (!recommendIntent.trim()) return;
    setRecommendLoading(true);
    setRecommendResult(null);
    try {
      const result = await api.marketplaceRecommend(recommendIntent.trim(), category || undefined);
      setRecommendResult(result);
    } catch {
      setRecommendResult({
        matched: false,
        result_type: 'service_error',
        recommendations: [],
        unmatched_intent_summary: null,
        service_error_message: '推荐服务暂时不可用，请稍后重试。',
      });
    } finally {
      setRecommendLoading(false);
    }
  };

  const clearRecommend = () => {
    setRecommendIntent('');
    setRecommendResult(null);
    setOutputTypeFilter('');
  };

  return (
    <section className="page">
      <div className="page-head compact">
        <div>
          <p className="eyebrow">Marketplace</p>
          <h1><ShoppingBag size={20} />资产市场</h1>
          <p className="subtle">从已发布角色中按业务场景发现、试用和接入角色资产。</p>
        </div>
      </div>

      <div className="scenario-cards">
        <h3 className="section-title">按业务场景快速查找</h3>
        <div className="scenario-grid">
          {SCENARIO_CARDS.map(item => (
            <button key={item.outputType} className="scenario-card" onClick={() => { setOutputTypeFilter(item.outputType); setRecommendResult(null); }}>
              <item.icon size={24} />
              <strong>{item.label}</strong>
              <span className="subtle">{item.description}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="recommend-section">
        <h3 className="section-title">描述业务任务，让 AI 推荐合适角色</h3>
        <div className="recommend-input-row">
          <input
            type="text"
            className="recommend-input"
            value={recommendIntent}
            onChange={e => setRecommendIntent(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleRecommend()}
            placeholder="例如：我需要一个帮经营管理层做预算偏差复盘的角色"
          />
          <button className="primary-btn" onClick={handleRecommend} disabled={recommendLoading || !recommendIntent.trim()}>
            {recommendLoading ? 'AI 正在匹配...' : 'AI 推荐角色'}
          </button>
        </div>
      </div>

      {recommendResult ? (
        <div className="recommend-results">
          <div className="section-title-row">
            <div>
              <h2>AI 推荐结果</h2>
              <p className="subtle">输入意图：{recommendIntent}</p>
            </div>
            <button className="secondary-btn small-btn" onClick={clearRecommend}>返回列表</button>
          </div>

          {recommendResult.matched && recommendResult.recommendations.length > 0 ? (
            <div className="recommend-grid">
              {recommendResult.recommendations.map(item => (
                <article key={item.role_id} className="recommend-card">
                  <header>
                    <strong>{item.role_name}</strong>
                    <span className="badge">{item.output_type ? (outputTypeText[item.output_type] || item.output_type) : '自由输出'}</span>
                  </header>
                  <p>{item.bio}</p>
                  {item.matched_dimensions.length > 0 && (
                    <div className="recommend-dimensions">
                      {item.matched_dimensions.map(label => <span key={label} className="tag-pill">{label}</span>)}
                    </div>
                  )}
                  <div className="recommend-reason">
                    <span className="label">匹配摘要</span>
                    <p>{item.reason_summary || item.recommendation_reason}</p>
                  </div>
                  {item.reason_evidence.length > 0 && (
                    <div className="recommend-evidence">
                      <span className="label">匹配依据</span>
                      <ul>
                        {item.reason_evidence.map(evidence => <li key={evidence}>{evidence}</li>)}
                      </ul>
                    </div>
                  )}
                  {item.caution && (
                    <div className="recommend-caution">
                      <span className="label">使用提醒</span>
                      <p>{item.caution}</p>
                    </div>
                  )}
                  <div className="recommend-scenarios">
                    <span className="label">适用场景</span>
                    <span>{item.applicable_scenarios_label || '待补齐'}</span>
                  </div>
                  <div className="marketplace-meta">
                    {item.match_score !== null && <span>匹配分 {item.match_score?.toFixed(2)}</span>}
                    {item.knowledge_boundary && <span>{item.knowledge_boundary}</span>}
                  </div>
                  <div className="marketplace-actions">
                    <Link to={'/roles/' + item.role_id + '/exports'} className="primary-btn small-btn">直接试用</Link>
                    <Link to={`/roles/${item.role_id}`} className="secondary-btn small-btn">角色详情</Link>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="recommend-empty">
              {recommendResult.result_type === 'out_of_scope' && <p>该需求不属于企业正常业务决策场景范围，当前不推荐角色。</p>}
              {recommendResult.result_type === 'no_match' && <p>{recommendResult.unmatched_intent_summary || '当前已发布角色未覆盖该业务意图。'}</p>}
              {recommendResult.result_type === 'service_error' && <p>{recommendResult.service_error_message || '推荐服务暂时不可用。'}</p>}
            </div>
          )}
        </div>
      ) : (
        <>
          <div className="marketplace-filter">
            <select value={category} onChange={e => setCategory(e.target.value)}>
              <option value="">全分类</option>
              {Object.entries(categoryText).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
            </select>
          </div>

          {loading ? <div className="page-loading">正在加载资产市场...</div> : (
            <div className="marketplace-grid">
              {roles.map(role => (
                <article key={role.role_id} className="marketplace-card">
                  <header>
                    <strong>{role.role_name}</strong>
                    <span className="badge">{role.output_type ? (outputTypeText[role.output_type] || role.output_type) : '自由输出'}</span>
                  </header>
                  <p>{role.summary || role.bio}</p>
                  <div className="marketplace-meta">
                    <span>{categoryText[role.category] || role.category}</span>
                    <span>{outputModeText[role.output_mode]}</span>
                    {role.business_domain && <span>{role.business_domain}</span>}
                  </div>
                  {!role.recommend_pool_eligible && <p className="subtle pool-hint">说明卡或业务画像还不完整，暂不进入 AI 推荐池。</p>}
                  <div className="marketplace-actions">
                    <Link to={'/roles/' + role.role_id + '/exports'} className="primary-btn small-btn">外供与调用</Link>
                    <Link to={`/roles/${role.role_id}`} className="secondary-btn small-btn">详情</Link>
                  </div>
                </article>
              ))}
              {roles.length === 0 && <div className="empty-state">当前没有符合筛选条件的已发布角色。</div>}
            </div>
          )}
        </>
      )}
    </section>
  );
}
