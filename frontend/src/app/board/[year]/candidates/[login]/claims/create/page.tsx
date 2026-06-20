'use client'
import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams, useRouter } from 'next/navigation'
import React, { useState } from 'react'

import { GetBoardCandidateDocument } from 'types/__generated__/boardQueries.generated'
import { CreateBoardCandidateClaimDocument } from 'types/__generated__/claimMutations.generated'
import { GetBoardCandidateClaimsDocument } from 'types/__generated__/claimQueries.generated'
import { extractGraphQLErrors } from 'utils/helpers/handleGraphQLError'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import ClaimForm from 'components/ClaimForm'
import LoadingSpinner from 'components/LoadingSpinner'

const CreateClaimPage = () => {
  const router = useRouter()
  const { isSyncing, session } = useDjangoSession()
  const { login, year } = useParams<{ login: string; year: string }>()

  const [createClaim, { loading }] = useMutation(CreateBoardCandidateClaimDocument)

  const [formData, setFormData] = useState({
    description: '',
    name: '',
  })

  const { data: candidateGraphQLData, loading: isCandidateLoading } = useQuery(
    GetBoardCandidateDocument,
    {
      variables: { login: login, year: Number.parseInt(year) },
    }
  )

  if (isSyncing || isCandidateLoading) {
    return <LoadingSpinner />
  }

  const isCandidate = candidateGraphQLData?.boardOfDirectors?.candidate != null

  if (!isCandidate || session?.user?.login !== login) {
    return (
      <AccessDeniedDisplay
        title="Access Denied"
        message="You must be a candidate to create a claim."
      />
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const input = {
        description: formData.description,
        name: formData.name,
        year: Number.parseInt(year),
      }

      const result = await createClaim({
        awaitRefetchQueries: true,
        refetchQueries: [
          {
            query: GetBoardCandidateClaimsDocument,
            variables: { login, year: Number.parseInt(year) },
          },
        ],
        variables: { input },
      })

      if (!result.data?.createBoardCandidateClaim?.ok) {
        throw new Error(result.data?.createBoardCandidateClaim?.message ?? 'Claim creation failed.')
      }

      addToast({
        description: 'Claim created successfully!',
        title: 'Success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'success',
      })

      router.push(`/board/${year}/candidates/${login}/claims`)
    } catch (err) {
      const { hasValidationErrors } = extractGraphQLErrors(err)
      if (!hasValidationErrors) {
        addToast({
          description:
            err instanceof Error ? err.message : 'Unable to complete the requested operation.',
          timeout: 3000,
          shouldShowTimeoutProgress: true,
          color: 'danger',
        })
      }
      throw err
    }
  }

  return (
    <ClaimForm
      formData={formData}
      setFormData={setFormData}
      onSubmit={handleSubmit}
      loading={loading}
      title="Create Claim"
    />
  )
}

export default CreateClaimPage
