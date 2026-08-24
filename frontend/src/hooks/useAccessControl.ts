import { useEffect, useState } from 'react'

interface AccessData {
  getProgram?: {
    admins?: Array<{ login: string }> | null
  } | null
  getModule?: {
    mentors?: Array<{ login: string }> | null
  } | null
  /** Staff-only queries under `/my/mentorship/` */
  managementProgram?: {
    admins?: Array<{ login: string }> | null
  } | null
  managementModule?: {
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

    const program = accessData?.managementProgram ?? accessData?.getProgram
    const moduleNode = accessData?.managementModule ?? accessData?.getModule

    const hasProgram = Boolean(program)
    const hasModule = Boolean(moduleNode)

    if (!hasProgram && !hasModule) {
      setHasAccess(false)
      return
    }

    const isAdmin =
      hasProgram &&
      (program?.admins || []).some((admin: { login: string }) => admin.login === currentUserLogin)

    const isMentor =
      hasModule &&
      (moduleNode?.mentors || []).some(
        (mentor: { login: string }) => mentor.login === currentUserLogin
      )

    setHasAccess(isAdmin || isMentor)
  }, [sessionStatus, currentUserLogin, isLoading, accessData])

  return hasAccess
}
