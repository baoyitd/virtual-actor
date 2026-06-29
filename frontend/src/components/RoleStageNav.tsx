import { FileText, Layers3, Package2, ShieldCheck, TestTube2 } from 'lucide-react';
import { NavLink } from 'react-router-dom';

export function RoleStageNav({ roleId }: { roleId: string }) {
  const items = [
    { to: '/roles/' + roleId + '/edit', label: '01 角色定义工作台', icon: Layers3, note: 'L1-L4 定义骨架' },
    { to: '/roles/' + roleId + '/briefing', label: '02 使用前说明', icon: FileText, note: '说明卡与调用预览' },
    { to: '/roles/' + roleId + '/test', label: '03 试用与测试', icon: TestTube2, note: '测试当前版本' },
    { to: '/roles/' + roleId + '/governance', label: '04 治理与发布', icon: ShieldCheck, note: '治理项 + 发布 / 归档' },
    { to: '/roles/' + roleId + '/exports', label: '05 外供与调用', icon: Package2, note: '外供包 + 验证调用 + 记录' },
  ];

  return (
    <aside className="role-stage-nav">
      <div className="role-stage-head">
        <p className="eyebrow">Role Flow</p>
        <strong>v0.5 主链路</strong>
        <span>先定义与说明，保存说明后进入测试；发布后进入外供与调用。</span>
      </div>
      <div className="role-stage-group">
        {items.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => (isActive ? 'role-stage-link active' : 'role-stage-link')}
          >
            <item.icon size={18} />
            <div>
              <strong>{item.label}</strong>
              <small>{item.note}</small>
            </div>
          </NavLink>
        ))}
      </div>
    </aside>
  );
}
