import { useState } from 'react'
import { login } from '../api'

export default function Login() {
  const [user, setUser] = useState('admin')
  const [pass, setPass] = useState('')
  const [err, setErr] = useState('')

  const handle = async () => {
    try {
      await login(user, pass)
      location.reload()
    } catch { setErr('Login failed') }
  }

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="bg-oda-surface p-8 rounded-lg w-80">
        <h2 className="text-2xl font-bold text-oda-primary mb-6">OdaTrade</h2>
        <input className="w-full mb-3 p-2 bg-oda-bg rounded border border-gray-700" placeholder="Username" value={user} onChange={e => setUser(e.target.value)} />
        <input className="w-full mb-3 p-2 bg-oda-bg rounded border border-gray-700" type="password" placeholder="Password" value={pass} onChange={e => setPass(e.target.value)} />
        {err && <p className="text-oda-accent text-sm mb-2">{err}</p>}
        <button onClick={handle} className="w-full py-2 bg-oda-primary text-oda-bg rounded font-semibold">Login</button>
      </div>
    </div>
  )
}
