'use client'
import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams, useRouter } from 'next/navigation'
import React, { useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { UpdateBoardCandidateClaimDocument } from 'types/__generated__/claimMutations.generated'
import { GetBoardCandidateClaimDocument } from 'types/__generated__/claimQueries.generated'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import ClaimForm from 'components/ClaimForm'
import LoadingSpinner from 'components/LoadingSpinner'

const EditClaimPage = () => {
  const router = useRouter()
  const { claimKey, login, year } = useParams<{ claimKey: string; login: string; year: string }>()
  const { isSyncing, session } = useDjangoSession()
  const {
    data: graphQLData,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetBoardCandidateClaimDocument, {
    fetchPolicy: 'cache-and-network',
    skip: !claimKey || session?.user?.login !== login,
    variables: { key: claimKey, login: login, year: Number.parseInt(year) },
  })

  const [updateClaim, { loading }] = useMutation(UpdateBoardCandidateClaimDocument)
  const [formData, setFormData] = useState({
    description: '',
    name: '',
  })
  const [backendErrors, setBackendErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError])

  const claim = graphQLData?.boardCandidateClaim

  useEffect(() => {
    if (claim) {
      setFormData({
        description: claim.description ?? '',
        name: claim.name ?? '',
      })
    }
  }, [claim])

  if (isLoading || isSyncing) return <LoadingSpinner />

  if (session?.user?.login !== login) {
    return (
      <AccessDeniedDisplay title="Access Denied" message="You can only view your own claims." />
    )
  }

  if (graphQLRequestError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading claim"
        message="An error occurred while loading the claim data"
      />
    )
  }

  if (!graphQLData || !claim) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Claim Not Found"
        message="Sorry, the claim you're looking for doesn't exist."
      />
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const input = {
      description: formData.description,
      key: claimKey,
      name: formData.name,
      year: Number.parseInt(year),
    }

    try {
      const result = await updateClaim({
        variables: { input },
        update(cache, { data }) {
          const updatedClaim = data?.updateBoardCandidateClaim?.claim
          if (!updatedClaim) return
          cache.writeQuery({
            query: GetBoardCandidateClaimDocument,
            variables: { key: claimKey, login, year: Number.parseInt(year) },
            data: { boardCandidateClaim: updatedClaim },
          })
        },
      })

      const payload = result.data?.updateBoardCandidateClaim
      if (!payload?.ok) {
        if (payload?.fieldErrors?.length) {
          setBackendErrors(
            Object.fromEntries(payload.fieldErrors.map((fe) => [fe.field, fe.message]))
          )
        } else {
          addToast({
            description: payload?.message ?? 'Claim update failed.',
            timeout: 3000,
            shouldShowTimeoutProgress: true,
            color: 'danger',
          })
        }
        return
      }

      addToast({
        description: 'Claim updated successfully!',
        title: 'Success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'success',
      })

      const updatedClaim = payload.claim
      if (updatedClaim?.key) {
        router.push(`/board/${year}/candidates/${login}/claims/${updatedClaim.key}`)
      }
    } catch (error) {
      addToast({
        description: error instanceof Error ? error.message : 'Claim update failed.',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
      })
    }
  }

  return (
    <ClaimForm
      formData={formData}
      setFormData={setFormData}
      backendErrors={backendErrors}
      setBackendErrors={setBackendErrors}
      onSubmit={handleSubmit}
      loading={loading}
      title="Edit Claim"
      submitText="Edit Claim"
    />
  )
}

export default EditClaimPage
