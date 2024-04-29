import { useEffect, useState } from 'react'
import { api } from '../api'

export default function SignalsLab() {
  const [symbol, setSymbol] = useState('btcusdt')
  const [snap, setSnap] = useState(null)

  const evaluate = () => api(`/signals/evaluate/${symbol}`).then(setSnap)
  useEffect(() => { evaluate() }, [symbol])

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Signals Lab</h2>
      <select className="bg-oda-surface p-2 rounded mb-4" value={symbol} onChange={e => setSymbol(e.target.value)}>
        {['btcusdt', 'ethusdt', 'AAPL', 'TSLA', 'EURUSD'].map(s => <option key={s} value={s}>{s}</option>)}
      </select>
      <button onClick={evaluate} className="ml-2 px-4 py-2 bg-oda-primary text-oda-bg rounded">Evaluate</button>

      {snap && !snap.error && (
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-oda-surface p-4 rounded-lg">
            <p className="text-gray-400">Regime</p>
            <div className="mt-2 h-4 bg-oda-bg rounded-full overflow-hidden">
              <div className="h-full bg-oda-primary rounded-full" style={{ width: `${(snap.regime || 0) * 100}%` }} />
            </div>
            <p className="mt-1 text-sm">{(snap.regime * 100).toFixed(0)}% — {snap.regime < 0.3 ? 'Calm' : snap.regime < 0.6 ? 'Moderate' : 'Volatile'}</p>
          </div>
          <div className="bg-oda-surface p-4 rounded-lg">
            <p className="text-gray-400">Bull Share</p>
            <p className="text-3xl font-bold text-green-400">{(snap.bull_share * 100).toFixed(1)}%</p>
            <p className="text-sm text-gray-500">Entry threshold: {(snap.entry_threshold * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-oda-surface p-4 rounded-lg">
            <p className="text-gray-400">Action</p>
            <p className={`text-3xl font-bold ${snap.action === 'BUY' ? 'text-green-400' : snap.action === 'SELL' ? 'text-red-400' : 'text-gray-400'}`}>{snap.action}</p>
            <p className="text-sm text-gray-500">{snap.reason}</p>
          </div>
        </div>
      )}

      {snap?.votes && (
        <div className="mt-6 bg-oda-surface p-4 rounded-lg">
          <h3 className="text-lg mb-3">Votes Heatmap</h3>
          <div className="grid grid-cols-4 gap-2">
            {snap.votes.map(v => (
              <div key={v.name} className={`p-3 rounded text-center ${v.value === 1 ? 'bg-green-900/40' : v.value === -1 ? 'bg-red-900/40' : 'bg-gray-800'}`}>
                <p className="font-semibold">{v.name}</p>
                <p className="text-sm">{v.value > 0 ? 'BULL' : v.value < 0 ? 'BEAR' : 'NEUTRAL'}</p>
                <p className="text-xs text-gray-500">w={v.weight}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
