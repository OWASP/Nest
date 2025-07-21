import { Tooltip } from '@heroui/tooltip'
import { FC } from 'react'

const MetricsScoreCircle: FC<{ score: number }> = ({ score }) => {
  // Base colours with reduced opacity so colours remain but are less contrasting
  let scoreStyle = 'bg-green-400/80 text-green-900/90'
  if (score < 50) {
    scoreStyle = 'bg-red-400/80 text-red-900/90'
  } else if (score < 75) {
    scoreStyle = 'bg-yellow-400/80 text-yellow-900/90'
  }
  return (
    <Tooltip content={'Current Project Health Score'} placement="top">
      <div
        className={`group relative flex h-14 w-14 flex-col items-center justify-center rounded-full shadow-md transition-all duration-300 hover:scale-105 hover:shadow-lg ${scoreStyle}`}
      >
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
        <div className="relative z-10 flex flex-col items-center text-center">
          <span className="text-[0.5rem] font-medium uppercase tracking-wide opacity-60">
            Health
          </span>
          <span className="text-xl font-extrabold leading-none">{score}</span>
          <span className="text-[0.5rem] font-medium uppercase tracking-wide opacity-60">
            Score
          </span>
        </div>
        {score < 30 && (
          <div className="animate-pulse absolute inset-0 rounded-full bg-red-400/20"></div>
        )}
      </div>
    </Tooltip>
  )
}
export default MetricsScoreCircle
