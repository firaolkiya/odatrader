export default function StatCard({ label, value, hint, trend, accent = 'primary' }) {
  const accents = {
    primary: 'from-oda-primary/20 to-transparent text-oda-primary',
    green: 'from-emerald-500/20 to-transparent text-emerald-400',
    red: 'from-rose-500/20 to-transparent text-rose-400',
    blue: 'from-sky-500/20 to-transparent text-sky-400',
  }
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-oda-surface/80 p-5 shadow-card backdrop-blur-sm transition hover:border-oda-primary/30">
      <div className={`absolute inset-x-0 top-0 h-20 bg-gradient-to-b ${accents[accent]}`} />
      <div className="relative">
        <p className="text-sm text-gray-400">{label}</p>
        <p className="mt-2 text-3xl font-bold tracking-tight text-white">{value}</p>
        {(hint || trend) && (
          <div className="mt-2 flex items-center gap-2 text-xs">
            {trend && (
              <span className={trend.startsWith('+') ? 'text-emerald-400' : trend.startsWith('-') ? 'text-rose-400' : 'text-gray-400'}>
                {trend}
              </span>
            )}
            {hint && <span className="text-gray-500">{hint}</span>}
          </div>
        )}
      </div>
    </div>
  )
}
