import { useEffect, useState } from 'react'
import { api, connectWS } from '../api'

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
      <h2 className="text-2xl font-bold mb-6">Orders Blotter</h2>
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-oda-surface p-4 rounded-lg">
          <h3 className="text-lg mb-3">Open Orders</h3>
          {orders.length === 0 ? <p className="text-gray-500">No open orders</p> : orders.map(o => (
            <div key={o.id} className="flex justify-between py-2 border-b border-gray-800 text-sm">
              <span>{o.symbol}</span><span className={o.side === 'buy' ? 'text-green-400' : 'text-red-400'}>{o.side}</span>
              <span>{o.qty}</span><span className="text-gray-500">{o.status}</span>
            </div>
          ))}
        </div>
        <div className="bg-oda-surface p-4 rounded-lg">
          <h3 className="text-lg mb-3">Live Trades</h3>
          {trades.length === 0 ? <p className="text-gray-500">Waiting for trade events...</p> : trades.map((t, i) => (
            <div key={i} className="flex justify-between py-2 border-b border-gray-800 text-sm">
              <span>{t.symbol || '—'}</span><span>{t.side || '—'}</span><span>{t.price || t.fill_price || '—'}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
