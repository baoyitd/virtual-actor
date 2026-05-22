import { HashRouter, Navigate, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { api, getToken, setToken } from './api';
import type { User } from './api';
import { Layout } from './components/Layout';
import { RoleList } from './pages/RoleList';
import { RoleDetail } from './pages/RoleDetail';
import { RoleEdit } from './pages/RoleEdit';
import { RoleTest } from './pages/RoleTest';

function Login({ onLogin }: { onLogin: (user: User) => void }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await api.login(username, password);
      setToken(result.access_token);
      onLogin(result.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-shell">
      <section className="login-panel">
        <div className="brand-mark">VA</div>
        <h1>角色资产管理平台</h1>
        <p>面向企业 AI 决策场景的虚拟专家配置、知识绑定与发布管理。</p>
        <label>账号</label>
        <input value={username} onChange={e => setUsername(e.target.value)} />
        <label>密码</label>
        <input value={password} onChange={e => setPassword(e.target.value)} type="password" onKeyDown={e => e.key === 'Enter' && submit()} />
        {error && <div className="form-error">{error}</div>}
        <button className="primary-btn" onClick={submit} disabled={loading}>{loading ? '登录中...' : '登录'}</button>
      </section>
    </main>
  );
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [checking, setChecking] = useState(Boolean(getToken()));

  useEffect(() => {
    if (!getToken()) return;
    api.me().then(setUser).catch(() => setToken(null)).finally(() => setChecking(false));
  }, []);

  if (checking) return <div className="page-loading">正在校验登录状态...</div>;
  if (!user) return <Login onLogin={setUser} />;

  return (
    <HashRouter>
      <Layout user={user} onLogout={() => { setToken(null); setUser(null); }}>
        <Routes>
          <Route path="/" element={<RoleList />} />
          <Route path="/roles/:id" element={<RoleDetail />} />
          <Route path="/roles/:id/edit" element={<RoleEdit />} />
          <Route path="/roles/:id/test" element={<RoleTest />} />
          <Route path="/create" element={<RoleEdit />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </HashRouter>
  );
}
