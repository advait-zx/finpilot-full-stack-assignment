import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, auth } from '../api'

export default function LoginPage() {
  const [username,setUsername]=useState('viewer'); const [password,setPassword]=useState('viewer123'); const [error,setError]=useState(''); const [loading,setLoading]=useState(false); const navigate=useNavigate()
  async function submit(e:FormEvent){ e.preventDefault(); setError(''); setLoading(true); try { const r=await api<{access_token:string;role:string}>('/auth/login',{method:'POST',body:JSON.stringify({username,password})}); auth.set(r.access_token,r.role); navigate('/customers') } catch(e){ setError(e instanceof Error?e.message:'Login failed') } finally { setLoading(false) } }
  return <div className="login-page"><div className="login-card"><div className="brand login-brand"><span className="brand-mark">F</span><div><strong>FinPilot</strong><small>Investment portfolio operations</small></div></div><h1>Welcome back</h1><p className="muted">Sign in with the seeded reviewer account.</p><form onSubmit={submit}><label>Username<input value={username} onChange={e=>setUsername(e.target.value)} autoComplete="username"/></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} autoComplete="current-password"/></label>{error&&<div className="error-box">{error}</div>}<button className="primary" disabled={loading}>{loading?'Signing in…':'Sign in'}</button></form><p className="hint">Viewer: viewer / viewer123 · Admin: admin / admin123</p></div></div>
}
