'use client'

import { useQuery } from '@apollo/client'
import { notFound } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { FC, ReactNode, useEffect, useState } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_USER_IS_OWASP_STAFF } from 'server/queries/userQueries'
import type { User } from 'types/user'
import { userAuthStatus } from 'utils/constants'
import LoadingSpinner from 'components/LoadingSpinner'

const DashboardWrapper: FC<{ children: ReactNode }> = ({ children }) => {
  const { status, data: session } = useSession()
  const [user, setUser] = useState<User>()

  useEffect(() => {
    if (status === userAuthStatus.UNAUTHENTICATED) {
      notFound()
    }
  }, [status, session])

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

  if (loading || status === userAuthStatus.LOADING) {
    return <LoadingSpinner />
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
