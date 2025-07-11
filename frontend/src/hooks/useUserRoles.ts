'use client'
import { gql, useQuery } from '@apollo/client'

export const GET_USER_ROLES = gql`
  query GetUserRoles {
    currentUserRoles {
      roles
    }
  }
`

interface UserRolesData {
  currentUserRoles: {
    roles: string[]
  }
}

export const useUserRoles = () => {
  const { data, loading, error } = useQuery<UserRolesData>(GET_USER_ROLES)
  return {
    roles: data?.currentUserRoles?.roles ?? [],
    isLoadingRoles: loading,
    error,
  }
}
