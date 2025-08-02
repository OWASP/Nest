import { useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { IS_PROJECT_LEADER_QUERY } from 'server/queries/mentorshipQueries'

export const useProjectLeader = () => {
  const { data, loading, error } = useQuery(IS_PROJECT_LEADER_QUERY, {
    fetchPolicy: 'network-only',
    onError: () => {
      addToast({
        title: 'Permission Check Failed',
        description: 'Could not verify your permissions. Please try again later.',
        color: 'danger',
        timeout: 3000,
        variant: 'solid',
      })
    },
  })

  return {
    isLeader: data?.isProjectLeader ?? false,
    loading,
    error,
  }
}
