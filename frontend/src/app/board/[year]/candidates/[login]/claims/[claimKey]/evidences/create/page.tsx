'use client'
import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams, useRouter } from 'next/navigation'
import React, { useState } from 'react'

import { GetClaimAndEvidencesDocument } from 'types/__generated__/claimQueries.generated'
import { CreateBoardCandidateClaimEvidenceDocument } from 'types/__generated__/evidenceMutations.generated'
import { handleMutationPayloadErrors } from 'utils/helpers/handleGraphQLError'
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
  const [backendErrors, setBackendErrors] = useState<Record<string, string>>({})

  if (isSyncing) {
    return <LoadingSpinner />
  }

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

    const input = {
      claimKey: claimKey,
      description: formData.description,
      file: formData.file,
      name: formData.name,
      sourceUrl: formData.sourceUrl.trim() || null,
      year: Number.parseInt(year),
    }

    try {
      const result = await createEvidence({
        variables: { input },
        update(cache, { data }) {
          const newEvidence = data?.createBoardCandidateClaimEvidence?.evidence
          if (!newEvidence) return
          const existing = cache.readQuery({
            query: GetClaimAndEvidencesDocument,
            variables: {
              key: claimKey,
              login,
              sessionLogin: session?.user?.login ?? '',
              year: Number.parseInt(year),
            },
          })
          if (existing) {
            cache.writeQuery({
              query: GetClaimAndEvidencesDocument,
              variables: {
                key: claimKey,
                login,
                sessionLogin: session?.user?.login ?? '',
                year: Number.parseInt(year),
              },
              data: {
                ...existing,
                boardCandidateClaimEvidences: [
                  ...existing.boardCandidateClaimEvidences,
                  newEvidence,
                ],
              },
            })
          }
        },
      })

      const payload = result.data?.createBoardCandidateClaimEvidence
      if (!handleMutationPayloadErrors(payload, 'Evidence creation failed.', setBackendErrors)) {
        return
      }

      addToast({
        description: 'Evidence created successfully!',
        title: 'Success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'success',
      })

      router.push(`/board/${year}/candidates/${login}/claims/${claimKey}`)
    } catch (error) {
      addToast({
        description: error instanceof Error ? error.message : 'Evidence creation failed.',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
      })
    }
  }

  return (
    <EvidenceForm
      formData={formData}
      setFormData={setFormData}
      backendErrors={backendErrors}
      setBackendErrors={setBackendErrors}
      onSubmit={handleSubmit}
      loading={loading}
      title="Add Evidence"
    />
  )
}

export default CreateEvidencePage
