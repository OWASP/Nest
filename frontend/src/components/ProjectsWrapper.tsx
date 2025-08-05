'use client'
import { Button } from '@heroui/button'
import { useDjangoSession } from 'hooks/useDjangoSession'
import Link from 'next/link'
import { useSelectedLayoutSegment } from 'next/navigation'
import { FC, ReactNode } from 'react'
import LoadingSpinner from 'components/LoadingSpinner'

const ProjectsWrapper: FC<{ children: ReactNode }> = ({ children }) => {
  const segment = useSelectedLayoutSegment()
  const { isSyncing, session } = useDjangoSession()
  const isOwaspStaff = session?.user?.isOwaspStaff
  if (isSyncing) {
    return <LoadingSpinner />
  }
  if (segment) {
    return <>{children}</>
  }

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
