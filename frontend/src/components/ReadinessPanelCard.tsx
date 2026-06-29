import { Link } from 'react-router-dom';
import type { ReadinessPanel } from '../api';

function routeFor(roleId: string, screen: string | null) {
  if (screen === 'workspace') return `/roles/${roleId}/edit`;
  if (screen === 'briefing') return `/roles/${roleId}/briefing`;
  if (screen === 'publish') return `/roles/${roleId}/governance`;
  if (screen === 'exports') return `/roles/${roleId}/exports`;
  return null;
}

interface ReadinessPanelCardProps {
  roleId: string;
  title: string;
  panel: ReadinessPanel;
}

export function ReadinessPanelCard({ roleId, title, panel }: ReadinessPanelCardProps) {
  return (
    <article className="detail-section readiness-card">
      <div className="section-title-row">
        <div>
          <h2>{title}</h2>
          <p className="subtle">{panel.ready ? '当前已闭合' : '当前仍有待补齐项'}</p>
        </div>
        <span className={`tag-pill ${panel.ready ? 'success' : 'warning'}`}>
          {panel.ready ? 'Ready' : 'Pending'}
        </span>
      </div>

      <div className="readiness-group">
        <h3>硬要求</h3>
        <div className="mini-check-list">
          {panel.hard_requirements.map(item => {
            const target = routeFor(roleId, item.route_screen);
            return (
              <div key={item.key} className={`mini-check ${item.status}`}>
                <div>
                  <strong>{item.label}</strong>
                  <span>{item.message}</span>
                </div>
                {target && item.status !== 'met' && <Link className="text-link" to={target}>去补齐</Link>}
              </div>
            );
          })}
        </div>
      </div>

      {panel.soft_hints.length > 0 && (
        <div className="readiness-group">
          <h3>软提示</h3>
          <div className="mini-check-list">
            {panel.soft_hints.map(item => {
              const target = routeFor(roleId, item.route_screen);
              return (
                <div key={item.key} className={`mini-check ${item.status}`}>
                  <div>
                    <strong>{item.label}</strong>
                    <span>{item.message}</span>
                  </div>
                  {target && item.status !== 'met' && <Link className="text-link" to={target}>查看</Link>}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </article>
  );
}
