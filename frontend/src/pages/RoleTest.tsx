import { ArrowLeft, Send, ShieldAlert, Star } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api';
import type { RoleDetail, TestResult } from '../api';

function sortHistory(items: TestResult[]) {
  return [...items].sort((a, b) => {
    const aTime = a.tested_at ? new Date(a.tested_at).getTime() : 0;
    const bTime = b.tested_at ? new Date(b.tested_at).getTime() : 0;
    return aTime - bTime;
  });
}

export function RoleTest() {
  const { id } = useParams<{ id: string }>();
  const [role, setRole] = useState<RoleDetail | null>(null);
  const [history, setHistory] = useState<TestResult[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const historyRef = useRef<HTMLDivElement | null>(null);

  const load = async () => {
    if (!id) return;
    setLoading(true);
    setError('');
    try {
      const [r, h] = await Promise.all([api.getRole(id), api.testHistory(id)]);
      setRole(r);
      setHistory(sortHistory(h));
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载测试台失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  useEffect(() => {
    const node = historyRef.current;
    if (!node) return;
    node.scrollTo({ top: node.scrollHeight, behavior: 'smooth' });
  }, [history.length, sending]);

  const send = async () => {
    if (!id || !input.trim()) return;
    setSending(true);
    setError('');
    try {
      const result = await api.runTest(id, input.trim());
      const normalized = result.test_output?.trim() ? result.test_output : '测试已完成，但未返回可展示内容。';
      if (!result.test_output?.trim()) {
        setError('测试已完成，但模型未返回可展示内容，请检查网关或模型响应。');
      }
      setHistory(prev => sortHistory([...prev, { ...result, test_output: normalized }]));
      setInput('');
    } catch (err) {
      setError(err instanceof Error ? err.message : '测试失败');
    } finally {
      setSending(false);
    }
  };

  const rate = async (testId: string, score: number) => {
    const result = await api.rateTest(testId, score);
    setHistory(prev => prev.map(item => item.id === testId ? result : item));
  };

  if (loading) return <div className="page-loading">正在加载角色测试台...</div>;
  if (!role) return <div className="empty-state">角色不存在或无权访问</div>;

  return (
    <section className="page test-page">
      <div className="page-head compact">
        <div>
          <Link to={`/roles/${id}`} className="back-link"><ArrowLeft size={16} />返回角色详情</Link>
          <h1>测试：{role.name}</h1>
          <p className="subtle">测试会调用真实知识平台检索，并记录来源、评分和版本。</p>
        </div>
      </div>
      {error && <div className="alert error"><ShieldAlert size={17} />{error}</div>}

      <div className="test-layout">
        <main className="chat-panel">
          <div className="chat-history" ref={historyRef}>
            {history.length === 0 && <div className="empty-state">暂无测试记录，输入问题开始验证角色表现。</div>}
            {history.map(item => (
              <article key={item.id} className="chat-record">
                <div className="question">用户：{item.test_input}</div>
                <div className="answer">{item.test_output?.trim() || '测试已完成，但未返回可展示内容。'}</div>
                <div className="source-line">
                  {item.knowledge_retrieved.length === 0 ? '未返回知识来源' : item.knowledge_retrieved.map(s => `${s.source} (${s.score})`).join(' / ')}
                </div>
                <div className="rating-line">
                  {[1, 2, 3, 4, 5].map(score => (
                    <button key={score} className={item.human_rating && score <= item.human_rating ? 'active' : ''} onClick={() => rate(item.id, score)} title={`${score} 分`}><Star size={15} /></button>
                  ))}
                  <span>{item.tested_at ? new Date(item.tested_at).toLocaleString('zh-CN') : ''}</span>
                </div>
              </article>
            ))}
            {sending && (
              <article className="chat-record pending">
                <div className="question">用户：{input.trim()}</div>
                <div className="answer">正在调用知识检索与模型，请稍候...</div>
              </article>
            )}
          </div>
          <div className="chat-input">
            <textarea value={input} onChange={e => setInput(e.target.value)} placeholder="输入业务问题，验证角色是否能基于绑定知识给出可靠回答" onKeyDown={e => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) send();
            }} />
            <button className="primary-btn" onClick={send} disabled={sending}><Send size={17} />{sending ? '测试中...' : '发送测试'}</button>
          </div>
        </main>
        <aside className="detail-section test-context">
          <h2>测试上下文</h2>
          <p><strong>当前版本</strong><span>{role.role_version_id}</span></p>
          <p><strong>模型</strong><span>{role.model_binding ? `${role.model_binding.model_name} / max_tokens=${role.model_binding.max_tokens}` : '-'}</span></p>
          <p><strong>绑定知识</strong><span>{role.knowledge_refs.length} 条</span></p>
          <p><strong>测试记录</strong><span>{history.length} 次</span></p>
        </aside>
      </div>
    </section>
  );
}
