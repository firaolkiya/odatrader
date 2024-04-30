import { Routes, Route, NavLink } from 'react-router-dom'
import Overview from './pages/Overview'
import SignalsLab from './pages/SignalsLab'
import Positions from './pages/Positions'
import Blotter from './pages/Blotter'
import Risk from './pages/Risk'
import Backtests from './pages/Backtests'
import Login from './pages/Login'

const nav = [
  { to: '/', label: 'Overview', icon: '◉' },
  { to: '/signals', label: 'Signals Lab', icon: '⚡' },
  { to: '/positions', label: 'Positions', icon: '▤' },
  { to: '/blotter', label: 'Blotter', icon: '≡' },
  { to: '/risk', label: 'Risk', icon: '◆' },
  { to: '/backtests', label: 'Backtests', icon: '↺' },
]

export default function App() {
  const token = localStorage.getItem('odatrade_token') || import.meta.env.VITE_USE_MOCK === 'true'
  if (!token) return <Login />

  return (
    <div className="relative min-h-screen overflow-hidden bg-oda-bg">
      <div className="pointer-events-none absolute -left-32 top-0 h-96 w-96 rounded-full bg-oda-primary/10 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[28rem] w-[28rem] rounded-full bg-cyan-500/10 blur-3xl" />

      <div className="relative flex min-h-screen">
        <nav className="flex w-64 flex-col border-r border-white/10 bg-oda-surface/60 p-5 backdrop-blur-xl">
          <div className="mb-8">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-oda-primary to-cyan-400 text-lg font-black text-oda-bg">
                O
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">OdaTrade</h1>
                <p className="text-xs text-gray-500">Trading Console</p>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-1">
            {nav.map(n => (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                    isActive
                      ? 'bg-oda-primary/15 text-oda-primary shadow-inner shadow-oda-primary/10'
                      : 'text-gray-400 hover:bg-white/5 hover:text-white'
                  }`}
              >
                <span className="text-base opacity-80">{n.icon}</span>
                {n.label}
              </NavLink>
            ))}
          </div>

          <button
            onClick={() => {
              localStorage.removeItem('odatrade_token')
              location.reload()
            }}
            className="mt-auto rounded-xl px-3 py-2 text-left text-sm text-gray-500 transition hover:bg-white/5 hover:text-oda-accent"
          >
            Logout
          </button>
        </nav>

        <main className="flex-1 overflow-auto p-8">
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
    </div>
  )
}
