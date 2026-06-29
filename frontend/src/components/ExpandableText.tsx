import { useState, type CSSProperties } from 'react';

interface ExpandableTextProps {
  text: string | null | undefined;
  collapsedLines?: number;
  emptyText?: string;
}

export function ExpandableText({
  text,
  collapsedLines = 6,
  emptyText = '暂无内容',
}: ExpandableTextProps) {
  const normalized = (text || '').trim();
  const [expanded, setExpanded] = useState(false);
  const lineCount = normalized.split('\n').length;
  const shouldCollapse = normalized.length > 220 || lineCount > collapsedLines;

  if (!normalized) {
    return <span className="muted-text">{emptyText}</span>;
  }

  const style = {
    '--collapsed-lines': collapsedLines,
  } as CSSProperties;

  return (
    <div className="expandable-text-block">
      <div
        className={`expandable-text ${shouldCollapse && !expanded ? 'collapsed' : ''}`}
        style={style}
      >
        {normalized}
      </div>
      {shouldCollapse && (
        <button
          className="text-toggle-btn"
          type="button"
          onClick={() => setExpanded(prev => !prev)}
        >
          {expanded ? '收起' : '展开全部'}
        </button>
      )}
    </div>
  );
}
