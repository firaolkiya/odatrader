import { useEffect, useState } from 'react'
import { api, connectWS } from '../api'
import PageHeader from '../components/PageHeader'
import Panel from '../components/Panel'
import Badge from '../components/Badge'

export default function Blotter() {
  const [orders, setOrders] = useState([])
  const [trades, setTrades] = useState([])

  useEffect(() => {
    api('/orders').then(d => setOrders(d.open || []))
    const ws = connectWS('/ws/trades/btcusdt', (data) => {
      if (data.type === 'trade') setTrades(prev => [data, ...prev].slice(0, 50))
    })
    return () => ws.close()
  }, [])

  return (
    <div>
      <PageHeader
        title="Orders Blotter"
        subtitle="Working orders and recent fills."
        actions={<Badge tone="info">{orders.length} open orders</Badge>}
      />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <Panel className="overflow-hidden">
          <div className="border-b border-white/10 px-5 py-4">
            <h3 className="text-lg font-semibold text-white">Open Orders</h3>
          </div>
          <div className="divide-y divide-white/5">
            {orders.length === 0 ? (
              <p className="px-5 py-10 text-center text-gray-500">No open orders</p>
            ) : orders.map(o => (
              <div key={o.id} className="flex flex-wrap items-center justify-between gap-3 px-5 py-4 text-sm hover:bg-white/[0.02]">
                <div>
                  <p className="font-medium text-white">{o.symbol}</p>
                  <p className="text-xs text-gray-500">{o.id} · {o.type}</p>
                </div>
                <Badge tone={o.side === 'buy' ? 'success' : 'danger'}>{o.side}</Badge>
                <span className="text-gray-300">{o.qty} @ {o.price}</span>
                <Badge tone={o.status === 'partial' ? 'warn' : 'neutral'}>{o.status}</Badge>
              </div>
            ))}
          </div>
        </Panel>

        <Panel className="overflow-hidden">
          <div className="border-b border-white/10 px-5 py-4">
            <h3 className="text-lg font-semibold text-white">Live Trades</h3>
          </div>
          <div className="max-h-[32rem] divide-y divide-white/5 overflow-y-auto">
            {trades.length === 0 ? (
              <p className="px-5 py-10 text-center text-gray-500">Waiting for trade events...</p>
            ) : trades.map((t, i) => (
              <div key={i} className="flex items-center justify-between px-5 py-3 text-sm hover:bg-white/[0.02]">
                <div>
                  <p className="font-medium text-white">{t.symbol || '—'}</p>
                  <p className="text-xs text-gray-500">{t.time || new Date().toLocaleTimeString()}</p>
                </div>
                <Badge tone={t.side === 'buy' ? 'success' : 'danger'}>{t.side || '—'}</Badge>
                <span className="font-mono text-gray-300">{t.price || t.fill_price || '—'}</span>
                <span className="text-gray-500">{t.qty || ''}</span>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  )
}
