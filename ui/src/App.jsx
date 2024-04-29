import { Routes, Route, NavLink } from 'react-router-dom'
import Overview from './pages/Overview'
import SignalsLab from './pages/SignalsLab'
import Positions from './pages/Positions'
import Blotter from './pages/Blotter'
import Risk from './pages/Risk'
import Backtests from './pages/Backtests'
import Login from './pages/Login'

const nav = [
  { to: '/', label: 'Overview' },
  { to: '/signals', label: 'Signals Lab' },
  { to: '/positions', label: 'Positions' },
  { to: '/blotter', label: 'Blotter' },
  { to: '/risk', label: 'Risk' },
  { to: '/backtests', label: 'Backtests' },
]

export default function App() {
  const token = localStorage.getItem('odatrade_token')
  if (!token) return <Login />

  return (
    <div className="flex min-h-screen">
      <nav className="w-56 bg-oda-surface p-4 flex flex-col gap-1">
        <h1 className="text-xl font-bold text-oda-primary mb-6">OdaTrade</h1>
        {nav.map(n => (
          <NavLink key={n.to} to={n.to} className={({ isActive }) =>
            `px-3 py-2 rounded ${isActive ? 'bg-oda-primary/20 text-oda-primary' : 'text-gray-400 hover:text-white'}`}>
            {n.label}
          </NavLink>
        ))}
        <button onClick={() => { localStorage.removeItem('odatrade_token'); location.reload() }}
          className="mt-auto text-sm text-gray-500 hover:text-oda-accent">Logout</button>
      </nav>
      <main className="flex-1 p-6 overflow-auto">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/signals" element={<SignalsLab />} />
          <Route path="/positions" element={<Positions />} />
          <Route path="/blotter" element={<Blotter />} />
          <Route path="/risk" element={<Risk />} />
          <Route path="/backtests" element={<Backtests />} />
        </Routes>
      </main>
    </div>
  )
}
