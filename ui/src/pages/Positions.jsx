import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Positions() {
  const [positions, setPositions] = useState({})

  useEffect(() => { api('/positions').then(d => setPositions(d.positions || {})) }, [])

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Positions</h2>
      {Object.entries(positions).map(([botId, pos]) => (
        <div key={botId} className="bg-oda-surface p-4 rounded-lg mb-4">
          <h3 className="text-oda-primary font-semibold mb-2">Bot: {botId}</h3>
          {Object.keys(pos).length === 0 ? <p className="text-gray-500">No open positions</p> : (
            <table className="w-full text-sm">
              <thead><tr className="text-gray-400"><th className="text-left p-2">Symbol</th><th>Qty</th><th>Entry</th><th>PnL</th></tr></thead>
              <tbody>{Object.entries(pos).map(([sym, p]) => (
                <tr key={sym} className="border-t border-gray-800">
                  <td className="p-2">{sym}</td><td className="text-center">{p.qty}</td>
                  <td className="text-center">{p.entry?.toFixed?.(2) || p.avg_entry}</td>
                  <td className={`text-center ${(p.pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>{p.pnl || 0}</td>
                </tr>
              ))}</tbody>
            </table>
          )}
        </div>
      ))}
    </div>
  )
}
