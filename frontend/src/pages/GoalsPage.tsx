import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'

type Goal = {
  goal_id: string
  goal_type: string
  goal_name: string
  target_amount: number
  current_funded_amount: number
  target_date: string
  priority: 'LOW' | 'MEDIUM' | 'HIGH'
  funded_percentage: number
  overdue: boolean
  inconsistent: boolean
}

type FormState = {
  goal_type: string
  goal_name: string
  target_amount: string
  current_funded_amount: string
  target_date: string
  priority: string
}

const emptyForm: FormState = {
  goal_type: 'WEALTH_CREATION',
  goal_name: '',
  target_amount: '',
  current_funded_amount: '0',
  target_date: '',
  priority: 'MEDIUM',
}

const fmt = (n: number) => new Intl.NumberFormat('en-IN', {
  style: 'currency', currency: 'INR', maximumFractionDigits: 0,
}).format(n)

export default function GoalsPage() {
  const { id } = useParams()
  const [goals, setGoals] = useState<Goal[]>([])
  const [form, setForm] = useState<FormState>(emptyForm)
  const [editing, setEditing] = useState<Goal | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const title = useMemo(() => editing ? `Edit ${editing.goal_name}` : 'Create a goal', [editing])

  async function load() {
    if (!id) return
    setLoading(true)
    setError('')
    try {
      setGoals(await api<Goal[]>(`/customers/${id}/goals`))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load goals')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [id])

  function beginEdit(goal: Goal) {
    setEditing(goal)
    setForm({
      goal_type: goal.goal_type,
      goal_name: goal.goal_name,
      target_amount: String(goal.target_amount),
      current_funded_amount: String(goal.current_funded_amount),
      target_date: goal.target_date,
      priority: goal.priority,
    })
    setSuccess('')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function cancelEdit() {
    setEditing(null)
    setForm(emptyForm)
    setError('')
  }

  function validate() {
    if (!form.goal_name.trim()) return 'Goal name is required'
    if (!form.target_date) return 'Target date is required'
    if (Number(form.target_amount) <= 0) return 'Target amount must be greater than zero'
    if (Number(form.current_funded_amount) < 0) return 'Funded amount cannot be negative'
    return ''
  }

  async function submit(e: FormEvent) {
    e.preventDefault()
    if (!id) return
    const validation = validate()
    if (validation) { setError(validation); return }

    setSaving(true)
    setError('')
    setSuccess('')
    try {
      const body = editing ? {
        goal_name: form.goal_name.trim(),
        target_amount: Number(form.target_amount),
        current_funded_amount: Number(form.current_funded_amount),
        target_date: form.target_date,
        priority: form.priority,
      } : {
        goal_type: form.goal_type,
        goal_name: form.goal_name.trim(),
        target_amount: Number(form.target_amount),
        current_funded_amount: Number(form.current_funded_amount),
        target_date: form.target_date,
        priority: form.priority,
      }

      if (editing) {
        await api(`/goals/${editing.goal_id}`, { method: 'PATCH', body: JSON.stringify(body) })
        setSuccess('Goal updated successfully.')
      } else {
        await api(`/customers/${id}/goals`, { method: 'POST', body: JSON.stringify(body) })
        setSuccess('Goal created successfully.')
      }
      setEditing(null)
      setForm(emptyForm)
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save goal')
    } finally {
      setSaving(false)
    }
  }

  return <section>
    <div className="page-header">
      <div>
        <Link className="text-link" to={`/customers/${id}`}>← Customer overview</Link>
        <h1>Financial goals</h1>
        <p className="muted">Create and maintain customer goals with server-side validation.</p>
      </div>
    </div>

    <div className="dashboard-grid goal-management-grid">
      <form className="card goal-form" onSubmit={submit}>
        <div className="card-title"><h2>{title}</h2>{editing && <button type="button" className="ghost" onClick={cancelEdit}>Cancel</button>}</div>
        <label>Goal name<input value={form.goal_name} onChange={e => setForm({...form, goal_name: e.target.value})} placeholder="Retirement corpus" /></label>
        <label>Goal type<select value={form.goal_type} onChange={e => setForm({...form, goal_type: e.target.value})} disabled={Boolean(editing)}>
          <option value="EDUCATION">Education</option>
          <option value="EMERGENCY_FUND">Emergency fund</option>
          <option value="HOME_PURCHASE">Home purchase</option>
          <option value="RETIREMENT">Retirement</option>
          <option value="TRAVEL">Travel</option>
          <option value="WEALTH_CREATION">Wealth creation</option>
        </select></label>
        <div className="form-two-col">
          <label>Target amount<input type="number" min="1" step="0.01" value={form.target_amount} onChange={e => setForm({...form, target_amount: e.target.value})} /></label>
          <label>Funded amount<input type="number" min="0" step="0.01" value={form.current_funded_amount} onChange={e => setForm({...form, current_funded_amount: e.target.value})} /></label>
        </div>
        <div className="form-two-col">
          <label>Target date<input type="date" value={form.target_date} onChange={e => setForm({...form, target_date: e.target.value})} /></label>
          <label>Priority<select value={form.priority} onChange={e => setForm({...form, priority: e.target.value})}><option>LOW</option><option>MEDIUM</option><option>HIGH</option></select></label>
        </div>
        {error && <div className="error-box">{error}</div>}
        {success && <div className="success-box">{success}</div>}
        <button className="primary" disabled={saving}>{saving ? 'Saving…' : editing ? 'Save changes' : 'Create goal'}</button>
      </form>

      <div className="card">
        <div className="card-title"><h2>Current goals</h2><span>{goals.length} total</span></div>
        {loading ? <p className="muted">Loading goals…</p> : goals.length === 0 ? <p className="muted">No goals for this customer.</p> : <div className="goal-list">
          {goals.map(g => <div className="goal" key={g.goal_id}>
            <div><strong>{g.goal_name}</strong><span>{g.priority} · due {g.target_date}</span></div>
            <div className="progress" aria-label={`${g.goal_name} ${g.funded_percentage}% funded`}><i style={{width: `${Math.min(g.funded_percentage, 100)}%`}} /></div>
            <div className="goal-foot"><span>{g.funded_percentage}% funded</span><span>{fmt(g.current_funded_amount)} / {fmt(g.target_amount)}</span></div>
            {(g.overdue || g.inconsistent) && <small className="warning">{g.overdue ? 'Overdue and not fully funded' : 'Funding exceeds target amount'}</small>}
            <button className="goal-edit" onClick={() => beginEdit(g)}>Edit goal</button>
          </div>)}
        </div>}
      </div>
    </div>
  </section>
}
