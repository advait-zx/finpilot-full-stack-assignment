const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const auth = {
  token: () => sessionStorage.getItem('finpilot_token'),
  role: () => sessionStorage.getItem('finpilot_role'),
  set: (token: string, role: string) => { sessionStorage.setItem('finpilot_token', token); sessionStorage.setItem('finpilot_role', role) },
  clear: () => { sessionStorage.removeItem('finpilot_token'); sessionStorage.removeItem('finpilot_role') }
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  if (!(options.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  const token = auth.token()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const response = await fetch(`${API_URL}${path}`, { ...options, headers })
  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try { const body = await response.json(); detail = body.detail || detail } catch { /* ignore */ }
    throw new Error(detail)
  }
  return response.json()
}
