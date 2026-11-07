import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { auth } from '../api'

export default function Layout() {
  const navigate = useNavigate()
  const role = auth.role()
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">F</span><div><strong>FinPilot</strong><small>Wealth Operations</small></div></div>
      <nav>
        <NavLink to="/customers">Customers</NavLink>
        {role === 'ADMIN' && <NavLink to="/admin/import">Admin Import</NavLink>}
      </nav>
      <div className="sidebar-bottom"><span className="role-pill">{role}</span><button className="ghost" onClick={() => { auth.clear(); navigate('/login') }}>Sign out</button></div>
    </aside>
    <main className="main"><Outlet /></main>
  </div>
}
