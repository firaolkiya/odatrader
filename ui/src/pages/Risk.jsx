import { useEffect, useState } from 'react'
import { api } from '../api'
import PageHeader from '../components/PageHeader'
import Panel from '../components/Panel'
import Badge from '../components/Badge'

export default function Risk() {
  const [risk, setRisk] = useState({})

  useEffect(() => { api('/metrics/risk').then(setRisk) }, [])

  return (
    <div>
      <PageHeader
        title="Risk Dashboard"
        subtitle="Per-bot exposure, VaR limits, and kill-switch status."
      />

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {(risk.bots || []).map(b => (
          <Panel key={b.bot_id} className="p-5">
            <div className="mb-4 flex items-start justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-white">{b.name || b.bot_id}</h3>
                <p className="text-xs text-gray-500">{b.bot_id}</p>
              </div>
              <Badge tone={b.kill_switch ? 'danger' : 'success'}>
                {b.kill_switch ? 'Kill switch' : 'Active'}
              </Badge>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(b.metrics || {}).map(([k, v]) => (
                <div key={k} className="rounded-xl border border-white/10 bg-oda-bg/50 p-3">
                  <p className="text-xs uppercase tracking-wide text-gray-500">{k.replace(/_/g, ' ')}</p>
                  <p className="mt-1 text-lg font-bold text-white">{v}</p>
                </div>
              ))}
            </div>
          </Panel>
        ))}
      </div>
    </div>
  )
}
