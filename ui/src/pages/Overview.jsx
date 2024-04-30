import { useEffect, useState } from 'react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api, connectWS } from '../api'
import PageHeader from '../components/PageHeader'
import Panel from '../components/Panel'
import StatCard from '../components/StatCard'
import Badge from '../components/Badge'

const fmt = (n) => n?.toLocaleString?.(undefined, { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 })

export default function Overview() {
  const [status, setStatus] = useState({})
  const [pnl, setPnl] = useState({})
  const [equity, setEquity] = useState([])

  useEffect(() => {
    api('/status').then(setStatus)
    api('/metrics/pnl?window=MTD').then(setPnl)
    const ws = connectWS('/ws/realtime', (data) => {
      if (data.type === 'pnl_update') {
        setEquity(prev => [...prev.slice(-29), {
          t: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          v: data.cumulative || 0,
        }])
      }
    })
    return () => ws.close()
  }, [])

  const liveEquity = equity.length ? equity[equity.length - 1].v : null
  const mtdPct = ((pnl.mtd_return_pct || 0) * 100).toFixed(1)
  const dailyStr = pnl.daily_pnl >= 0 ? `+$${pnl.daily_pnl?.toFixed(2)} today` : `-$${Math.abs(pnl.daily_pnl || 0).toFixed(2)} today`

  return (
    <div>
      <PageHeader
        title="Overview"
        subtitle="Portfolio health, infrastructure status, and equity curve."
        actions={<Badge tone="success">3 bots active</Badge>}
      />

      <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Portfolio Value" value={liveEquity != null ? fmt(liveEquity) : '—'} trend={mtdPct !== '0.0' ? `+${mtdPct}%` : undefined} hint="MTD" accent="primary" />
        <StatCard label="Realized PnL" value={fmt(pnl.realized || 0)} trend={dailyStr} accent="green" />
        <StatCard label="Win Rate" value={`${((pnl.win_rate || 0) * 100).toFixed(1)}%`} hint={`${pnl.trades || 0} trades`} accent="blue" />
        <StatCard label="Sharpe (30d)" value={(pnl.sharpe || 0).toFixed(2)} hint={`Max DD ${((pnl.max_drawdown || 0) * 100).toFixed(1)}%`} accent="primary" />
      </div>

      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          ['Running Bots', `${status.running_bots || 0} / ${status.total_bots || 0}`],
          ['Redis', status.redis ? 'Connected' : 'Offline'],
          ['Postgres', status.postgres ? 'Connected' : 'Offline'],
          ['Uptime', `${status.uptime_hours || 0}h`],
        ].map(([label, val]) => (
          <Panel key={label} className="p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
            <p className="mt-1 text-lg font-semibold text-white">{val}</p>
          </Panel>
        ))}
      </div>

      <Panel className="p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white">Equity Curve</h3>
            <p className="text-sm text-gray-500">Month-to-date account balance</p>
          </div>
          <Badge tone="info">MTD</Badge>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={equity}>
              <defs>
                <linearGradient id="eqFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00d4aa" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#00d4aa" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#ffffff08" vertical={false} />
              <XAxis dataKey="t" tick={{ fill: '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} width={70} domain={['auto', 'auto']} />
              <Tooltip
                contentStyle={{ background: '#1a1d24', border: '1px solid #ffffff15', borderRadius: 12 }}
                formatter={(v) => [fmt(v), 'Equity']}
              />
              <Area type="monotone" dataKey="v" stroke="#00d4aa" strokeWidth={2.5} fill="url(#eqFill)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Panel>
    </div>
  )
}
