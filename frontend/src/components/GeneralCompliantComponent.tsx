'use client'

import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import clsx from 'clsx'
import { FC } from 'react'
import SecondaryCard from 'components/SecondaryCard'

const GeneralCompliantComponent: FC<{
  readonly icon: IconProp
  readonly compliant: boolean
}> = ({ icon, compliant }) => {
  const greenClass = 'bg-green-100 dark:bg-green-700 hover:bg-green-200 dark:hover:bg-green-600'
  const redClass = 'bg-red-100 dark:bg-red-700 hover:bg-red-600 dark:hover:bg-red-600'

  return (
    <SecondaryCard
      className={clsx('pointer-events-auto items-center justify-center text-center font-light', {
        [greenClass]: compliant,
        [redClass]: !compliant,
      })}
    >
      <FontAwesomeIcon icon={icon} className="text-4xl" />
    </SecondaryCard>
  )
}

export default GeneralCompliantComponent
