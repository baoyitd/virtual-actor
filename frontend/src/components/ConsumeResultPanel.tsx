import { boundaryDimensionText, consumeStatusText, outputTypeText } from '../api';
import { ExpandableText } from './ExpandableText';
import { StructuredResultDisplay } from './StructuredResultDisplay';

const STATUS_COLOR: Record<string, string> = {
  success: '#167c47',
  insufficient_context: '#b16a05',
  insufficient_knowledge: '#c16012',
  boundary_blocked: '#b4232b',
  system_failed: '#7a1118',
  undefined: '#66758a',
};

type SourceItem = {
  type?: string;
  source?: string;
  score?: number;
};

type ResultLike = {
  status: string;
  status_reason: string;
  answer: string;
  boundary_status: Record<string, string> | null;
  structured_result: Record<string, unknown> | null;
  output_type: string | null;
  sources: Array<Record<string, unknown>> | null;
  role_version_id: string;
  created_at: string | null;
  query?: string | null;
  context?: string | null;
  validation_record_id?: string;
  usage_record_id?: string;
};

interface ConsumeResultPanelProps {
  title: string;
  result: ResultLike;
}

function formatTime(value: string | null) {
  if (!value) return '未记录';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date);
}

function formatOutputLabel(outputType: string | null) {
  return outputType ? (outputTypeText[outputType] || outputType) : '自由输出';
}

function toSourcesByType(sources: Array<Record<string, unknown>> | null) {
  const items = (sources || []) as SourceItem[];
  return {
    knowledge: items.filter(item => item.type === 'knowledge'),
    data: items.filter(item => item.type === 'data'),
  };
}

function renderSourceItems(items: SourceItem[], emptyText: string) {
  if (items.length === 0) {
    return <span className="muted-text">{emptyText}</span>;
  }
  return (
    <div className="source-chip-list">
      {items.map((item, index) => (
        <div key={`${item.type || 'source'}-${item.source || index}`} className="source-chip">
          <strong>{item.source || '未命名来源'}</strong>
          {typeof item.score === 'number' && (
            <small>相关度 {item.score.toFixed(2)}</small>
          )}
        </div>
      ))}
    </div>
  );
}

export function ConsumeResultPanel({ title, result }: ConsumeResultPanelProps) {
  const groupedSources = toSourcesByType(result.sources);
  const hasStructuredResult = Boolean(result.structured_result && Object.keys(result.structured_result).length > 0);
  const boundaryStatus = result.boundary_status || {};
  const traceId = result.validation_record_id || result.usage_record_id || '';

  return (
    <div className="result-card result-card-detailed">
      <div className="consume-status-bar" style={{ background: STATUS_COLOR[result.status] || '#66758a' }}>
        <strong>{consumeStatusText[result.status] || result.status}</strong>
        <span>{result.status_reason}</span>
      </div>

      <div className="result-summary-grid">
        <div className="result-summary-card result-summary-card-wide">
          <strong>{title}</strong>
          <ExpandableText text={result.query} collapsedLines={3} emptyText="当前未记录测试问题。" />
        </div>
        {result.context && (
          <div className="result-summary-card result-summary-card-wide">
            <strong>业务上下文</strong>
            <ExpandableText text={result.context} collapsedLines={4} />
          </div>
        )}
        <div className="result-summary-card">
          <strong>执行时间</strong>
          <span>{formatTime(result.created_at)}</span>
        </div>
        <div className="result-summary-card">
          <strong>输出方式</strong>
          <span>{formatOutputLabel(result.output_type)}</span>
        </div>
        <div className="result-summary-card result-summary-card-wide">
          <strong>本次结论</strong>
          <ExpandableText text={result.status_reason} collapsedLines={3} />
        </div>
      </div>

      {hasStructuredResult && (
        <div className="consume-structured">
          <h3>结构化结果</h3>
          <StructuredResultDisplay data={result.structured_result || {}} outputType={result.output_type || ''} />
        </div>
      )}

      <div className="consume-answer">
        <h3>自然语言回答</h3>
        <ExpandableText text={result.answer} collapsedLines={8} />
      </div>

      <div className="consume-sources">
        <h3>命中依据</h3>
        <div className="consume-sources-grid">
          <div className="source-group-card">
            <strong>知识来源</strong>
            {renderSourceItems(groupedSources.knowledge, '当前未命中真实知识来源。')}
          </div>
          <div className="source-group-card">
            <strong>数据来源</strong>
            {renderSourceItems(groupedSources.data, '当前未命中结构化业务数据。')}
          </div>
        </div>
      </div>

      <div className="consume-boundary">
        <h3>边界判断</h3>
        <div className="boundary-grid">
          <div>
            <strong>知识边界</strong>
            <span>{boundaryDimensionText[boundaryStatus.knowledge_boundary] || boundaryStatus.knowledge_boundary || '未返回'}</span>
          </div>
          <div>
            <strong>能力边界</strong>
            <span>{boundaryDimensionText[boundaryStatus.capability_boundary] || boundaryStatus.capability_boundary || '未返回'}</span>
          </div>
        </div>
      </div>

      {traceId && (
        <details className="trace-details">
          <summary>查看技术追溯</summary>
          <div className="trace-details-body">
            <div className="trace-row">
              <strong>role_version_id</strong>
              <span>{result.role_version_id}</span>
            </div>
            {result.validation_record_id && (
              <div className="trace-row">
                <strong>validation_record_id</strong>
                <span>{result.validation_record_id}</span>
              </div>
            )}
            {result.usage_record_id && (
              <div className="trace-row">
                <strong>usage_record_id</strong>
                <span>{result.usage_record_id}</span>
              </div>
            )}
          </div>
        </details>
      )}
    </div>
  );
}
