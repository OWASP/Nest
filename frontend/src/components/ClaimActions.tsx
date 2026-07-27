'use client'

import { ApolloCache } from '@apollo/client'
import { useMutation } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/modal'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
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
import { ClaimStatusEnum, ReviewStatusEnum } from 'types/__generated__/graphql'
import { CreateBoardCandidateClaimReviewDocument } from 'types/__generated__/reviewMutations.generated'
import type { CreateBoardCandidateClaimReviewMutation } from 'types/__generated__/reviewMutations.generated'
import { GetClaimsAndReviewsDocument } from 'types/__generated__/reviewQueries.generated'
import type { Claim } from 'types/claim'
import DropdownActions from 'components/DropdownActions'

interface ClaimActionsProps {
  claim: { key: string; status: ClaimStatusEnum }
  hasReviewed: boolean
  isReviewer: boolean | undefined
  login: string
  year: string
}

type ClaimAction = 'submit' | 'discard' | 'withdraw' | 'approve' | 'reject'

const ACTIONS_BY_STATUS: Record<ClaimStatusEnum, ClaimAction[]> = {
  DRAFT: ['submit', 'discard'],
  SUBMITTED: ['withdraw'],
  APPROVED: ['withdraw'],
  REJECTED: [],
  DISCARDED: [],
  WITHDRAWN: [],
}

const ClaimActions: React.FC<ClaimActionsProps> = ({
  claim,
  hasReviewed,
  isReviewer,
  login,
  year,
}) => {
  const router = useRouter()
  const { session } = useDjangoSession()
  const sessionLogin = session?.user?.login ?? ''
  const [confirmAction, setConfirmAction] = useState<ClaimAction | null>(null)
  const [reason, setReason] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [submitClaim] = useMutation(SubmitBoardCandidateClaimDocument)
  const [discardClaim] = useMutation(DiscardBoardCandidateClaimDocument)
  const [withdrawClaim] = useMutation(WithdrawBoardCandidateClaimDocument)
  const [createReview] = useMutation(CreateBoardCandidateClaimReviewDocument)

  const updateClaimsCache = (
    cache: ApolloCache,
    mutationData: { claim?: Claim | null } | null | undefined
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

  const updateReviewsCache = (
    cache: ApolloCache,
    mutationData:
      | CreateBoardCandidateClaimReviewMutation['createBoardCandidateClaimReview']
      | null
      | undefined
  ) => {
    const newReview = mutationData?.review
    if (!newReview || !sessionLogin) return

    const existing = cache.readQuery({
      query: GetClaimsAndReviewsDocument,
      variables: { sessionLogin, year: Number.parseInt(year) },
    })

    if (existing) {
      cache.writeQuery({
        query: GetClaimsAndReviewsDocument,
        variables: { sessionLogin, year: Number.parseInt(year) },
        data: {
          ...existing,
          boardCandidateClaims: existing.boardCandidateClaims.map((c) =>
            c.key === claim.key
              ? {
                  ...c,
                  reviews: [
                    ...c.reviews,
                    {
                      __typename: 'BoardCandidateClaimReviewNode' as const,
                      id: newReview.id,
                      createdAt: newReview.createdAt,
                      status: newReview.status,
                      reviewer: { __typename: 'UserNode' as const, login: sessionLogin },
                    },
                  ],
                }
              : c
          ),
        },
      })
    }
  }

  const ACTION_HANDLERS: Record<ClaimAction, () => void> = {
    submit: () => setConfirmAction('submit'),
    discard: () => setConfirmAction('discard'),
    withdraw: () => setConfirmAction('withdraw'),
    approve: () => setConfirmAction('approve'),
    reject: () => setConfirmAction('reject'),
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
      approve: 'Claim approved successfully.',
      reject: 'Claim rejected successfully.',
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
        case 'approve':
        case 'reject':
          result = await createReview({
            variables: {
              input: {
                claimKey: claim.key,
                claimMemberLogin: login,
                notes: reason ?? '',
                status:
                  confirmAction === 'approve'
                    ? ReviewStatusEnum.Approved
                    : ReviewStatusEnum.Rejected,
                year: Number.parseInt(year),
              },
            },
            update: (cache, { data }) =>
              updateReviewsCache(cache, data?.createBoardCandidateClaimReview),
          })
          if (!result.data?.createBoardCandidateClaimReview?.ok) {
            throw new Error(
              result.data?.createBoardCandidateClaimReview?.message ??
                `${upperFirst(confirmAction)} failed.`
            )
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
      if (confirmAction === 'approve' || confirmAction === 'reject') {
        router.push(`/board/${year}/review`)
      } else {
        router.push(`/board/${year}/candidates/${login}/claims`)
      }
    } catch (error) {
      addToast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Claim action failed.',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
      })
      resetConfirm()
    } finally {
      setIsLoading(false)
    }
  }

  const options = [
    ...(claim.status == ClaimStatusEnum.Draft
      ? [
          {
            key: 'edit',
            label: 'Edit Claim',
            onAction: () =>
              router.push(`/board/${year}/candidates/${login}/claims/${claim.key}/edit`),
          },
        ]
      : []),
    ...(!isReviewer
      ? (ACTIONS_BY_STATUS[claim.status] ?? []).map((key) => ({
          key,
          label: `${upperFirst(key)} Claim`,
          onAction: ACTION_HANDLERS[key],
        }))
      : []),
    ...(isReviewer && !hasReviewed && claim.status === ClaimStatusEnum.Submitted
      ? [
          {
            key: 'approve',
            label: 'Approve Claim',
            onAction: ACTION_HANDLERS['approve'],
          },
          {
            key: 'reject',
            label: 'Reject Claim',
            onAction: ACTION_HANDLERS['reject'],
          },
        ]
      : []),
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
          {['withdraw', 'approve', 'reject'].includes(confirmAction ?? '') && (
            <ModalBody>
              <textarea
                aria-label={confirmAction === 'withdraw' ? 'Reason for withdrawal' : 'Notes'}
                className="mt-2 w-full rounded border p-2"
                rows={3}
                placeholder={confirmAction === 'withdraw' ? 'Reason for withdrawal...' : 'Notes...'}
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
