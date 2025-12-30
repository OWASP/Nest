'use client'

import { Tooltip } from '@heroui/tooltip'
import clsx from 'clsx'
import { FC } from 'react'
import type { IconType } from 'react-icons'
import { IconWrapper } from 'wrappers/IconWrapper'

const GeneralCompliantComponent: FC<{
  readonly compliant: boolean
  readonly icon: IconType
  readonly title: string
}> = ({ icon, compliant, title }) => {
  return (
    <Tooltip content={title} placement="top">
      <div
        className={clsx(
          'relative flex h-14 w-14 items-center justify-center rounded-full shadow-md transition-all duration-300 ease-in-out group hover:scale-105 hover:shadow-lg cursor-default',
          {

            'bg-green-400/80 text-green-900/90': compliant,
            'bg-red-400/80 text-red-900/90': !compliant,
          }
        )}
      >
        <IconWrapper
          icon={icon}
          className="h-7 w-7" 
        />
      </div>
    </Tooltip>
  )
}

export default GeneralCompliantComponent
