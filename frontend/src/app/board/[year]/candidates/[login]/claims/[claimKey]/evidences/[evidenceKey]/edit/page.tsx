'use client'
import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams, useRouter } from 'next/navigation'
import React, { useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { UpdateBoardCandidateClaimEvidenceDocument } from 'types/__generated__/evidenceMutations.generated'
import { GetBoardCandidateClaimEvidenceDocument } from 'types/__generated__/evidenceQueries.generated'
import { extractGraphQLErrors } from 'utils/helpers/handleGraphQLError'
import slugify from 'utils/slugify'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import EvidenceForm from 'components/EvidenceForm'
import LoadingSpinner from 'components/LoadingSpinner'

const EditEvidencePage = () => {
  const router = useRouter()
  const { claimKey, evidenceKey, login, year } = useParams<{
    claimKey: string
    evidenceKey: string
    login: string
    year: string
  }>()
  const { isSyncing, session } = useDjangoSession()
  const {
    data: graphQLData,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetBoardCandidateClaimEvidenceDocument, {
    fetchPolicy: 'cache-and-network',
    skip: !evidenceKey || session?.user?.login !== login,
    variables: { claimKey, key: evidenceKey, login, year: Number.parseInt(year) },
  })

  const [updateEvidence, { loading }] = useMutation(UpdateBoardCandidateClaimEvidenceDocument)
  const [formData, setFormData] = useState({
    description: '',
    name: '',
    file: null as File | null,
    sourceUrl: '',
  })

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError])

  const evidence = graphQLData?.boardCandidateClaimEvidence

  useEffect(() => {
    if (evidence) {
      setFormData({
        description: evidence.description ?? '',
        name: evidence.name ?? '',
        file: null,
        sourceUrl: evidence.sourceUrl ?? '',
      })
    }
  }, [evidence])

  if (isLoading || isSyncing) return <LoadingSpinner />

  if (graphQLRequestError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading program"
        message="An error occurred while loading the evidence data"
      />
    )
  }

  if (!graphQLData || !evidence) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Evidence Not Found"
        message="Sorry, the evidence you're looking for doesn't exist."
      />
    )
  }

  if (session?.user?.login !== login) {
    return (
      <AccessDeniedDisplay title="Access Denied" message="You can only view your own claims." />
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const input = {
        claimKey: claimKey,
        description: formData.description,
        file: formData.file || null,
        key: evidenceKey,
        name: formData.name,
        sourceUrl: formData.sourceUrl,
        year: Number.parseInt(year),
      }

      const result = await updateEvidence({
        awaitRefetchQueries: true,
        refetchQueries: [
          {
            query: GetBoardCandidateClaimEvidenceDocument,
            variables: { claimKey, key: evidenceKey, login, year: Number.parseInt(year) },
          },
        ],
        variables: { input },
      })

      if (!result.data?.updateBoardCandidateClaimEvidence?.ok) {
        throw new Error(
          result.data?.updateBoardCandidateClaimEvidence?.message ?? 'Evidence update failed.'
        )
      }

      addToast({
        description: 'Evidence updated successfully!',
        title: 'Success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'success',
      })

      router.push(
        `/board/${year}/candidates/${login}/claims/${claimKey}/evidences/${slugify(formData.name)}`
      )
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

  if (isSyncing) {
    return <LoadingSpinner />
  }

  return (
    <EvidenceForm
      formData={formData}
      setFormData={setFormData}
      onSubmit={handleSubmit}
      loading={loading}
      title="Edit Evidence"
      submitText="Update Evidence"
    />
  )
}

export default EditEvidencePage
