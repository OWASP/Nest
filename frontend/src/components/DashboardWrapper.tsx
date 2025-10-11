'use client'

import { useDjangoSession } from 'hooks/useDjangoSession'
import { notFound } from 'next/navigation'
import { FC, ReactNode } from 'react'
import LoadingSpinner from 'components/LoadingSpinner'

const DashboardWrapper: FC<{ children: ReactNode }> = ({ children }) => {
  const { isSyncing, session } = useDjangoSession()

  if (isSyncing) {
    return <LoadingSpinner />
  }

  const isOwaspStaff = session?.user?.isOwaspStaff
  if (!isOwaspStaff) {
    notFound()
  }
  return <>{children}</>
}

export default DashboardWrapper
