import { useEffect, useState } from 'react'
import { api } from '../api'
import PageHeader from '../components/PageHeader'
import Panel from '../components/Panel'
import Badge from '../components/Badge'

const fmt = (n) => n?.toLocaleString?.(undefined, { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 })
const fmtPrice = (sym, n) => {
  if (sym === 'EURUSD') return n?.toFixed?.(4) ?? n
  if (sym === 'BTCUSDT') return n?.toLocaleString?.(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return n?.toFixed?.(2) ?? n
}

export default function Positions() {
  const [positions, setPositions] = useState({})

  useEffect(() => { api('/positions').then(d => setPositions(d.positions || {})) }, [])

  const totalPnl = Object.values(positions).flatMap(p => Object.values(p)).reduce((s, p) => s + (p.pnl || 0), 0)

  return (
    <div>
      <PageHeader
        title="Positions"
        subtitle="Open exposure across all bots with entry, mark, and unrealized PnL."
        actions={<Badge tone={totalPnl >= 0 ? 'success' : 'danger'}>Total PnL {fmt(totalPnl)}</Badge>}
      />

      <div className="space-y-5">
        {Object.entries(positions).map(([botId, pos]) => (
          <Panel key={botId} className="overflow-hidden">
            <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
              <div>
                <h3 className="font-semibold text-white">{botId.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</h3>
                <p className="text-xs text-gray-500">{Object.keys(pos).length} open symbols</p>
              </div>
              <Badge tone={Object.keys(pos).length ? 'info' : 'neutral'}>
                {Object.keys(pos).length ? 'Active' : 'Flat'}
              </Badge>
            </div>

            {Object.keys(pos).length === 0 ? (
              <p className="px-5 py-8 text-center text-gray-500">No open positions</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs uppercase tracking-wide text-gray-500">
                      <th className="px-5 py-3">Symbol</th>
                      <th className="px-5 py-3">Side</th>
                      <th className="px-5 py-3">Qty</th>
                      <th className="px-5 py-3">Entry</th>
                      <th className="px-5 py-3">Mark</th>
                      <th className="px-5 py-3">Notional</th>
                      <th className="px-5 py-3 text-right">PnL</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(pos).map(([sym, p]) => (
                      <tr key={sym} className="border-t border-white/5 hover:bg-white/[0.02]">
                        <td className="px-5 py-3 font-medium text-white">{sym}</td>
                        <td className="px-5 py-3">
                          <Badge tone={p.side === 'short' ? 'danger' : 'success'}>{p.side || 'long'}</Badge>
                        </td>
                        <td className="px-5 py-3 text-gray-300">{p.qty}</td>
                        <td className="px-5 py-3 text-gray-300">{fmtPrice(sym, p.entry ?? p.avg_entry)}</td>
                        <td className="px-5 py-3 text-oda-primary">{fmtPrice(sym, p.mark ?? p.entry)}</td>
                        <td className="px-5 py-3 text-gray-300">{fmt(p.notional)}</td>
                        <td className={`px-5 py-3 text-right font-semibold ${(p.pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {fmt(p.pnl || 0)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Panel>
        ))}
      </div>
    </div>
  )
}
