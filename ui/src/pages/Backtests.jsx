import { useState } from 'react'
import { api } from '../api'
import PageHeader from '../components/PageHeader'
import Panel from '../components/Panel'
import Badge from '../components/Badge'

const resultCards = {
  backtest: [
    ['Total Return', r => `${(r.total_return * 100).toFixed(2)}%`],
    ['Sharpe', r => r.sharpe?.toFixed(2)],
    ['Max Drawdown', r => `${(r.max_drawdown * 100).toFixed(2)}%`],
    ['Win Rate', r => `${(r.win_rate * 100).toFixed(1)}%`],
    ['Trades', r => r.trades],
    ['Final Equity', r => `$${r.equity_final?.toLocaleString()}`],
  ],
  walkForward: [
    ['Avg Return', r => `${(r.avg_return * 100).toFixed(2)}%`],
    ['Best Fold', r => `${(r.best_fold * 100).toFixed(2)}%`],
    ['Worst Fold', r => `${(r.worst_fold * 100).toFixed(2)}%`],
    ['Stability', r => `${(r.stability_score * 100).toFixed(0)}%`],
  ],
  monteCarlo: [
    ['Median Return', r => `${(r.median_return * 100).toFixed(2)}%`],
    ['P5 Return', r => `${(r.p5_return * 100).toFixed(2)}%`],
    ['P95 Return', r => `${(r.p95_return * 100).toFixed(2)}%`],
    ['Ruin Prob.', r => `${(r.ruin_probability * 100).toFixed(2)}%`],
  ],
}

export default function Backtests() {
  const [result, setResult] = useState(null)
  const [resultType, setResultType] = useState(null)
  const [loading, setLoading] = useState(false)

  const run = async (type, fn) => {
    setLoading(true)
    setResultType(type)
    const r = await fn()
    setResult(r)
    setLoading(false)
  }

  const cards = resultType ? resultCards[resultType] : null

  return (
    <div>
      <PageHeader
        title="Backtests"
        subtitle="Run strategy simulations and review performance metrics."
      />

      <div className="mb-8 flex flex-wrap gap-3">
        <button
          onClick={() => run('backtest', () => api('/backtest/run', { method: 'POST', body: JSON.stringify({ symbol: 'btcusdt', strategy: 'adaptive', days: 30 }) }))}
          disabled={loading}
          className="rounded-xl bg-gradient-to-r from-oda-primary to-cyan-400 px-5 py-2.5 text-sm font-semibold text-oda-bg disabled:opacity-50"
        >
          Run Backtest
        </button>
        <button
          onClick={() => run('walkForward', () => api('/backtest/walk-forward', { method: 'POST', body: JSON.stringify({ symbol: 'btcusdt', days: 30 }) }))}
          disabled={loading}
          className="rounded-xl border border-oda-primary/40 bg-oda-primary/10 px-5 py-2.5 text-sm font-semibold text-oda-primary disabled:opacity-50"
        >
          Walk-Forward
        </button>
        <button
          onClick={() => run('monteCarlo', () => api('/backtest/monte-carlo', { method: 'POST', body: JSON.stringify({}) }))}
          disabled={loading}
          className="rounded-xl border border-white/10 bg-white/5 px-5 py-2.5 text-sm font-semibold text-gray-200 disabled:opacity-50"
        >
          Monte Carlo
        </button>
      </div>

      {loading && (
        <Panel className="p-8 text-center text-gray-400">
          <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-oda-primary border-t-transparent" />
          Running simulation...
        </Panel>
      )}

      {result && cards && !loading && (
        <>
          <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
            {cards.map(([label, fmt]) => (
              <Panel key={label} className="p-4 text-center">
                <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
                <p className="mt-2 text-xl font-bold text-white">{fmt(result)}</p>
              </Panel>
            ))}
          </div>
          <Panel className="p-5">
            <div className="mb-3 flex items-center gap-2">
              <h3 className="font-semibold text-white">Raw output</h3>
              <Badge tone="neutral">JSON</Badge>
            </div>
            <pre className="max-h-64 overflow-auto rounded-xl bg-oda-bg p-4 text-xs text-gray-300">{JSON.stringify(result, null, 2)}</pre>
          </Panel>
        </>
      )}
    </div>
  )
}
