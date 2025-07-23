'use client'
import { useSelectedLayoutSegment } from 'next/navigation'
import { FC } from 'react'

import AccessProjectDashboardButton from 'components/AccessProjectDashboardButton'

const AccessProjectDashboardButtonWrapper: FC = () => {
  const segment = useSelectedLayoutSegment()

  if (segment) {
    return <></>
  }

  return <AccessProjectDashboardButton />
}

export default AccessProjectDashboardButtonWrapper
