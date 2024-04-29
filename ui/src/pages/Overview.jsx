import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { api, connectWS } from '../api'

export default function Overview() {
  const [status, setStatus] = useState({})
  const [pnl, setPnl] = useState({})
  const [equity, setEquity] = useState([])

  useEffect(() => {
    api('/status').then(setStatus)
    api('/metrics/pnl?window=MTD').then(setPnl)
    const ws = connectWS('/ws/realtime', (data) => {
      if (data.type === 'pnl_update') setEquity(prev => [...prev.slice(-50), { t: Date.now(), v: data.cumulative || 0 }])
    })
    return () => ws.close()
  }, [])

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Overview</h2>
      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          ['Running Bots', status.running_bots || 0],
          ['Total Bots', status.total_bots || 0],
          ['Redis', status.redis ? 'Connected' : 'Offline'],
          ['Postgres', status.postgres ? 'Connected' : 'Offline'],
        ].map(([label, val]) => (
          <div key={label} className="bg-oda-surface p-4 rounded-lg">
            <p className="text-gray-400 text-sm">{label}</p>
            <p className="text-2xl font-bold text-oda-primary">{val}</p>
          </div>
        ))}
      </div>
      <div className="bg-oda-surface p-4 rounded-lg h-64">
        <h3 className="text-lg mb-2">Equity Curve</h3>
        <ResponsiveContainer width="100%" height="90%">
          <LineChart data={equity.length ? equity : [{ t: 0, v: 5000 }]}>
            <XAxis dataKey="t" hide /><YAxis domain={['auto', 'auto']} /><Tooltip />
            <Line type="monotone" dataKey="v" stroke="#00d4aa" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
