import { useState } from 'react'
import { login } from '../api'
import Badge from '../components/Badge'

export default function Login() {
  const [user, setUser] = useState('admin')
  const [pass, setPass] = useState('')
  const [err, setErr] = useState('')

  const handle = async () => {
    try {
      await login(user, pass)
      location.reload()
    } catch {
      setErr('Login failed')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-oda-bg">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-oda-surface/80 p-8 shadow-card backdrop-blur-sm">
        <Badge tone="info">Live API mode</Badge>
        <h2 className="mt-4 text-3xl font-bold text-white">OdaTrade</h2>
        <p className="mt-2 text-sm text-gray-400">Sign in to connect to the backend API.</p>
        <input
          className="mt-6 w-full rounded-xl border border-white/10 bg-oda-bg p-3 text-white outline-none focus:ring-2 focus:ring-oda-primary/40"
          placeholder="Username"
          value={user}
          onChange={e => setUser(e.target.value)}
        />
        <input
          className="mt-3 w-full rounded-xl border border-white/10 bg-oda-bg p-3 text-white outline-none focus:ring-2 focus:ring-oda-primary/40"
          type="password"
          placeholder="Password"
          value={pass}
          onChange={e => setPass(e.target.value)}
        />
        {err && <p className="mt-2 text-sm text-oda-accent">{err}</p>}
        <button
          onClick={handle}
          className="mt-5 w-full rounded-xl bg-gradient-to-r from-oda-primary to-cyan-400 py-3 font-semibold text-oda-bg"
        >
          Login
        </button>
      </div>
    </div>
  )
}
