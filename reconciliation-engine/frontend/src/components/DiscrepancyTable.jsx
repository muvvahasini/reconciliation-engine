import { AlertTriangle, CheckCircle2, Copy, ExternalLink, SearchX } from 'lucide-react'

const labels = {
  MISSING_IN_SYSTEM_B: 'Missing in B',
  ORPHAN_IN_SYSTEM_B: 'Orphan in B',
  DUPLICATE_IN_SYSTEM_B: 'Duplicate in B',
  VALUE_MISMATCH: 'Value mismatch',
}

const icons = {
  MISSING_IN_SYSTEM_B: SearchX,
  ORPHAN_IN_SYSTEM_B: AlertTriangle,
  DUPLICATE_IN_SYSTEM_B: Copy,
  VALUE_MISMATCH: ExternalLink,
}

function money(value) {
  if (value === null || value === undefined || value === '') return '—'
  return value
}

export default function DiscrepancyTable({ items }) {
  if (!items.length) return <div className="empty-state"><CheckCircle2 size={34}/><h3>Everything reconciles</h3><p>No disagreements match the current tenant and reason filters.</p></div>

  return <div className="table-shell">
    <table>
      <thead><tr><th>Record</th><th>Location</th><th>Reason</th><th>System A</th><th>System B</th><th>Evidence</th></tr></thead>
      <tbody>{items.map((row, index) => {
        const Icon = icons[row.reason] || AlertTriangle
        return <tr key={`${row.reason}-${row.record_id}-${index}`}>
          <td><div className="record-cell"><strong>{row.record_id}</strong><span>{row.org_id}</span></div></td>
          <td><span className="location-chip">{row.location_id}</span></td>
          <td><span className={`reason-badge ${row.reason.toLowerCase()}`}><Icon size={13}/>{labels[row.reason]}</span></td>
          <td className="value a">{money(row.val_a)}</td>
          <td className="value b">{money(row.val_b)}</td>
          <td className="evidence">{row.entry_ids?.length ? row.entry_ids.join(', ') : 'No B entry'}</td>
        </tr>
      })}</tbody>
    </table>
  </div>
}
