export default function Panel({ children, className = '' }) {
  return (
    <div className={`rounded-2xl border border-white/10 bg-oda-surface/80 backdrop-blur-sm shadow-card ${className}`}>
      {children}
    </div>
  )
}
