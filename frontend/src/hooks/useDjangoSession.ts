import { useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useSession, signOut } from 'next-auth/react'
import { useEffect, useState } from 'react'
import { SYNC_DJANGO_SESSION_MUTATION } from 'server/queries/authQueries'
import { ExtendedSession } from 'types/auth'

// flag in sessionStorage to indicate if the Django session has been synced
const SYNC_STATUS_KEY = 'django_session_synced'

/*
Purpose:
  1. Wait for NextAuth to finish (status == 'authenticated')
  2. Grab Github `accessToken` from JWT.
  3. Fire SYNC_DJANGO_SESSION_MUTATION with the accessToken.
  4. Resolved request from the Django will return with cookie
     that automatically handled by the client and the cookie will be fixed
  5. Store a flag in sessionStorage to indicate that the Django session has been synced

*/

export const useDjangoSession = () => {
  const { data: session, status } = useSession()
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
            addToast({
              color: 'success',
              description: githubAuth?.message,
              shouldShowTimeoutProgress: true,
              timeout: 3000,
              title: 'Authentication Successful',
              variant: 'solid',
            })
          } else {
            signOut() // Invalidate Next.js session if not ok
            addToast({
              color: 'danger',
              description: githubAuth?.message,
              shouldShowTimeoutProgress: true,
              timeout: 4000,
              title: 'Authentication Failed',
              variant: 'solid',
            })
            return
          }
        })
        .catch(() => {
          addToast({
            color: 'danger',
            description: 'Failed to sign in with GitHub',
            shouldShowTimeoutProgress: true,
            timeout: 4000,
            title: 'Authentication Failed',
            variant: 'solid',
          })
        })
        .finally(() => {
          setIsSyncing(false)
        })
    }
  }, [status, session, syncSession])

  return { isSyncing: loading || isSyncing }
}
