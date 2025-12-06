'use client'

import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { faCertificate } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import clsx from 'clsx'
import { FC } from 'react'

const BADGE_SIZE = 16

const GeneralCompliantComponent: FC<{
  readonly compliant: boolean
  readonly icon: IconProp
  readonly title: string
  readonly size?: 'sm' | 'md'
}> = ({ icon, compliant, title, size = 'md' }) => {
  const isSmall = size === 'sm'

  return (
    <Tooltip content={title} placement="top">
      <div
        className={clsx(
          'group pointer-events-auto relative inline-flex items-center justify-center',
          !isSmall && 'transition-all duration-300 ease-in-out hover:scale-105'
        )}
        style={isSmall ? { width: BADGE_SIZE, height: BADGE_SIZE } : undefined}
      >
        <FontAwesomeIcon
          icon={faCertificate}
          className={clsx('drop-shadow-md filter transition-all group-hover:drop-shadow-lg', {
            'h-14 w-14': !isSmall,
            'text-green-400/80': compliant,
            'text-red-400/80': !compliant,
          })}
          style={isSmall ? { width: BADGE_SIZE, height: BADGE_SIZE } : undefined}
        />
        <FontAwesomeIcon
          icon={icon}
          className={clsx('absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2', {
            'h-7 w-7': !isSmall,
            'text-green-900/90': compliant,
            'text-red-900/90': !compliant,
          })}
          style={isSmall ? { width: BADGE_SIZE * 0.5, height: BADGE_SIZE * 0.5 } : undefined}
        />
      </div>
    </Tooltip>
  )
}

export default GeneralCompliantComponent
