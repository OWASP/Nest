import { useMutation } from '@apollo/client'
import { signOut } from 'next-auth/react'
import { useState } from 'react'
import { LOGOUT_DJANGO_MUTATION } from 'server/queries/authQueries'

// Handles logout:
// 1) calls Django logout mutation (invalidates session cookie),
// 2) signs the user out of NextAuth (clears JWT & redirects),
// 3) clears Apollo cache so no user data lingers in memory.

export const useLogout = () => {
  const [logoutUser, { loading, client }] = useMutation(LOGOUT_DJANGO_MUTATION)
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
