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
          'group relative flex h-10 w-10 cursor-default items-center justify-center rounded-full shadow-md transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-lg sm:h-14 sm:w-14',
          {
            'bg-green-400/80 text-green-900/90': compliant,
            'bg-red-400/80 text-red-900/90': !compliant,
          }
        )}
      >
        <IconWrapper icon={icon} className="h-5 w-5 sm:h-7 sm:w-7" />
      </div>
    </Tooltip>
  )
}

export default GeneralCompliantComponent
