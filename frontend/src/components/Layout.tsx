import { BarChart3, Database, LogOut, ShieldCheck, ShoppingBag, Users } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import type { User } from '../api';

export function Layout({ children, user, onLogout }: { children: React.ReactNode; user: User; onLogout: () => void }) {
  return (
    <div className="app-shell">
      <aside className="side-nav">
        <div className="side-brand">
          <div className="brand-mark small">VA</div>
          <div>
            <strong>角色资产平台</strong>
            <span>Role Asset Platform</span>
          </div>
        </div>
        <nav>
          <NavLink to="/marketplace" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}><ShoppingBag size={18} />资产市场</NavLink>
          <NavLink to="/" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}><Users size={18} />角色资产</NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}><BarChart3 size={18} />运营看板</NavLink>
          <NavLink to="/data-assets" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}><Database size={18} />数据资产管理</NavLink>
          <div className="nav-note">v0.5 冻结骨架：L1-L4 / 使用前说明与调用预览 / 治理发布 / 外供复用</div>
        </nav>
        <div className="side-user">
          <ShieldCheck size={18} />
          <div><strong>{user.username}</strong><span>内部商业试用</span></div>
          <button title="退出登录" onClick={onLogout}><LogOut size={17} /></button>
        </div>
      </aside>
      <main className="main-area">{children}</main>
    </div>
  );
}
