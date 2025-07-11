import { gql, useMutation } from '@apollo/client'
import { useSession } from 'next-auth/react'
import { useEffect, useRef } from 'react'
import { ExtendedSession } from 'types/program'

const SYNC_DJANGO_SESSION_MUTATION = gql`
  mutation SyncDjangoSession($accessToken: String!) {
    githubAuth(accessToken: $accessToken) {
      authUser {
        username
      }
    }
  }
`

export const useDjangoSession = () => {
  const { data: session, status } = useSession()
  const [syncSession, { loading }] = useMutation(SYNC_DJANGO_SESSION_MUTATION)
  const syncAttempted = useRef(false)

  useEffect(() => {
    if (status === 'unauthenticated') {
      syncAttempted.current = false
    }

    if (status === 'authenticated' && (session as ExtendedSession)?.accessToken) {
      if (!syncAttempted.current) {
        syncAttempted.current = true
        syncSession({
          variables: {
            accessToken: (session as ExtendedSession).accessToken,
          },
        })
          .then()
          .catch((error) => {
            throw new Error(`Failed to sync Django session: ${error.message}`)
          })
      }
    }
  }, [status, session, syncSession])
  return { isSyncing: loading }
}
