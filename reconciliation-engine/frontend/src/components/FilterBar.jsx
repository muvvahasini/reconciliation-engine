import { ArrowDownUp, Filter, Building2 } from 'lucide-react'

export default function FilterBar({ tenant, setTenant, tenants, reason, setReason, sort, setSort }) {
  return <section className="filter-panel">
    <div className="filter-heading"><Filter size={17}/><span>Audit scope</span></div>
    <div className="filters">
      <label className="field">
        <span><Building2 size={14}/> Tenant</span>
        <select value={tenant} onChange={e => setTenant(e.target.value)}>
          {tenants.map(t => <option key={t.org_id} value={t.org_id}>{t.org_id}</option>)}
        </select>
      </label>
      <label className="field">
        <span>Reason</span>
        <select value={reason} onChange={e => setReason(e.target.value)}>
          <option value="ALL">All discrepancies</option>
          <option value="MISSING_IN_SYSTEM_B">Missing in B</option>
          <option value="ORPHAN_IN_SYSTEM_B">Orphan in B</option>
          <option value="DUPLICATE_IN_SYSTEM_B">Duplicate in B</option>
          <option value="VALUE_MISMATCH">Value mismatch</option>
        </select>
      </label>
      <button className="sort-button" onClick={() => setSort(sort === 'asc' ? 'desc' : 'asc')}>
        <ArrowDownUp size={16}/>{sort === 'asc' ? 'Lowest value' : 'Highest value'}
      </button>
    </div>
  </section>
}
