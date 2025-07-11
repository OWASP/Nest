import { gql, useMutation } from '@apollo/client'
import { signOut } from 'next-auth/react'
import { useState } from 'react'

const LOGOUT_DJANGO_MUTATION = gql`
  mutation LogoutDjango {
    logoutUser
  }
`

export const useLogout = () => {
  const [logoutUser, { loading, client }] = useMutation(LOGOUT_DJANGO_MUTATION)
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await logoutUser()
      await client.clearStore()
      await signOut({ callbackUrl: '/' })
    } catch (error) {
      await signOut({ callbackUrl: '/' })
      throw new Error('Logout failed: ' + error.message)
    } finally {
      setIsLoggingOut(false)
    }
  }

  return { logout: handleLogout, isLoggingOut: loading || isLoggingOut }
}
