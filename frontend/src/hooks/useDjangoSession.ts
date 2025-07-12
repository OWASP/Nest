import { useMutation } from '@apollo/client'
import { useSession } from 'next-auth/react'
import { useEffect, useState } from 'react'
import { SYNC_DJANGO_SESSION_MUTATION } from 'server/queries/authQueries'
import { ExtendedSession } from 'types/program'

const SYNC_STATUS_KEY = 'django_session_synced'

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

      syncSession({
        variables: {
          accessToken: (session as ExtendedSession).accessToken,
        },
      })
        .then(() => {
          sessionStorage.setItem(SYNC_STATUS_KEY, 'true')
        })
        .catch(() => {
          throw new Error()
        })
        .finally(() => {
          setIsSyncing(false)
        })
    }
  }, [status, session, syncSession])

  return { isSyncing: loading || isSyncing }
}
