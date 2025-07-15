import { useMutation } from '@apollo/client'
import { useSession } from 'next-auth/react'
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
    // If the session is unauthenticated, remove the sync status flag
    // so next login re‑runs sync
    if (status === 'unauthenticated') {
      sessionStorage.removeItem(SYNC_STATUS_KEY)
      return
    }

    const shouldSync =
      status === 'authenticated' && //logged in via jwt
      (session as ExtendedSession)?.accessToken && // we have GH Token
      !sessionStorage.getItem(SYNC_STATUS_KEY) //not yet synced

    if (shouldSync) {
      setIsSyncing(true)

      // sends  Github token to Django.
      // On Success, Django writes session cookie, browser stores it

      syncSession({
        variables: {
          accessToken: (session as ExtendedSession).accessToken,
        },
      })
        .then(() => {
          sessionStorage.setItem(SYNC_STATUS_KEY, 'true')
        })
        .catch(() => {
          throw new Error('Failed to sync Django session')
        })
        .finally(() => {
          setIsSyncing(false)
        })
    }
  }, [status, session, syncSession])

  return { isSyncing: loading || isSyncing }
}
