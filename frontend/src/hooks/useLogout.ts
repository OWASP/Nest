import { useMutation } from '@apollo/client'
import { signOut } from 'next-auth/react'
import { useState } from 'react'
import { LOGOUT_DJANGO_MUTATION } from 'server/queries/authQueries'


export const useLogout = () => {
  const [logoutUser, { loading, client }] = useMutation(LOGOUT_DJANGO_MUTATION)
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await logoutUser()
      await signOut({ callbackUrl: '/' })
      await client.clearStore()
    } catch (error) {
      await signOut({ callbackUrl: '/' })
      throw new Error('Logout failed: ' + error.message)
    } finally {
      setIsLoggingOut(false)
    }
  }

  return { logout: handleLogout, isLoggingOut: loading || isLoggingOut }
}
