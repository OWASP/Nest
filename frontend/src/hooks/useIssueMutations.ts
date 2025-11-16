import { useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useState } from 'react'
import {
  ASSIGN_ISSUE_TO_USER,
  CLEAR_TASK_DEADLINE,
  GET_MODULE_ISSUE_VIEW,
  SET_TASK_DEADLINE,
  UNASSIGN_ISSUE_FROM_USER,
} from 'server/queries/issueQueries'

interface UseIssueMutationsProps {
  programKey: string
  moduleKey: string
  issueId: string
}

export const useIssueMutations = ({ programKey, moduleKey, issueId }: UseIssueMutationsProps) => {
  const [isEditingDeadline, setIsEditingDeadline] = useState(false)
  const [deadlineInput, setDeadlineInput] = useState<string>('')

  const commonMutationConfig = {
    refetchQueries: [
      {
        query: GET_MODULE_ISSUE_VIEW,
        variables: { programKey, moduleKey, number: Number(issueId) },
      },
    ],
    awaitRefetchQueries: true,
  }

  const [assignIssue, { loading: assigning }] = useMutation(ASSIGN_ISSUE_TO_USER, {
    ...commonMutationConfig,
    onCompleted: () => {
      addToast({
        title: 'Issue assigned successfully',
        variant: 'solid',
        color: 'success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
    },
    onError: (error) => {
      addToast({
        title: 'Failed to assign issue: ' + error.message,
        variant: 'solid',
        color: 'danger',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
    },
  })

  const [unassignIssue, { loading: unassigning }] = useMutation(UNASSIGN_ISSUE_FROM_USER, {
    ...commonMutationConfig,
    onCompleted: () => {
      addToast({
        title: 'Issue unassigned successfully',
        variant: 'solid',
        color: 'success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
    },
    onError: (error) => {
      addToast({
        title: 'Failed to unassign issue: ' + error.message,
        variant: 'solid',
        color: 'danger',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
    },
  })

  const [setTaskDeadlineMutation, { loading: settingDeadline }] = useMutation(SET_TASK_DEADLINE, {
    ...commonMutationConfig,
    onCompleted: () => {
      addToast({
        title: 'Deadline updated',
        variant: 'solid',
        color: 'success',
        timeout: 2500,
        shouldShowTimeoutProgress: true,
      })
      setIsEditingDeadline(false)
    },
    onError: (err) => {
      addToast({
        title: 'Failed to update deadline: ' + err.message,
        variant: 'solid',
        color: 'danger',
        timeout: 3500,
        shouldShowTimeoutProgress: true,
      })
    },
  })

  const [clearTaskDeadlineMutation, { loading: clearingDeadline }] = useMutation(
    CLEAR_TASK_DEADLINE,
    {
      ...commonMutationConfig,
      onCompleted: () => {
        addToast({
          title: 'Deadline cleared',
          variant: 'solid',
          color: 'success',
          timeout: 2500,
          shouldShowTimeoutProgress: true,
        })
        setIsEditingDeadline(false)
      },
      onError: (err) => {
        addToast({
          title: 'Failed to clear deadline: ' + err.message,
          variant: 'solid',
          color: 'danger',
          timeout: 3500,
          shouldShowTimeoutProgress: true,
        })
      },
    }
  )

  return {
    // Mutations
    assignIssue,
    unassignIssue,
    setTaskDeadlineMutation,
    clearTaskDeadlineMutation,

    // Loading states
    assigning,
    unassigning,
    settingDeadline,
    clearingDeadline,

    // Deadline state
    isEditingDeadline,
    setIsEditingDeadline,
    deadlineInput,
    setDeadlineInput,
  }
}
