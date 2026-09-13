export default function StatCard({ label, value, hint, tone = 'default' }) {
  return <article className={`stat-card ${tone}`}>
    <div className="stat-label">{label}</div>
    <div className="stat-value">{value}</div>
    <div className="stat-hint">{hint}</div>
  </article>
}
