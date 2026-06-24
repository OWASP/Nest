'use client'

import { useMutation } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/modal'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import type React from 'react'
import { GetBoardCandidateClaimDocument } from 'types/__generated__/claimQueries.generated'
import { RemoveBoardCandidateClaimEvidenceDocument } from 'types/__generated__/evidenceMutations.generated'
import { GetBoardCandidateClaimEvidencesDocument } from 'types/__generated__/evidenceQueries.generated'
import DropdownActions from 'components/DropdownActions'

interface ClaimProperties {
  id: string
  description: string
  key: string
  name: string
  status: string
  updatedAt: string
}

interface EvidenceProperties {
  id: string
  createdAt: string
  description: string
  key: string
  name: string
  sourceUrl: string
  updatedAt: string
}

interface EvidenceActionsProps {
  claim: ClaimProperties
  evidence: EvidenceProperties
  login: string
  year: string
}

const EvidenceActions: React.FC<EvidenceActionsProps> = ({ claim, evidence, login, year }) => {
  const router = useRouter()
  const [confirmRemove, setConfirmRemove] = useState<boolean>(false)
  const [reason, setReason] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [removeEvidence] = useMutation(RemoveBoardCandidateClaimEvidenceDocument)

  const resetConfirm = () => {
    setConfirmRemove(false)
    setReason(null)
  }

  const handleConfirmRemove = async () => {
    setIsLoading(true)

    try {
      const result = await removeEvidence({
        variables: {
          input: {
            key: evidence.key,
            claimKey: claim.key,
            removedReason: reason,
            year: Number.parseInt(year),
          },
        },
        refetchQueries: [
          {
            query: GetBoardCandidateClaimDocument,
            variables: { key: claim.key, login, year: Number.parseInt(year) },
          },
          {
            query: GetBoardCandidateClaimEvidencesDocument,
            variables: { claimKey: claim.key, login, year: Number.parseInt(year) },
          },
        ],
      })

      if (!result.data?.removeBoardCandidateClaimEvidence?.ok) {
        throw new Error(
          result.data?.removeBoardCandidateClaimEvidence?.message ?? 'Evidence remove failed.'
        )
      }

      addToast({
        title: 'Success',
        description: 'Evidence removed successfully.',
        color: 'success',
      })

      resetConfirm()
      router.push(`/board/${year}/candidates/${login}/claims/${claim.key}`)
    } catch (error) {
      addToast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Evidence remove failed.',
        color: 'danger',
      })
    } finally {
      setIsLoading(false)
    }
  }

  const options = [
    ...(claim.status == 'DRAFT'
      ? [
          {
            key: 'edit',
            label: 'Edit Evidence',
            onAction: () =>
              router.push(
                `/board/${year}/candidates/${login}/claims/${claim.key}/evidences/${evidence.key}/edit`
              ),
          },
        ]
      : []),
    ...(['DRAFT', 'DISCARDED', 'WITHDRAWN'].includes(claim.status)
      ? [
          {
            key: 'remove',
            label: 'Remove Evidence',
            onAction: () => setConfirmRemove(true),
          },
        ]
      : []),
  ]

  return (
    <>
      <DropdownActions options={options} />
      <Modal
        isOpen={!!confirmRemove}
        onClose={() => {
          resetConfirm()
        }}
      >
        <ModalContent>
          <ModalHeader className="flex flex-col gap-1">Remove Evidence</ModalHeader>
          <ModalBody>
            <p>Are you sure you want to remove this evidence? This action cannot be undone.</p>
          </ModalBody>
          <ModalBody>
            <textarea
              className="mt-2 w-full rounded border p-2"
              rows={3}
              placeholder="Reason for removal..."
              value={reason ?? ''}
              onChange={(e) => setReason(e.target.value)}
            />
          </ModalBody>
          <ModalFooter>
            <Button
              color="default"
              variant="light"
              onPress={() => {
                resetConfirm()
              }}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              color="danger"
              onPress={handleConfirmRemove}
              isLoading={isLoading}
              disabled={isLoading}
              className="text-white"
            >
              Remove
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default EvidenceActions
