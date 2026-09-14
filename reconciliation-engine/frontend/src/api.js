const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export async function getTenants() {
  const response = await fetch(`${API_BASE}/api/tenants/`)
  if (!response.ok) throw new Error('Unable to load tenants')
  return response.json()
}

export async function getDiscrepancies(orgId, reason, sort) {
  const params = new URLSearchParams({ org_id: orgId, reason, sort })
  const response = await fetch(`${API_BASE}/api/discrepancies/?${params}`)
  const body = await response.json()
  if (!response.ok) throw new Error(body.error || 'Unable to load discrepancies')
  return body
}
