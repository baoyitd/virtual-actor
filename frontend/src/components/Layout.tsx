import { BookOpen, LogOut, Plus, ShieldCheck, Users } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import type { User } from '../api';

export function Layout({ children, user, onLogout }: { children: React.ReactNode; user: User; onLogout: () => void }) {
  return (
    <div className="app-shell">
      <aside className="side-nav">
        <div className="side-brand">
          <div className="brand-mark small">VA</div>
          <div>
            <strong>角色产品</strong>
            <span>Virtual Actor</span>
          </div>
        </div>
        <nav>
          <NavLink to="/" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}><Users size={18} />角色资产</NavLink>
          <NavLink to="/create" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}><Plus size={18} />新建角色</NavLink>
          <div className="nav-note"><BookOpen size={16} />知识平台真实集成</div>
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
