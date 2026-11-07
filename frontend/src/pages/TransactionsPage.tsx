import { FormEvent, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'

const fmt=(n:number)=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:2}).format(n)

type Account={account_id:string;account_type:string;provider:string;status:string}
type Profile={accounts:Account[]}

export default function TransactionsPage(){
  const{id}=useParams();
  const[items,setItems]=useState<any[]>([]);
  const[meta,setMeta]=useState<any>({page:1,pages:0,total:0});
  const[accounts,setAccounts]=useState<Account[]>([]);
  const[type,setType]=useState('');
  const[start,setStart]=useState('');
  const[end,setEnd]=useState('');
  const[account,setAccount]=useState('');
  const[instrument,setInstrument]=useState('');
  const[loading,setLoading]=useState(false);
  const[error,setError]=useState('');

  async function load(page=1){
    if(!id)return;
    setLoading(true);setError('');
    const qs=new URLSearchParams({page:String(page),page_size:'25'});
    if(type)qs.set('transaction_type',type);
    if(start)qs.set('start_date',start);
    if(end)qs.set('end_date',end);
    if(account)qs.set('account_id',account);
    if(instrument.trim())qs.set('instrument_id',instrument.trim());
    try{const r=await api<any>(`/customers/${id}/transactions?${qs}`);setItems(r.items);setMeta(r.meta)}catch(e){setError(e instanceof Error?e.message:'Failed')}finally{setLoading(false)}
  }

  useEffect(()=>{
    if(!id)return;
    load();
    api<Profile>(`/customers/${id}`).then(r=>setAccounts(r.accounts)).catch(()=>{})
  },[id]);

  function submit(e:FormEvent){e.preventDefault();load(1)}
  function clearFilters(){setType('');setStart('');setEnd('');setAccount('');setInstrument('');setTimeout(()=>load(1),0)}

  return <section>
    <div className="page-header"><div><Link className="text-link" to={`/customers/${id}`}>← Customer overview</Link><h1>Transactions</h1><p className="muted">Server-side filtering and pagination · {meta.total} records</p></div></div>
    <form className="filter-card transaction-filters" onSubmit={submit}>
      <label>Account<select value={account} onChange={e=>setAccount(e.target.value)}><option value="">All accounts</option>{accounts.map(a=><option value={a.account_id} key={a.account_id}>{a.account_id} · {a.account_type}</option>)}</select></label>
      <label>Instrument ID<input placeholder="e.g. I0010" value={instrument} onChange={e=>setInstrument(e.target.value)}/></label>
      <label>Type<select value={type} onChange={e=>setType(e.target.value)}><option value="">All types</option><option>BUY</option><option>SELL</option><option>DIVIDEND</option><option>FEE</option></select></label>
      <label>From<input type="date" value={start} onChange={e=>setStart(e.target.value)}/></label>
      <label>To<input type="date" value={end} onChange={e=>setEnd(e.target.value)}/></label>
      <div className="filter-actions"><button className="primary">Apply</button><button type="button" className="secondary-button" onClick={clearFilters}>Clear</button></div>
    </form>
    {error&&<div className="error-box">{error}</div>}
    <div className="table-card"><table><thead><tr><th>Date</th><th>Account</th><th>Instrument</th><th>Type</th><th>Quantity</th><th>Price</th><th>Amount</th><th>Status</th></tr></thead><tbody>{items.map(t=><tr key={t.transaction_id} className={t.status==='REVERSED'?'muted-row':''}><td>{t.trade_date}</td><td>{t.account_id}</td><td><strong>{t.symbol||'—'}</strong><span>{t.instrument_name||t.instrument_id}</span></td><td>{t.transaction_type}</td><td>{Number(t.quantity).toLocaleString()}</td><td>{fmt(Number(t.price))}</td><td>{fmt(Number(t.amount))}</td><td><span className={`status ${t.status.toLowerCase()}`}>{t.status}</span></td></tr>)}</tbody></table>{loading&&<div className="table-overlay">Loading…</div>}</div>
    <div className="pagination"><button className="ghost" disabled={meta.page<=1} onClick={()=>load(meta.page-1)}>Previous</button><span>Page {meta.page} of {meta.pages||1}</span><button className="ghost" disabled={meta.page>=meta.pages} onClick={()=>load(meta.page+1)}>Next</button></div>
  </section>
}
