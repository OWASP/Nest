'use client'
import { useQuery } from '@apollo/client'
import { GET_USER_ROLES } from 'server/queries/authQueries'
import type { UserRolesData } from 'types/auth'

// Custom hook to fetch the current user's roles using a GraphQL query.
// It returns the list of roles (e.g., 'mentor', 'contributor'), a loading state,
// and any potential error encountered during the query.
// This is typically used to conditionally render UI based on the user's role.

export const useUserRoles = () => {
  const { data, loading, error } = useQuery<UserRolesData>(GET_USER_ROLES)
  return {
    roles: data?.currentUserRoles?.roles ?? [],
    isLoadingRoles: loading,
    error,
  }
}
