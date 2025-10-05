import { useMutation } from '@apollo/client/react'
import { signOut } from 'next-auth/react'
import { useState } from 'react'
import { LogoutDjangoDocument } from 'types/__generated__/authQueries.generated'

// Handles logout:
// 1) calls Django logout mutation (invalidates session cookie),
// 2) signs the user out of NextAuth (clears JWT & redirects),
// 3) clears Apollo cache so no user data lingers in memory.

export const useLogout = () => {
  const [logoutUser, { loading, client }] = useMutation(LogoutDjangoDocument)
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await logoutUser() // Removes Django session cookie
      await signOut({ callbackUrl: '/' }) // Removes NextAuth session (JWT)
      await client.clearStore() // Removes Apollo cache
    } catch (error) {
      await signOut({ callbackUrl: '/' })
      throw new Error('Logout failed: ' + error.message)
    } finally {
      setIsLoggingOut(false)
    }
  }

  return { logout: handleLogout, isLoggingOut: loading || isLoggingOut }
}
