'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Chip, Tooltip } from '@heroui/react'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { FaChevronUp, FaChevronDown } from 'react-icons/fa'
import { FaPlus } from 'react-icons/fa6'
import { handleAppError } from 'app/global-error'
import { ReorderBoardCandidateClaimsDocument } from 'types/__generated__/claimMutations.generated'
import {
  GetBoardCandidateAndClaimsDocument,
  GetBoardCandidateClaimsDocument,
} from 'types/__generated__/claimQueries.generated'
import { ClaimStatusEnum } from 'types/__generated__/graphql'
import { formatDate } from 'utils/dateFormatter'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import ActionButton from 'components/ActionButton'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const ReorderButton = ({
  direction,
  claimKey,
  status,
  onReorder,
}: {
  direction: 'up' | 'down'
  claimKey: string
  status: ClaimStatusEnum.Draft | ClaimStatusEnum.Approved
  onReorder: (
    key: string,
    direction: 'up' | 'down',
    status: ClaimStatusEnum.Draft | ClaimStatusEnum.Approved
  ) => void
}) => {
  const Icon = direction === 'up' ? FaChevronUp : FaChevronDown
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onReorder(claimKey, direction, status)
  }
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.stopPropagation()
      onReorder(claimKey, direction, status)
    }
  }
  return (
    <div
      className="rounded p-2 hover:bg-gray-200 dark:hover:bg-gray-700"
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
    >
      <Icon className="text-gray-400 dark:text-gray-500" size={24} />
    </div>
  )
}

