import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Risk() {
  const [risk, setRisk] = useState({})

  useEffect(() => { api('/metrics/risk').then(setRisk) }, [])

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Risk Dashboard</h2>
      {(risk.bots || []).map(b => (
        <div key={b.bot_id} className="bg-oda-surface p-4 rounded-lg mb-4">
          <div className="flex justify-between items-center">
            <h3 className="font-semibold">{b.name || b.bot_id}</h3>
            <span className={`px-2 py-1 rounded text-xs ${b.kill_switch ? 'bg-red-900 text-red-300' : 'bg-green-900 text-green-300'}`}>
              {b.kill_switch ? 'KILL SWITCH' : 'ACTIVE'}
            </span>
          </div>
          <div className="grid grid-cols-4 gap-4 mt-3 text-sm">
            {Object.entries(b.metrics || {}).map(([k, v]) => (
              <div key={k}><p className="text-gray-400">{k}</p><p className="font-bold">{v}</p></div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
