const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export const isMockMode = () => import.meta.env.VITE_USE_MOCK === 'true'

export function getToken() {
  return localStorage.getItem('odatrade_token')
}

async function mockLayer() {
  return import('./mock/mockApi')
}

export async function api(path, options = {}) {
  if (isMockMode()) {
    const { mockApi } = await mockLayer()
    return mockApi(path, options)
  }

  const headers = { 'Content-Type': 'application/json', ...options.headers }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  return res.json()
}

export async function login(username, password) {
  const data = await api('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) })
  if (data.access_token) localStorage.setItem('odatrade_token', data.access_token)
  return data
}

export function connectWS(path, onMessage) {
  if (isMockMode()) {
    let ws = { close() {} }
    mockLayer().then(({ mockConnectWS }) => {
      ws = mockConnectWS(path, onMessage)
    })
    return ws
  }

  const wsUrl = (import.meta.env.VITE_API_BASE || 'http://localhost:8000').replace('http', 'ws')
  const ws = new WebSocket(`${wsUrl}${path}`)
  ws.onmessage = (e) => onMessage(JSON.parse(e.data))
  return ws
}

if (isMockMode() && !getToken()) {
  localStorage.setItem('odatrade_token', 'mock-prototype-token')
}
