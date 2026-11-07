'use client'

import { useDjangoSession } from 'hooks/useDjangoSession'
import { notFound } from 'next/navigation'
import { FC, ReactNode } from 'react'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import LoadingSpinner from 'components/LoadingSpinner'

const DashboardWrapper: FC<{ children: ReactNode }> = ({ children }) => {
  const { isSyncing, session } = useDjangoSession()

  if (isSyncing) {
    return <LoadingSpinner />
  }

  if (!session) {
    notFound()
  }

  const isOwaspStaff = session?.user?.isOwaspStaff
  if (!isOwaspStaff) {
    return <AccessDeniedDisplay />
  }

  return <>{children}</>
}

export default DashboardWrapper
