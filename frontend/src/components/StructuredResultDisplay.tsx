import { outputTypeText } from '../api';

const fieldLabels: Record<string, Record<string, string>> = {
  decision_advice: {
    position: '立场/倾向', key_reasons: '关键理由', major_risks: '主要风险',
    preconditions: '前置条件', suggested_actions: '建议动作', references: '引用依据',
  },
  risk_analysis: {
    key_findings: '关键发现', risk_items: '风险项', overall_risk_level: '综合风险等级',
    impact_scope: '影响范围', suggested_mitigations: '建议缓解措施', references: '引用依据',
  },
  policy_explanation: {
    applicable_clauses: '适用条款', clause_explanation: '条款解释',
    allowed_actions: '可做事项', prohibited_actions: '不可做事项', caveats: '注意事项',
    references: '引用依据',
  },
  review_findings: {
    issues: '问题项', items_to_confirm: '需确认事项', overall_severity: '综合严重等级',
    references: '引用依据',
  },
};

const subFieldLabels: Record<string, Record<string, string>> = {
  RiskItem: { risk: '风险描述', level: '风险等级', mitigation: '缓解措施' },
  RiskDetailItem: { item: '风险描述', severity: '严重等级', impact: '影响说明', mitigation: '缓解措施' },
  ReferenceItem: { source: '来源名称', section: '涉及章节', type: '依据类型' },
  ClauseItem: { clause: '条款标识', content: '条款原文' },
  IssueItem: { title: '问题标题', severity: '严重等级', description: '问题说明', suggestion: '修改建议' },
};

function getSubFieldType(parentKey: string): string {
  const map: Record<string, string> = {
    major_risks: 'RiskItem', risk_items: 'RiskDetailItem',
    references: 'ReferenceItem', applicable_clauses: 'ClauseItem', issues: 'IssueItem',
  };
  return map[parentKey] || '';
}

interface Props {
  data: Record<string, unknown>;
  outputType: string;
}

export function StructuredResultDisplay({ data, outputType }: Props) {
  const labels = fieldLabels[outputType] || {};
  const typeName = outputTypeText[outputType] || outputType;

  const renderValue = (key: string, value: unknown) => {
    if (value === null || value === undefined) return <span style={{ color: '#9ca3af' }}>-</span>;
    if (typeof value === 'string') return <span>{value}</span>;
    if (typeof value === 'number') return <span>{value}</span>;

    if (Array.isArray(value)) {
      if (value.length === 0) return <span style={{ color: '#9ca3af' }}>（空）</span>;
      const subType = getSubFieldType(key);
      const subLabels = subFieldLabels[subType] || {};
      if (subType && typeof value[0] === 'object' && value[0] !== null) {
        return (
          <div>
            {value.map((item, i) => (
              <div key={i} className="result-nested-item">
                {Object.entries(item as Record<string, unknown>).map(([sk, sv]) => (
                  <div key={sk} className="result-field-row">
                    <span className="result-field-label">{subLabels[sk] || sk}</span>
                    <span className="result-field-value">{typeof sv === 'object' ? JSON.stringify(sv) : String(sv ?? '-')}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        );
      }
      return (
        <ol style={{ margin: 0, paddingLeft: 20 }}>
          {value.map((item, i) => <li key={i}>{String(item)}</li>)}
        </ol>
      );
    }

    if (typeof value === 'object') {
      return <span>{JSON.stringify(value)}</span>;
    }

    return <span>{String(value)}</span>;
  };

  return (
    <div>
      <div style={{ fontSize: 13, color: '#516178', marginBottom: 8 }}>
        输出类型：{typeName}
      </div>
      {Object.entries(data).map(([key, value]) => (
        <div key={key} className="result-field-row">
          <span className="result-field-label">{labels[key] || key}</span>
          <span className="result-field-value">{renderValue(key, value)}</span>
        </div>
      ))}
    </div>
  );
}