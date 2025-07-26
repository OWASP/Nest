'use client'

import { useQuery } from '@apollo/client'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { notFound } from 'next/navigation'
import { FC, ReactNode, useEffect, useState } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_USER_IS_OWASP_STAFF } from 'server/queries/userQueries'
import type { User } from 'types/user'
import LoadingSpinner from 'components/LoadingSpinner'

const DashboardWrapper: FC<{ children: ReactNode }> = ({ children }) => {
  const { isSyncing, session } = useDjangoSession()
  const [user, setUser] = useState<User>()

  useEffect(() => {
    if (isSyncing) {
      return
    }
  }, [isSyncing])
  const {
    data,
    error: graphQLError,
    loading,
  } = useQuery(GET_USER_IS_OWASP_STAFF, {
    variables: {
      login: session?.user?.login,
    },
    skip: !session?.user?.login,
  })
  useEffect(() => {
    if (graphQLError) {
      handleAppError(graphQLError)
    }
    if (data) {
      setUser(data.user)
    }
  }, [data, graphQLError])

  if (loading || isSyncing) {
    return <LoadingSpinner />
  }

  if (!session?.user?.login) {
    notFound()
  }

  if (!user) {
    return <LoadingSpinner />
  }

  if (!user.isOwaspStaff) {
    notFound()
  }
  return <>{children}</>
}

export default DashboardWrapper
