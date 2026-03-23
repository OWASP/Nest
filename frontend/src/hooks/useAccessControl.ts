import { useEffect, useState } from 'react'

interface AccessData {
  getProgram?: {
    admins?: Array<{ login: string }> | null
  } | null
  getModule?: {
    mentors?: Array<{ login: string }> | null
  } | null
}

export const useAccessControl = (
  accessData: AccessData | undefined,
  sessionStatus: string,
  currentUserLogin: string | undefined,
  isLoading: boolean
): boolean | undefined => {
  const [hasAccess, setHasAccess] = useState<boolean | undefined>(undefined)

  useEffect(() => {
    if (sessionStatus === 'loading' || isLoading) {
      setHasAccess(undefined)
      return
    }

    if (sessionStatus === 'unauthenticated') {
      setHasAccess(false)
      return
    }

    if (!accessData?.getProgram?.admins || !accessData?.getModule?.mentors) {
      setHasAccess(undefined)
      return
    }

    const isAdmin = (accessData.getProgram?.admins || []).some(
      (admin: { login: string }) => admin.login === currentUserLogin
    )

    const isMentor = (accessData.getModule?.mentors || []).some(
      (mentor: { login: string }) => mentor.login === currentUserLogin
    )

    setHasAccess(isAdmin || isMentor)
  }, [sessionStatus, currentUserLogin, isLoading, accessData])

  return hasAccess
}