const CandidateClaimsPage = () => {
  const router = useRouter()
  const { isSyncing, session } = useDjangoSession()
  const { login, year } = useParams<{ login: string; year: string }>()
  const [draftOrder, setDraftOrder] = useState<string[]>([])
  const [approvedOrder, setApprovedOrder] = useState<string[]>([])
  const [reorderClaims] = useMutation(ReorderBoardCandidateClaimsDocument)

  const {
    data: graphQLData,
    loading: isLoading,
    error: graphQLRequestError,
  } = useQuery(GetBoardCandidateAndClaimsDocument, {
    skip: !login || !year || session?.user?.login !== login,
    variables: { login, year: Number.parseInt(year) },
  })

  const isCandidate = graphQLData?.boardOfDirectors?.candidate != null
  const claims = graphQLData?.boardCandidateClaims ?? []

  useEffect(() => {
    const c = graphQLData?.boardCandidateClaims ?? []
    setDraftOrder(
      c.filter((claim) => claim.status === ClaimStatusEnum.Draft).map((claim) => claim.key)
    )
    setApprovedOrder(
      c.filter((claim) => claim.status === ClaimStatusEnum.Approved).map((claim) => claim.key)
    )
  }, [graphQLData])

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError])

  if (isSyncing || isLoading) {
    return <LoadingSpinner />
  }

  if (!isCandidate || session?.user?.login !== login) {
    return (
      <AccessDeniedDisplay title="Access Denied" message="You can only view your own claims." />
    )
  }

  const originalDraftOrder = claims
    .filter((c) => c.status === ClaimStatusEnum.Draft)
    .map((c) => c.key)
  const originalApprovedOrder = claims
    .filter((c) => c.status === ClaimStatusEnum.Approved)
    .map((c) => c.key)

  const draftChanged = draftOrder.join() !== originalDraftOrder.join()
  const approvedChanged = approvedOrder.join() !== originalApprovedOrder.join()

  const handleReorder = (
    key: string,
    direction: 'up' | 'down',
    status: ClaimStatusEnum.Draft | ClaimStatusEnum.Approved
  ) => {
    const setOrder = status === ClaimStatusEnum.Draft ? setDraftOrder : setApprovedOrder
    setOrder((prev) => {
      const idx = prev.indexOf(key)
      if (idx === -1) return prev
      const swapIdx = direction === 'up' ? idx - 1 : idx + 1
      if (swapIdx < 0 || swapIdx >= prev.length) return prev
      const next = [...prev]
      ;[next[idx], next[swapIdx]] = [next[swapIdx], next[idx]]
      return next
    })
  }

  const handleSave = async (status: ClaimStatusEnum.Draft | ClaimStatusEnum.Approved) => {
    const keys = status === ClaimStatusEnum.Draft ? draftOrder : approvedOrder
    try {
      const { data } = await reorderClaims({
        variables: { input: { keys, year: Number.parseInt(year) } },
        update(cache, { data }) {
          const reorderedClaims = data?.reorderBoardCandidateClaims?.claims
          if (!reorderedClaims) return
          const existing = cache.readQuery({
            query: GetBoardCandidateClaimsDocument,
            variables: { login, year: Number.parseInt(year) },
          })
          if (existing) {
            cache.writeQuery({
              query: GetBoardCandidateClaimsDocument,
              variables: { login, year: Number.parseInt(year) },
              data: {
                boardCandidateClaims: [
                  ...existing.boardCandidateClaims.filter((c) => c.status !== status),
                  ...reorderedClaims,
                ],
              },
            })
          }
        },
      })
      if (data?.reorderBoardCandidateClaims?.ok) {
        addToast({
          title: 'Success',
          description: 'Claim order updated.',
          timeout: 3000,
          shouldShowTimeoutProgress: true,
          color: 'success',
        })
      } else {
        addToast({
          title: 'Error',
          description: 'Failed to update claim order.',
          timeout: 3000,
          shouldShowTimeoutProgress: true,
          color: 'danger',
        })
      }
    } catch {
      addToast({
        title: 'Error',
        description: 'Failed to update claim order.',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
      })
    }
  }

  const handleCreate = () => router.push(`/board/${year}/candidates/${login}/claims/create`)
  const handleClaimClick = (key: string) =>
    router.push(`/board/${year}/candidates/${login}/claims/${key}`)

  const sectionConfig = [
    {
      type: ClaimStatusEnum.Draft,
      title: 'Draft Claims',
      items: [...claims.filter((c) => c.status === ClaimStatusEnum.Draft)].sort(
        (a, b) => draftOrder.indexOf(a.key) - draftOrder.indexOf(b.key)
      ),
    },
    {
      type: ClaimStatusEnum.Submitted,
      title: 'Submitted Claims',
      items: claims.filter((c) => c.status === ClaimStatusEnum.Submitted),
    },
    {
      type: ClaimStatusEnum.Approved,
      title: 'Approved Claims',
      items: [...claims.filter((c) => c.status === ClaimStatusEnum.Approved)].sort(
        (a, b) => approvedOrder.indexOf(a.key) - approvedOrder.indexOf(b.key)
      ),
    },
    {
      type: ClaimStatusEnum.Rejected,
      title: 'Rejected Claims',
      items: claims.filter((c) => c.status === ClaimStatusEnum.Rejected),
    },
    {
      type: ClaimStatusEnum.Withdrawn,
      title: 'Withdrawn Claims',
      items: claims.filter((c) => c.status === ClaimStatusEnum.Withdrawn),
    },
  ]
  const orderChanged: Partial<Record<ClaimStatusEnum, boolean>> = {
    [ClaimStatusEnum.Draft]: draftChanged,
    [ClaimStatusEnum.Approved]: approvedChanged,
  }

  return (
    <div className="container mx-auto px-4 py-8 dark:bg-[#212529]">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-600 dark:text-white">Claims</h1>
          <p className="text-gray-600 dark:text-gray-400">Claims you've created</p>
        </div>
        <ActionButton onClick={handleCreate}>
          <FaPlus className="mr-2" />
          {'Create Claim'}
        </ActionButton>
      </div>
      {sectionConfig.map(({ type: statusType, title, items }) => (
        <SecondaryCard
          key={title}
          title={
            [ClaimStatusEnum.Draft, ClaimStatusEnum.Approved].includes(statusType) &&
            orderChanged[statusType] ? (
              <div className="flex w-full items-center justify-between">
                <span>{title}</span>
                <ActionButton
                  onClick={() =>
                    handleSave(statusType as ClaimStatusEnum.Draft | ClaimStatusEnum.Approved)
                  }
                >
                  Save Order
                </ActionButton>
              </div>
            ) : (
              title
            )
          }
        >
          {items.length == 0 ? (
            <p> No {title.toLowerCase()}. </p>
          ) : (
            <div className="grid gap-2">
              {items.map((claim) => (
                <Button
                  disableAnimation
                  key={claim.key}
                  onPress={() => handleClaimClick(claim.key)}
                  className="h-24 flex-row justify-between bg-transparent dark:hover:bg-gray-900"
                >
                  <div className="flex min-w-0 flex-1 flex-col items-start justify-start p-1">
                    <h3 className="w-full min-w-0 truncate text-left text-xl leading-tight font-semibold dark:text-gray-300">
                      {claim.name}
                    </h3>
                    <p className="w-full min-w-0 truncate text-left leading-tight text-gray-600 dark:text-gray-300">
                      {claim.description}
                    </p>
                    <div className="mt-1 flex items-center gap-2">
                      <span className="shrink-0 text-xs text-gray-600 dark:text-gray-400">
                        {formatDate(claim.createdAt)}
                      </span>
                      {claim.hasEvidence && (
                        <Tooltip
                          content="This claim has an evidence attached"
                          delay={150}
                          closeDelay={100}
                          showArrow
                          placement="right"
                        >
                          <Chip size="sm" variant="flat" color="success" className="text-tiny h-5">
                            Evidence
                          </Chip>
                        </Tooltip>
                      )}
                    </div>
                  </div>
                  {[ClaimStatusEnum.Draft, ClaimStatusEnum.Approved].includes(claim.status) && (
                    <div className="flex flex-row gap-2 p-1">
                      <ReorderButton
                        direction="up"
                        claimKey={claim.key}
                        status={claim.status as ClaimStatusEnum.Draft | ClaimStatusEnum.Approved}
                        onReorder={handleReorder}
                      />
                      <ReorderButton
                        direction="down"
                        claimKey={claim.key}
                        status={claim.status as ClaimStatusEnum.Draft | ClaimStatusEnum.Approved}
                        onReorder={handleReorder}
                      />
                    </div>
                  )}
                </Button>
              ))}
            </div>
          )}
        </SecondaryCard>
      ))}
    </div>
  )
}

export default CandidateClaimsPage
