'use client'

import { ApolloCache } from '@apollo/client'
import { useMutation } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/modal'
import { addToast } from '@heroui/toast'
import { upperFirst } from 'lodash'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import type React from 'react'
import {
  DiscardBoardCandidateClaimDocument,
  SubmitBoardCandidateClaimDocument,
  WithdrawBoardCandidateClaimDocument,
} from 'types/__generated__/claimMutations.generated'
import { GetBoardCandidateClaimsDocument } from 'types/__generated__/claimQueries.generated'
import DropdownActions from 'components/DropdownActions'

interface ClaimProperties {
  id: string
  description: string
  key: string
  name: string
  status: string
  updatedAt: string
}

interface ClaimActionsProps {
  claim: ClaimProperties
  login: string
  year: string
}

type ClaimAction = 'submit' | 'discard' | 'withdraw'

const ACTIONS_BY_STATUS: Record<string, ClaimAction[]> = {
  DRAFT: ['submit', 'discard'],
  SUBMITTED: ['withdraw'],
  APPROVED: ['withdraw'],
  REJECTED: [],
  DISCARDED: [],
  WITHDRAWN: [],
}

const ClaimActions: React.FC<ClaimActionsProps> = ({ claim, login, year }) => {
  const router = useRouter()
  const [confirmAction, setConfirmAction] = useState<ClaimAction | null>(null)
  const [reason, setReason] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [submitClaim] = useMutation(SubmitBoardCandidateClaimDocument)
  const [discardClaim] = useMutation(DiscardBoardCandidateClaimDocument)
  const [withdrawClaim] = useMutation(WithdrawBoardCandidateClaimDocument)

  type ClaimNode = {
    __typename: 'BoardCandidateClaimNode'
    id: string
    key: string
    status: string
    name: string
    description: string
    order: number
    createdAt: string | number
    updatedAt: string | number
  }

  const updateClaimsCache = (
    cache: ApolloCache,
    mutationData: { claim?: ClaimNode | null } | null | undefined
  ) => {
    const updatedClaim = mutationData?.claim
    if (!updatedClaim) return
    const existing = cache.readQuery({
      query: GetBoardCandidateClaimsDocument,
      variables: { login, year: Number.parseInt(year) },
    })
    if (existing) {
      cache.writeQuery({
        query: GetBoardCandidateClaimsDocument,
        variables: { login, year: Number.parseInt(year) },
        data: {
          boardCandidateClaims: existing.boardCandidateClaims.map((c) =>
            c.key === updatedClaim.key ? updatedClaim : c
          ),
        },
      })
    }
  }

  const ACTION_HANDLERS: Record<ClaimAction, () => void> = {
    submit: () => setConfirmAction('submit'),
    discard: () => setConfirmAction('discard'),
    withdraw: () => setConfirmAction('withdraw'),
  }

  const resetConfirm = () => {
    setConfirmAction(null)
    setReason(null)
  }

  const handleConfirm = async () => {
    setIsLoading(true)

    const SUCCESS_MESSAGES: Record<ClaimAction, string> = {
      submit: 'Claim submitted successfully.',
      discard: 'Claim discarded successfully.',
      withdraw: 'Claim withdrawn successfully.',
    }

    try {
      let result

      switch (confirmAction) {
        case 'submit':
          result = await submitClaim({
            variables: { input: { key: claim.key, year: Number.parseInt(year) } },
            update: (cache, { data }) => updateClaimsCache(cache, data?.submitBoardCandidateClaim),
          })
          if (!result.data?.submitBoardCandidateClaim?.ok) {
            throw new Error(result.data?.submitBoardCandidateClaim?.message ?? 'Submit failed.')
          }
          break
        case 'discard':
          result = await discardClaim({
            variables: { input: { key: claim.key, year: Number.parseInt(year) } },
            update: (cache, { data }) => updateClaimsCache(cache, data?.discardBoardCandidateClaim),
          })
          if (!result.data?.discardBoardCandidateClaim?.ok) {
            throw new Error(result.data?.discardBoardCandidateClaim?.message ?? 'Discard failed.')
          }
          break
        case 'withdraw':
          result = await withdrawClaim({
            variables: {
              input: { key: claim.key, withdrawnReason: reason ?? '', year: Number.parseInt(year) },
            },
            update: (cache, { data }) =>
              updateClaimsCache(cache, data?.withdrawBoardCandidateClaim),
          })
          if (!result.data?.withdrawBoardCandidateClaim?.ok) {
            throw new Error(result.data?.withdrawBoardCandidateClaim?.message ?? 'Withdraw failed.')
          }
          break
      }
      addToast({
        title: 'Success',
        description: SUCCESS_MESSAGES[confirmAction!],
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'success',
      })

      resetConfirm()
      router.push(`/board/${year}/candidates/${login}/claims`)
    } catch (error) {
      addToast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Claim action failed.',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
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
            label: 'Edit Claim',
            onAction: () =>
              router.push(`/board/${year}/candidates/${login}/claims/${claim.key}/edit`),
          },
        ]
      : []),
    ...(ACTIONS_BY_STATUS[claim.status] ?? []).map((key) => ({
      key,
      label: `${upperFirst(key)} Claim`,
      onAction: ACTION_HANDLERS[key],
    })),
  ]

  return (
    <>
      {options.length > 0 && <DropdownActions options={options} />}
      <Modal
        isOpen={!!confirmAction}
        onClose={() => {
          resetConfirm()
        }}
      >
        <ModalContent>
          <ModalHeader className="flex flex-col gap-1">
            {upperFirst(confirmAction ?? '')} Claim
          </ModalHeader>
          <ModalBody>
            <p>
              Are you sure you want to {confirmAction} this claim? This action cannot be undone.
            </p>
          </ModalBody>
          {confirmAction == 'withdraw' && (
            <ModalBody>
              <textarea
                className="mt-2 w-full rounded border p-2"
                rows={3}
                placeholder="Reason for withdrawal..."
                value={reason ?? ''}
                onChange={(e) => setReason(e.target.value)}
              />
            </ModalBody>
          )}
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
              onPress={handleConfirm}
              isLoading={isLoading}
              disabled={isLoading}
              className="text-white"
            >
              {upperFirst(confirmAction ?? '')}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default ClaimActions
