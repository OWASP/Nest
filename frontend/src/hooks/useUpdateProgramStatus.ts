import { DocumentNode } from '@apollo/client'
import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import upperFirst from 'lodash/upperFirst'
import { handleAppError } from 'app/global-error'
import { ProgramStatusEnum } from 'types/__generated__/graphql'
import { UpdateProgramStatusDocument } from 'types/__generated__/programsMutations.generated'

interface UseUpdateProgramStatusProps {
  programKey: string
  programName: string
  isAdmin: boolean
  refetchQueries?: { query: DocumentNode; variables: { programKey: string } }[]
}

export const useUpdateProgramStatus = ({
  programKey,
  programName,
  isAdmin,
  refetchQueries = [],
}: UseUpdateProgramStatusProps) => {
  const [updateProgramMutation] = useMutation(UpdateProgramStatusDocument, {
    onError: handleAppError,
  })

  const updateProgramStatus = async (newStatus: ProgramStatusEnum) => {
    if (!isAdmin) {
      addToast({
        title: 'Permission Denied',
        description: 'Only admins can update the program status.',
        variant: 'solid',
        color: 'danger',
        timeout: 3000,
      })
      return
    }

    try {
      await updateProgramMutation({
        variables: {
          inputData: {
            key: programKey,
            name: programName,
            status: newStatus,
          },
        },
        refetchQueries,
      })

      addToast({
        title: `Program status updated to ${upperFirst(newStatus)}`,
        description: 'The status has been successfully updated.',
        variant: 'solid',
        color: 'success',
        timeout: 3000,
      })
    } catch (err) {
      handleAppError(err)
    }
  }

  return { updateProgramStatus }
}
