export default function Badge({ children, tone = 'neutral' }) {
  const tones = {
    neutral: 'bg-white/5 text-gray-300 ring-white/10',
    success: 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/30',
    danger: 'bg-rose-500/15 text-rose-300 ring-rose-500/30',
    warn: 'bg-amber-500/15 text-amber-300 ring-amber-500/30',
    info: 'bg-cyan-500/15 text-cyan-300 ring-cyan-500/30',
  }
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ${tones[tone]}`}>
      {children}
    </span>
  )
}
