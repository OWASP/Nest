'use client'

import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { faCertificate } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import clsx from 'clsx'
import { FC } from 'react'

const GeneralCompliantComponent: FC<{
  readonly compliant: boolean
  readonly icon: IconProp
  readonly title: string
}> = ({ icon, compliant, title }) => {
  return (
    <Tooltip content={title} placement="top">
      <div className="pointer-events-auto relative inline-block transition-all duration-300 ease-in-out hover:scale-105">
        <FontAwesomeIcon
          icon={faCertificate}
          className={clsx('h-20 w-20', {
            'text-green-400': compliant,
            'text-red-400': !compliant,
          })}
        />
        <FontAwesomeIcon
          icon={icon}
          className={clsx('absolute left-1/2 top-1/2 h-10 w-10 -translate-x-1/2 -translate-y-1/2', {
            'text-green-900': compliant,
            'text-red-900': !compliant,
          })}
        />
      </div>
    </Tooltip>
  )
}

export default GeneralCompliantComponent
