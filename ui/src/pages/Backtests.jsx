import { useState } from 'react'
import { api } from '../api'

export default function Backtests() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const runBacktest = async () => {
    setLoading(true)
    const r = await api('/backtest/run', { method: 'POST', body: JSON.stringify({ symbol: 'btcusdt', strategy: 'adaptive', days: 30 }) })
    setResult(r); setLoading(false)
  }

  const runWalkForward = async () => {
    setLoading(true)
    const r = await api('/backtest/walk-forward', { method: 'POST', body: JSON.stringify({ symbol: 'btcusdt', days: 30 }) })
    setResult(r); setLoading(false)
  }

  const runMonteCarlo = async () => {
    setLoading(true)
    const r = await api('/backtest/monte-carlo', { method: 'POST', body: JSON.stringify({}) })
    setResult(r); setLoading(false)
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Backtests</h2>
      <div className="flex gap-3 mb-6">
        <button onClick={runBacktest} disabled={loading} className="px-4 py-2 bg-oda-primary text-oda-bg rounded">Run Backtest</button>
        <button onClick={runWalkForward} disabled={loading} className="px-4 py-2 bg-oda-surface border border-oda-primary text-oda-primary rounded">Walk-Forward</button>
        <button onClick={runMonteCarlo} disabled={loading} className="px-4 py-2 bg-oda-surface border border-gray-600 rounded">Monte Carlo</button>
      </div>
      {loading && <p className="text-gray-400">Running...</p>}
      {result && (
        <pre className="bg-oda-surface p-4 rounded-lg text-sm overflow-auto max-h-96">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  )
}
