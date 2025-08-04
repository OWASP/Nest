'use client'

import { useDjangoSession } from 'hooks/useDjangoSession'
import { notFound } from 'next/navigation'
import { FC, ReactNode } from 'react'
import LoadingSpinner from 'components/LoadingSpinner'

const IS_OWASP_STAFF_KEY = 'is_owasp_staff'
const DashboardWrapper: FC<{ children: ReactNode }> = ({ children }) => {
  const { isSyncing } = useDjangoSession()

  if (isSyncing) {
    return <LoadingSpinner />
  }

  const isOwaspStaff = sessionStorage.getItem(IS_OWASP_STAFF_KEY) === 'true'
  if (!isOwaspStaff) {
    notFound()
  }
  return <>{children}</>
}

export default DashboardWrapper
