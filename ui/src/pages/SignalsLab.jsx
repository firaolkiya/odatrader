import { useEffect, useState } from 'react'
import { api } from '../api'
import PageHeader from '../components/PageHeader'
import Panel from '../components/Panel'
import Badge from '../components/Badge'

const symbols = ['btcusdt', 'ethusdt', 'AAPL', 'TSLA', 'EURUSD']

export default function SignalsLab() {
  const [symbol, setSymbol] = useState('btcusdt')
  const [snap, setSnap] = useState(null)

  const evaluate = () => api(`/signals/evaluate/${symbol}`).then(setSnap)
  useEffect(() => { evaluate() }, [symbol])

  const actionTone = snap?.action === 'BUY' ? 'success' : snap?.action === 'SELL' ? 'danger' : 'neutral'

  return (
    <div>
      <PageHeader
        title="Signals Lab"
        subtitle="Multi-strategy voting engine with regime detection and entry thresholds."
        actions={
          <>
            <select
              className="rounded-xl border border-white/10 bg-oda-bg px-4 py-2 text-sm text-white outline-none ring-oda-primary/40 focus:ring-2"
              value={symbol}
              onChange={e => setSymbol(e.target.value)}
            >
              {symbols.map(s => <option key={s} value={s}>{s.toUpperCase()}</option>)}
            </select>
            <button
              onClick={evaluate}
              className="rounded-xl bg-gradient-to-r from-oda-primary to-cyan-400 px-5 py-2 text-sm font-semibold text-oda-bg shadow-lg shadow-oda-primary/20"
            >
              Re-evaluate
            </button>
          </>
        }
      />

      {snap && !snap.error && (
        <>
          <div className="mb-8 grid grid-cols-1 gap-4 lg:grid-cols-3">
            <Panel className="p-5">
              <p className="text-sm text-gray-400">Market Regime</p>
              <div className="mt-4 h-3 overflow-hidden rounded-full bg-oda-bg">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-amber-400 to-rose-400 transition-all"
                  style={{ width: `${(snap.regime || 0) * 100}%` }}
                />
              </div>
              <p className="mt-3 text-2xl font-bold text-white">{(snap.regime * 100).toFixed(0)}%</p>
              <p className="text-sm text-gray-500">
                {snap.regime < 0.3 ? 'Calm — trend-friendly' : snap.regime < 0.6 ? 'Moderate volatility' : 'High volatility — reduce size'}
              </p>
            </Panel>

            <Panel className="p-5">
              <p className="text-sm text-gray-400">Bull Share</p>
              <p className="mt-3 text-4xl font-bold text-emerald-400">{(snap.bull_share * 100).toFixed(1)}%</p>
              <p className="mt-2 text-sm text-gray-500">Entry threshold: {(snap.entry_threshold * 100).toFixed(1)}%</p>
              <div className="mt-4 h-2 overflow-hidden rounded-full bg-oda-bg">
                <div className="h-full bg-emerald-500/70" style={{ width: `${snap.bull_share * 100}%` }} />
              </div>
            </Panel>

            <Panel className="p-5">
              <p className="text-sm text-gray-400">Recommended Action</p>
              <div className="mt-3 flex items-center gap-3">
                <p className={`text-4xl font-black ${snap.action === 'BUY' ? 'text-emerald-400' : snap.action === 'SELL' ? 'text-rose-400' : 'text-gray-300'}`}>
                  {snap.action}
                </p>
                <Badge tone={actionTone}>{symbol.toUpperCase()}</Badge>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-gray-400">{snap.reason}</p>
            </Panel>
          </div>

          {snap.votes && (
            <Panel className="p-6">
              <h3 className="mb-4 text-lg font-semibold text-white">Strategy Votes</h3>
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                {snap.votes.map(v => (
                  <div
                    key={v.name}
                    className={`rounded-xl border p-4 text-center transition ${
                      v.value === 1
                        ? 'border-emerald-500/30 bg-emerald-500/10'
                        : v.value === -1
                          ? 'border-rose-500/30 bg-rose-500/10'
                          : 'border-white/10 bg-white/5'
                    }`}
                  >
                    <p className="font-semibold text-white">{v.name}</p>
                    <p className="mt-1 text-sm font-medium">
                      {v.value > 0 ? 'BULL' : v.value < 0 ? 'BEAR' : 'NEUTRAL'}
                    </p>
                    <p className="mt-2 text-xs text-gray-500">weight {(v.weight * 100).toFixed(0)}%</p>
                  </div>
                ))}
              </div>
            </Panel>
          )}
        </>
      )}
    </div>
  )
}
