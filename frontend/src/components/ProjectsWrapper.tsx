'use client'
import { useSession } from 'next-auth/react'
import { FC, ReactNode } from 'react'
import { userAuthStatus } from 'utils/constants'
import { IS_GITHUB_AUTH_ENABLED } from 'utils/credentials'
import AccessProjectDashboardButtonWrapper from 'components/AccessProjectDashboardButtonWrapper'
import LoadingSpinner from 'components/LoadingSpinner'

const ProjectsWrapper: FC<{ children: ReactNode }> = ({ children }) => {
  const { status } = useSession()

  if (!IS_GITHUB_AUTH_ENABLED) {
    return <>{children}</>
  }
  if (status === userAuthStatus.LOADING) {
    return <LoadingSpinner />
  }

  return (
    <div className="flex flex-col justify-center">
      <AccessProjectDashboardButtonWrapper />
      {children}
    </div>
  )
}

export default ProjectsWrapper
