import { useMutation } from '@apollo/client'
import { useSession } from 'next-auth/react'
import { useEffect, useRef } from 'react'
import { SYNC_DJANGO_SESSION_MUTATION } from 'server/queries/authQueries'

declare module 'next-auth' {
  interface Session {
    accessToken?: string
  }
}

export const useDjangoSession = () => {
  const { data: session, status } = useSession()
  const [syncSession, { loading }] = useMutation(SYNC_DJANGO_SESSION_MUTATION)
  const syncAttempted = useRef(false)

  useEffect(() => {
    if (status === 'unauthenticated') {
      syncAttempted.current = false
    }

    if (status === 'authenticated' && session?.accessToken) {
      if (!syncAttempted.current) {
        syncAttempted.current = true
        syncSession({
          variables: {
            accessToken: session.accessToken,
          },
        }).catch((error) => {
          throw new Error(`Failed to sync Django session: ${error.message}`)
        })
      }
    }
  }, [status, session, syncSession])
  return { isSyncing: loading }
}
