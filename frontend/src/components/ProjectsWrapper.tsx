'use client'
import { useQuery } from '@apollo/client'
import { Button } from '@heroui/button'
import Link from 'next/link'
import { useSelectedLayoutSegment } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { FC, ReactNode, useEffect, useState } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_USER_IS_OWASP_STAFF } from 'server/queries/userQueries'
import type { User } from 'types/user'
import { userAuthStatus } from 'utils/constants'
import LoadingSpinner from 'components/LoadingSpinner'

const ProjectsWrapper: FC<{ children: ReactNode }> = ({ children }) => {
  const segment = useSelectedLayoutSegment()
  const [user, setUser] = useState<User>()
  const { data: session, status } = useSession()
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
  if (status === userAuthStatus.UNAUTHENTICATED) {
    return <>{children}</>
  }

  if (!user) {
    return <LoadingSpinner />
  }

  if (!user.isOwaspStaff) {
    return <>{children}</>
  }

  if (segment == 'dashboard' || segment == 'metrics') {
    return <>{children}</>
  }

  return (
    <div className="flex flex-col items-center justify-center">
      <Link href="/projects/dashboard">
        <Button color="secondary">Go To Dashboard</Button>
      </Link>
      {children}
    </div>
  )
}

export default ProjectsWrapper
