'use client'
import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import React, { Suspense, useEffect, useState } from 'react'

import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetBoardCandidateDocument } from 'types/__generated__/boardQueries.generated'
import { CreateBoardCandidateClaimDocument } from 'types/__generated__/claimMutations.generated'
import { GetBoardCandidateClaimsDocument } from 'types/__generated__/claimQueries.generated'
import { handleMutationPayloadErrors } from 'utils/helpers/handleGraphQLError'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import ClaimForm from 'components/ClaimForm'
import LoadingSpinner from 'components/LoadingSpinner'

const CreateClaimContent = () => {
  const router = useRouter()
  const { isSyncing, session } = useDjangoSession()
  const { login, year } = useParams<{ login: string; year: string }>()
  const searchParams = useSearchParams()

  const [createClaim, { loading }] = useMutation(CreateBoardCandidateClaimDocument)

  const [formData, setFormData] = useState({
    description: '',
    name: '',
    sourceText: searchParams.get('sourceText') ?? '',
  })
  const [backendErrors, setBackendErrors] = useState<Record<string, string>>({})

  const {
    data: candidateGraphQLData,
    loading: isCandidateLoading,
    error: candidateQueryError,
  } = useQuery(GetBoardCandidateDocument, {
    skip: !login || !year || session?.user?.login !== login,
    variables: { login: login, year: Number.parseInt(year) },
  })

  useEffect(() => {
    if (candidateQueryError) {
      handleAppError(candidateQueryError)
    }
  }, [candidateQueryError])

  if (isSyncing || isCandidateLoading) {
    return <LoadingSpinner />
  }

  if (candidateQueryError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading candidate"
        message="An error occurred while loading the candidate data"
      />
    )
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

    const input = {
      description: formData.description,
      name: formData.name,
      sourceText: formData.sourceText,
      year: Number.parseInt(year),
    }

    try {
      const result = await createClaim({
        variables: { input },
        update(cache, { data }) {
          const newClaim = data?.createBoardCandidateClaim?.claim
          if (!newClaim) return
          const existing = cache.readQuery({
            query: GetBoardCandidateClaimsDocument,
            variables: { login, year: Number.parseInt(year) },
          })
          if (existing) {
            cache.writeQuery({
              query: GetBoardCandidateClaimsDocument,
              variables: { login, year: Number.parseInt(year) },
              data: { boardCandidateClaims: [...existing.boardCandidateClaims, newClaim] },
            })
          }
        },
      })

      const payload = result.data?.createBoardCandidateClaim
      if (!handleMutationPayloadErrors(payload, 'Claim creation failed.', setBackendErrors)) {
        return
      }

      addToast({
        description: 'Claim created successfully!',
        title: 'Success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'success',
      })

      router.push(`/board/${year}/candidates/${login}/claims`)
    } catch (error) {
      addToast({
        description: error instanceof Error ? error.message : 'Claim creation failed.',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
      })
    }
  }

  const isSourceTextReadOnly = Boolean(searchParams.get('sourceText'))

  return (
    <ClaimForm
      formData={formData}
      setFormData={setFormData}
      backendErrors={backendErrors}
      setBackendErrors={setBackendErrors}
      onSubmit={handleSubmit}
      loading={loading}
      title="Create Claim"
      isSourceTextReadOnly={isSourceTextReadOnly}
    />
  )
}

const CreateClaimPage = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <CreateClaimContent />
    </Suspense>
  )
}

export default CreateClaimPage
