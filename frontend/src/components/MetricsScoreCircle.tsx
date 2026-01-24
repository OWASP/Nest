import { Tooltip } from '@heroui/tooltip'
import { FC, MouseEvent } from 'react'

interface MetricsScoreCircleProps {
  score: number
  onClick?: (e: MouseEvent<HTMLButtonElement>) => void
  clickable?: boolean
}

const MetricsScoreCircle: FC<MetricsScoreCircleProps> = ({ score, onClick, clickable = false }) => {
  let scoreStyle = 'bg-green-400/80 text-green-900/90'
  if (score < 50) {
    scoreStyle = 'bg-red-400/80 text-red-900/90'
  } else if (score < 75) {
    scoreStyle = 'bg-yellow-400/80 text-yellow-900/90'
  }

  const baseClasses = `relative flex h-10 w-10 sm:h-14 sm:w-14 flex-col items-center justify-center rounded-full shadow-md transition-all duration-300 ${scoreStyle}`
  const groupClass = clickable ? 'group' : ''
  const clickableClasses = clickable ? 'hover:scale-105 hover:shadow-lg cursor-pointer' : ''
  const finalClasses = `${groupClass} ${baseClasses} ${clickableClasses}`

  return (
    <Tooltip content={'Current Project Health Score'} placement="top">
      {clickable ? (
        <button className={finalClasses} onClick={onClick} tabIndex={0} type="button">
          <div className="absolute inset-0 rounded-full bg-linear-to-br from-white/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
          <div className="relative z-10 flex flex-col items-center text-center">
            <span className="text-[0.375rem] font-medium tracking-wide uppercase opacity-60 sm:text-[0.5rem]">
              Health
            </span>
            <span className="text-lg leading-none font-extrabold sm:text-xl">{score}</span>
            <span className="text-[0.375rem] font-medium tracking-wide uppercase opacity-60 sm:text-[0.5rem]">
              Score
            </span>
          </div>
          {score < 30 && (
            <div className="absolute inset-0 animate-pulse rounded-full bg-red-400/20" />
          )}
        </button>
      ) : (
        <div className={finalClasses}>
          <div className="relative z-10 flex flex-col items-center text-center">
            <span className="text-[0.375rem] font-medium tracking-wide uppercase opacity-60 sm:text-[0.5rem]">
              Health
            </span>
            <span className="text-lg leading-none font-extrabold sm:text-xl">{score}</span>
            <span className="text-[0.375rem] font-medium tracking-wide uppercase opacity-60 sm:text-[0.5rem]">
              Score
            </span>
          </div>
          {score < 30 && (
            <div className="absolute inset-0 animate-pulse rounded-full bg-red-400/20" />
          )}
        </div>
      )}
    </Tooltip>
  )
}

export default MetricsScoreCircle
