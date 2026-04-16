import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useState } from 'react'
import {
  AssignIssueToUserDocument,
  ClearTaskDeadlineDocument,
  GetModuleIssueViewDocument,
  SetTaskDeadlineDocument,
  UnassignIssueFromUserDocument,
} from 'types/__generated__/issueQueries.generated'

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
        query: GetModuleIssueViewDocument,
        variables: { programKey, moduleKey, number: Number(issueId) },
      },
    ],
    awaitRefetchQueries: true,
  }

  const [assignIssue, { loading: assigning }] = useMutation(AssignIssueToUserDocument, {
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

  const [unassignIssue, { loading: unassigning }] = useMutation(UnassignIssueFromUserDocument, {
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

  const [setTaskDeadlineMutation, { loading: settingDeadline }] = useMutation(
    SetTaskDeadlineDocument,
    {
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
    }
  )

  const [clearTaskDeadlineMutation, { loading: clearingDeadline }] = useMutation(
    ClearTaskDeadlineDocument,
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
