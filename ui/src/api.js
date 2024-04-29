const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export function getToken() { return localStorage.getItem('odatrade_token') }

export async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  return res.json()
}

export async function login(username, password) {
  const data = await api('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) })
  if (data.access_token) localStorage.setItem('odatrade_token', data.access_token)
  return data
}

export function connectWS(path, onMessage) {
  const wsUrl = (import.meta.env.VITE_API_BASE || 'http://localhost:8000').replace('http', 'ws')
  const ws = new WebSocket(`${wsUrl}${path}`)
  ws.onmessage = (e) => onMessage(JSON.parse(e.data))
  return ws
}
