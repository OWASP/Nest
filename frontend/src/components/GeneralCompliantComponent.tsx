'use client'

import { Tooltip } from '@heroui/tooltip'
import clsx from 'clsx'
import { FC } from 'react'
import type { IconType } from 'react-icons'
import { FaCertificate } from 'react-icons/fa6'
import { IconWrapper } from 'wrappers/IconWrapper'

const GeneralCompliantComponent: FC<{
  readonly compliant: boolean
  readonly icon: IconType
  readonly title: string
}> = ({ icon, compliant, title }) => {
  return (
    <Tooltip content={title} placement="top">
      <div className="group pointer-events-auto relative inline-block transition-all duration-300 ease-in-out hover:scale-105">
        <IconWrapper
          icon={FaCertificate}
          className={clsx(
            'h-14 w-14 drop-shadow-md filter transition-all group-hover:drop-shadow-lg',
            {
              'text-green-400/80': compliant,
              'text-red-400/80': !compliant,
            }
          )}
        />
        <IconWrapper
          icon={icon}
          className={clsx('absolute top-1/2 left-1/2 h-7 w-7 -translate-x-1/2 -translate-y-1/2', {
            'text-green-900/90': compliant,
            'text-red-900/90': !compliant,
          })}
        />
      </div>
    </Tooltip>
  )
}

export default GeneralCompliantComponent
