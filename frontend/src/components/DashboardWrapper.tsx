'use client'

import { notFound } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { FC, ReactNode, useEffect } from 'react'
import { userAuthStatus } from 'utils/constants'

const DashboardWrapper: FC<{ children: ReactNode }> = ({ children }) => {
  const { status } = useSession()

  useEffect(() => {
    if (status === userAuthStatus.LOADING) {
      return
    }
    if (status === userAuthStatus.UNAUTHENTICATED) {
      notFound()
    }
  }, [status])

  return <>{children}</>
}

export default DashboardWrapper
