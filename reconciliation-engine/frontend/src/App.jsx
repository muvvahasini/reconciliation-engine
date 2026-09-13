import { useEffect, useMemo, useState } from 'react'
import { Activity, Database, RefreshCw, ShieldCheck, Sparkles } from 'lucide-react'
import { getDiscrepancies, getTenants } from './api'
import StatCard from './components/StatCard'
import FilterBar from './components/FilterBar'
import DiscrepancyTable from './components/DiscrepancyTable'

export default function App() {
  const [tenants, setTenants] = useState([])
  const [tenant, setTenant] = useState('')
  const [reason, setReason] = useState('ALL')
  const [sort, setSort] = useState('asc')
  const [data, setData] = useState({ count: 0, results: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadTenants() {
    const result = await getTenants()
    setTenants(result.results)
    if (!tenant && result.results[0]) setTenant(result.results[0].org_id)
  }

  async function loadData() {
    if (!tenant) return
    setLoading(true); setError('')
    try { setData(await getDiscrepancies(tenant, reason, sort)) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { loadTenants().catch(e => { setError(e.message); setLoading(false) }) }, [])
  useEffect(() => { loadData() }, [tenant, reason, sort])

  const summary = useMemo(() => {
    const counts = data.results.reduce((acc, row) => { acc[row.reason] = (acc[row.reason] || 0) + 1; return acc }, {})
    return counts
  }, [data.results])

  return <main className="app-shell">
    <header className="topbar">
      <div className="brand"><div className="brand-mark"><Sparkles size={17}/></div><div><strong>RECONCILE</strong><span>Cross-system audit</span></div></div>
      <div className="system-status"><span className="status-dot"/> Live audit workspace <span className="divider"/> Tenant scoped</div>
    </header>

    <section className="hero">
      <div>
        <div className="eyebrow"><ShieldCheck size={15}/> DATA INTEGRITY / TENANT ISOLATION</div>
        <h1>Find the rows that <em>don't agree.</em></h1>
        <p>One focused view across System A and System B — normalized, reconciled, and strictly scoped to the selected organization.</p>
      </div>
      <div className="hero-meta"><Database size={18}/><span><b>240+</b> source rows<br/><small>raw exports preserved</small></span></div>
    </section>

    <div className="stats-grid">
      <StatCard label="Disagreements" value={data.count} hint="in current scope" tone="accent"/>
      <StatCard label="Missing in B" value={summary.MISSING_IN_SYSTEM_B || 0} hint="A has no matching entry"/>
      <StatCard label="Orphans" value={summary.ORPHAN_IN_SYSTEM_B || 0} hint="B has no A parent"/>
      <StatCard label="Duplicates / mismatches" value={(summary.DUPLICATE_IN_SYSTEM_B || 0) + (summary.VALUE_MISMATCH || 0)} hint="integrity exceptions"/>
    </div>

    <FilterBar tenant={tenant} setTenant={setTenant} tenants={tenants} reason={reason} setReason={setReason} sort={sort} setSort={setSort}/>

    <section className="results-head"><div><h2>Discrepancy register</h2><p>{loading ? 'Running reconciliation…' : `${data.count} exception${data.count === 1 ? '' : 's'} found for ${tenant || '—'}`}</p></div><button className="refresh" onClick={loadData} disabled={loading}><RefreshCw size={15} className={loading ? 'spin' : ''}/> Refresh</button></section>

    {error ? <div className="error-state">{error}</div> : <DiscrepancyTable items={data.results}/>} 

    <footer><span>Reconciliation Engine · assessment build</span><span>Raw data retained · normalized matching · tenant boundary enforced</span></footer>
  </main>
}
