'use client'
import { Button } from '@heroui/button'
import { useDjangoSession } from 'hooks/useDjangoSession'
import Link from 'next/link'
import { useSelectedLayoutSegment } from 'next/navigation'
import { FC, ReactNode } from 'react'
import LoadingSpinner from 'components/LoadingSpinner'

const IS_OWASP_STAFF_KEY = 'is_owasp_staff'

const ProjectsWrapper: FC<{ children: ReactNode }> = ({ children }) => {
  const segment = useSelectedLayoutSegment()
  const { isSyncing } = useDjangoSession()
  if (isSyncing) {
    return <LoadingSpinner />
  }
  if (segment) {
    return <>{children}</>
  }

  const isOwaspStaff = sessionStorage.getItem(IS_OWASP_STAFF_KEY) === 'true'
  if (!isOwaspStaff) {
    return <>{children}</>
  }

  return (
    <div className="flex flex-col items-center justify-center">
      <Link href="/projects/dashboard">
        <Button color="secondary" className="shadow-md hover:bg-gray-200 dark:hover:bg-gray-700">
          Go To Dashboard
        </Button>
      </Link>
      {children}
    </div>
  )
}

export default ProjectsWrapper
