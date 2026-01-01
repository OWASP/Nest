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
          'group relative flex h-14 w-14 cursor-default items-center justify-center rounded-full shadow-md transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-lg',
          {
            'bg-green-400/80 text-green-900/90': compliant,
            'bg-red-400/80 text-red-900/90': !compliant,
          }
        )}
      >
        <IconWrapper icon={icon} className="h-7 w-7" />
      </div>
    </Tooltip>
  )
}

export default GeneralCompliantComponent
