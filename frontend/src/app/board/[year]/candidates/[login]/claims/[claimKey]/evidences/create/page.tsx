'use client'
import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams, useRouter } from 'next/navigation'
import React, { useState } from 'react'

import { CreateBoardCandidateClaimEvidenceDocument } from 'types/__generated__/evidenceMutations.generated'
import { GetBoardCandidateClaimEvidencesDocument } from 'types/__generated__/evidenceQueries.generated'
import { extractGraphQLErrors } from 'utils/helpers/handleGraphQLError'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import EvidenceForm from 'components/EvidenceForm'
import LoadingSpinner from 'components/LoadingSpinner'

const CreateEvidencePage = () => {
  const router = useRouter()
  const { isSyncing, session } = useDjangoSession()
  const { claimKey, login, year } = useParams<{ claimKey: string; login: string; year: string }>()

  const [createEvidence, { loading }] = useMutation(CreateBoardCandidateClaimEvidenceDocument)

  const [formData, setFormData] = useState({
    description: '',
    name: '',
    file: null as File | null,
    sourceUrl: '',
  })

  if (session?.user?.login !== login) {
    return (
      <AccessDeniedDisplay
        title="Access Denied"
        message="You must be a candidate to add an evidence."
      />
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const input = {
        claimKey: claimKey,
        description: formData.description,
        file: formData.file,
        name: formData.name,
        sourceUrl: formData.sourceUrl,
        year: Number.parseInt(year),
      }

      const result = await createEvidence({
        variables: { input },
        update(cache, { data }) {
          const newEvidence = data?.createBoardCandidateClaimEvidence?.evidence
          if (!newEvidence) return
          const existing = cache.readQuery({
            query: GetBoardCandidateClaimEvidencesDocument,
            variables: { claimKey, login, year: Number.parseInt(year) },
          })
          if (existing) {
            cache.writeQuery({
              query: GetBoardCandidateClaimEvidencesDocument,
              variables: { claimKey, login, year: Number.parseInt(year) },
              data: {
                boardCandidateClaimEvidences: [
                  ...existing.boardCandidateClaimEvidences,
                  newEvidence,
                ],
              },
            })
          }
        },
      })

      if (!result.data?.createBoardCandidateClaimEvidence?.ok) {
        throw new Error(
          result.data?.createBoardCandidateClaimEvidence?.message ?? 'Evidence creation failed.'
        )
      }

      addToast({
        description: 'Evidence created successfully!',
        title: 'Success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'success',
      })

      router.push(`/board/${year}/candidates/${login}/claims/${claimKey}`)
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
      title="Add Evidence"
    />
  )
}

export default CreateEvidencePage
