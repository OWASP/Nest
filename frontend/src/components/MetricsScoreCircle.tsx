import { FC } from 'react'

const MetricsScoreCircle: FC<{ score: number }> = ({ score }) => {
  let scoreStyle = 'bg-green-400 text-green-900'
  if (score < 50) {
    scoreStyle = 'bg-red-400 text-red-900'
  } else if (score < 75) {
    scoreStyle = 'bg-yellow-400 text-yellow-900'
  }
  return (
    <div
      className={`group relative flex h-20 w-20 flex-col items-center justify-center rounded-full border-2 shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-xl ${scoreStyle}`}
    >
      <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
      <div className="relative z-10 flex flex-col items-center text-center">
        <span className="text-xs font-semibold uppercase tracking-wide opacity-90">Health</span>
        <span className="text-xl font-black leading-none">{score}</span>
        <span className="text-xs font-semibold uppercase tracking-wide opacity-90">Score</span>
      </div>
      {score < 30 && (
        <div className="animate-pulse absolute inset-0 rounded-full bg-red-400/20"></div>
      )}
    </div>
  )
}
export default MetricsScoreCircle
