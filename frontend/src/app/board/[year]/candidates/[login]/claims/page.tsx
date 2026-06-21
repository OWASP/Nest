'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { FaChevronUp, FaChevronDown } from 'react-icons/fa'
import { FaPlus } from 'react-icons/fa6'
import { handleAppError } from 'app/global-error'
import { GetBoardCandidateDocument } from 'types/__generated__/boardQueries.generated'
import { ReorderBoardCandidateClaimsDocument } from 'types/__generated__/claimMutations.generated'
import { GetBoardCandidateClaimsDocument } from 'types/__generated__/claimQueries.generated'
import { formatDate } from 'utils/dateFormatter'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import ActionButton from 'components/ActionButton'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const CandidateClaimsPage = () => {
  const router = useRouter()
  const { isSyncing, session } = useDjangoSession()
  const { login, year } = useParams<{ login: string; year: string }>()
  const [draftOrder, setDraftOrder] = useState<string[]>([])
  const [approvedOrder, setApprovedOrder] = useState<string[]>([])
  const [reorderClaims] = useMutation(ReorderBoardCandidateClaimsDocument)

  const {
    data: graphQLData,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetBoardCandidateClaimsDocument, {
    skip: !login || !year,
    variables: { login: login, year: Number.parseInt(year) },
  })

  const { data: candidateGraphQLData, loading: isCandidateLoading } = useQuery(
    GetBoardCandidateDocument,
    {
      variables: { login: login, year: Number.parseInt(year) },
    }
  )

  const isCandidate = candidateGraphQLData?.boardOfDirectors?.candidate != null
  const claims = graphQLData?.boardCandidateClaims ?? []

  useEffect(() => {
    const c = graphQLData?.boardCandidateClaims ?? []
    setDraftOrder(c.filter((claim) => claim.status === 'DRAFT').map((claim) => claim.key))
    setApprovedOrder(c.filter((claim) => claim.status === 'APPROVED').map((claim) => claim.key))
  }, [graphQLData])

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError])

  if (isSyncing || isLoading || isCandidateLoading) {
    return <LoadingSpinner />
  }

  if (!isCandidate || session?.user?.login !== login) {
    return (
      <AccessDeniedDisplay title="Access Denied" message="You can only view your own claims." />
    )
  }

  const originalDraftOrder = claims.filter((c) => c.status === 'DRAFT').map((c) => c.key)
  const originalApprovedOrder = claims.filter((c) => c.status === 'APPROVED').map((c) => c.key)

  const draftChanged = draftOrder.join() !== originalDraftOrder.join()
  const approvedChanged = approvedOrder.join() !== originalApprovedOrder.join()

  const handleReorder = (key: string, direction: 'up' | 'down', status: 'DRAFT' | 'APPROVED') => {
    const setOrder = status === 'DRAFT' ? setDraftOrder : setApprovedOrder
    setOrder((prev) => {
      const idx = prev.indexOf(key)
      const swapIdx = direction === 'up' ? idx - 1 : idx + 1
      if (swapIdx < 0 || swapIdx >= prev.length) return prev
      const next = [...prev]
      ;[next[idx], next[swapIdx]] = [next[swapIdx], next[idx]]
      return next
    })
  }

  const handleSave = async (status: string) => {
    const keys = status === 'DRAFT' ? draftOrder : approvedOrder
    try {
      await reorderClaims({
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
      addToast({ title: 'Success', description: 'Claim order updated.', color: 'success' })
    } catch {
      addToast({ title: 'Error', description: 'Failed to update claim order.', color: 'danger' })
    }
  }

  const handleCreate = () => router.push(`/board/${year}/candidates/${login}/claims/create`)
  const handleClaimClick = (key: string) =>
    router.push(`/board/${year}/candidates/${login}/claims/${key}`)

  const sectionConfig = [
    {
      type: 'DRAFT',
      title: 'Draft Claims',
      items: [...claims.filter((c) => c.status === 'DRAFT')].sort(
        (a, b) => draftOrder.indexOf(a.key) - draftOrder.indexOf(b.key)
      ),
    },
    {
      type: 'SUBMITTED',
      title: 'Submitted Claims',
      items: claims.filter((c) => c.status === 'SUBMITTED'),
    },
    {
      type: 'APPROVED',
      title: 'Approved Claims',
      items: [...claims.filter((c) => c.status === 'APPROVED')].sort(
        (a, b) => approvedOrder.indexOf(a.key) - approvedOrder.indexOf(b.key)
      ),
    },
    {
      type: 'REJECTED',
      title: 'Rejected Claims',
      items: claims.filter((c) => c.status === 'REJECTED'),
    },
    {
      type: 'WITHDRAWN',
      title: 'Withdrawn Claims',
      items: claims.filter((c) => c.status === 'WITHDRAWN'),
    },
  ]
  const orderChanged: Record<string, boolean> = { DRAFT: draftChanged, APPROVED: approvedChanged }

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
            ['DRAFT', 'APPROVED'].includes(statusType) && orderChanged[statusType] ? (
              <div className="flex w-full items-center justify-between">
                <span>{title}</span>
                <ActionButton onClick={() => handleSave(statusType)}>Save Order</ActionButton>
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
                    <span className="mt-1 shrink-0 text-xs text-gray-600 dark:text-gray-400">
                      {formatDate(claim.createdAt)}
                    </span>
                  </div>
                  {['DRAFT', 'APPROVED'].includes(claim.status) && (
                    <div className="flex flex-row gap-2 p-1">
                      <div
                        className="rounded p-2 hover:bg-gray-200 dark:hover:bg-gray-700"
                        role="button"
                        tabIndex={0}
                        onClick={(e) => {
                          e.stopPropagation()
                          handleReorder(claim.key, 'up', claim.status as 'DRAFT' | 'APPROVED')
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.stopPropagation()
                            handleReorder(claim.key, 'up', claim.status as 'DRAFT' | 'APPROVED')
                          }
                        }}
                      >
                        <FaChevronUp className="text-gray-400 dark:text-gray-500" size={24} />
                      </div>
                      <div
                        className="rounded p-2 hover:bg-gray-200 dark:hover:bg-gray-700"
                        role="button"
                        tabIndex={0}
                        onClick={(e) => {
                          e.stopPropagation()
                          handleReorder(claim.key, 'down', claim.status as 'DRAFT' | 'APPROVED')
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.stopPropagation()
                            handleReorder(claim.key, 'down', claim.status as 'DRAFT' | 'APPROVED')
                          }
                        }}
                      >
                        <FaChevronDown className="text-gray-400 dark:text-gray-500" size={24} />
                      </div>
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
