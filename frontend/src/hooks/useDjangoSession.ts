import { useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useSession, signOut } from 'next-auth/react'
import { useEffect, useState } from 'react'
import { SYNC_DJANGO_SESSION_MUTATION } from 'server/queries/authQueries'
import { ExtendedSession } from 'types/auth'

const SYNC_STATUS_KEY = 'django_session_synced'

export const useDjangoSession: () => { isSyncing: boolean; session?: ExtendedSession } = () => {
  const { data: session, status, update } = useSession()
  const [syncSession, { loading }] = useMutation(SYNC_DJANGO_SESSION_MUTATION)
  const [isSyncing, setIsSyncing] = useState(false)

  useEffect(() => {
    if (status === 'unauthenticated') {
      sessionStorage.removeItem(SYNC_STATUS_KEY)
      return
    }

    const shouldSync =
      status === 'authenticated' &&
      (session as ExtendedSession)?.accessToken &&
      !sessionStorage.getItem(SYNC_STATUS_KEY)

    if (shouldSync) {
      setIsSyncing(true)

      // The backend response contains a backend session cookie if successful.
      // The cookie name is set in SESSION_COOKIE_NAME of backend/settings/base.py.
      syncSession({
        variables: {
          accessToken: (session as ExtendedSession).accessToken,
        },
      })
        .then((response) => {
          const githubAuth = response?.data?.githubAuth
          if (githubAuth?.ok) {
            sessionStorage.setItem(SYNC_STATUS_KEY, 'true')
            update({
              user: {
                ...session.user,
                isOwaspStaff: githubAuth.user?.isOwaspStaff,
              },
            }).then(() => {})
          } else {
            signOut() // Invalidate Next.js session if not ok.
            addToast({
              color: 'danger',
              description: githubAuth?.message,
              shouldShowTimeoutProgress: true,
              timeout: 4000,
              title: 'Authentication Failed',
              variant: 'bordered',
            })
          }
        })
        .catch(() => {
          addToast({
            color: 'danger',
            description: 'Failed to sign in with GitHub',
            shouldShowTimeoutProgress: true,
            timeout: 4000,
            title: 'Authentication Failed',
            variant: 'bordered',
          })
        })
        .finally(() => {
          setIsSyncing(false)
        })
    }
  }, [status, session, syncSession, update])

  return {
    isSyncing: loading || isSyncing || status === 'loading',
    session: session as ExtendedSession,
  }
}
