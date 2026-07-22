'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import type { DragEndEvent } from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Button } from '@heroui/button'
import { Chip, Tooltip } from '@heroui/react'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams, useRouter } from 'next/navigation'
import React, { useCallback, useEffect, useState } from 'react'
import { FaGripVertical, FaPlus } from 'react-icons/fa6'
import { handleAppError } from 'app/global-error'
import { ReorderBoardCandidateClaimsDocument } from 'types/__generated__/claimMutations.generated'
import {
  GetBoardCandidateAndClaimsDocument,
  type GetBoardCandidateAndClaimsQuery,
} from 'types/__generated__/claimQueries.generated'
import { ClaimStatusEnum } from 'types/__generated__/graphql'
import { formatDate } from 'utils/dateFormatter'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import ActionButton from 'components/ActionButton'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

type Claim = NonNullable<GetBoardCandidateAndClaimsQuery['boardCandidateClaims']>[number]

const ClaimItem = ({
  claim,
  onClick,
  dragHandleProps,
}: {
  claim: Claim
  onClick: (key: string) => void
  dragHandleProps?: React.HTMLAttributes<HTMLDivElement>
}) => {
  const dragListeners = dragHandleProps as React.HTMLAttributes<HTMLDivElement>

  return (
    <Button
      disableAnimation
      onPress={() => onClick(claim.key)}
      className="h-24 w-full flex-row justify-between bg-transparent dark:hover:bg-gray-900"
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
      {dragHandleProps && (
        <div className="flex flex-row gap-2 pl-2">
          <div
            {...dragHandleProps}
            className="cursor-grab touch-none rounded p-2 hover:bg-gray-200 dark:hover:bg-gray-700"
            aria-label="Drag to reorder"
            onPointerDown={(e) => {
              e.stopPropagation()
              dragListeners?.onPointerDown?.(e)
            }}
          >
            <FaGripVertical className="text-gray-400 dark:text-gray-500" size={24} />
          </div>
        </div>
      )}
    </Button>
  )
}

const SortableClaimItem = ({
  claim,
  onClick,
}: {
  claim: Claim
  onClick: (key: string) => void
}) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: claim.key,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    position: 'relative' as const,
    zIndex: isDragging ? 1 : 0,
  }

  return (
    <div ref={setNodeRef} style={style} className="w-full min-w-0">
      <ClaimItem
        claim={claim}
        onClick={onClick}
        dragHandleProps={{ ...attributes, ...listeners }}
      />
    </div>
  )
}

const CandidateClaimsPage = () => {
  const router = useRouter()
  const { isSyncing, session } = useDjangoSession()
  const { login, year } = useParams<{ login: string; year: string }>()
  const [approvedOrder, setApprovedOrder] = useState<string[]>([])
  const [isSaving, setIsSaving] = useState(false)
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

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  useEffect(() => {
    const c = graphQLData?.boardCandidateClaims ?? []
    setApprovedOrder(
      c.filter((claim) => claim.status === ClaimStatusEnum.Approved).map((claim) => claim.key)
    )
  }, [graphQLData])

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError])

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event
      if (!over || active.id === over.id) return
      if (isSaving) return

      const previousOrder = [...approvedOrder]
      const oldIndex = approvedOrder.indexOf(String(active.id))
      const newIndex = approvedOrder.indexOf(String(over.id))

      if (oldIndex === -1 || newIndex === -1) return

      const newOrder = arrayMove(approvedOrder, oldIndex, newIndex)
      setApprovedOrder(newOrder)
      setIsSaving(true)

      reorderClaims({
        variables: { input: { keys: newOrder, year: Number.parseInt(year) } },
        update(cache, { data }) {
          const reorderedClaims = data?.reorderBoardCandidateClaims?.claims
          if (!reorderedClaims) return
          const existing = cache.readQuery({
            query: GetBoardCandidateAndClaimsDocument,
            variables: { login, year: Number.parseInt(year) },
          })
          if (existing) {
            cache.writeQuery({
              query: GetBoardCandidateAndClaimsDocument,
              variables: { login, year: Number.parseInt(year) },
              data: {
                ...existing,
                boardCandidateClaims: [
                  ...existing.boardCandidateClaims.filter(
                    (c) => c.status !== ClaimStatusEnum.Approved
                  ),
                  ...reorderedClaims,
                ],
              },
            })
          }
        },
      })
        .then(({ data }) => {
          if (data?.reorderBoardCandidateClaims?.ok) {
            addToast({
              title: 'Success',
              description: 'Claim order updated.',
              timeout: 3000,
              shouldShowTimeoutProgress: true,
              color: 'success',
            })
          } else {
            setApprovedOrder(previousOrder)
            addToast({
              title: 'Error',
              description: 'Failed to update claim order.',
              timeout: 3000,
              shouldShowTimeoutProgress: true,
              color: 'danger',
            })
          }
        })
        .catch(() => {
          setApprovedOrder(previousOrder)
          addToast({
            title: 'Error',
            description: 'Failed to update claim order.',
            timeout: 3000,
            shouldShowTimeoutProgress: true,
            color: 'danger',
          })
        })
        .finally(() => {
          setIsSaving(false)
        })
    },
    [approvedOrder, isSaving, reorderClaims, login, year]
  )

  if (isSyncing || isLoading) {
    return <LoadingSpinner />
  }

  if (!isCandidate || session?.user?.login !== login) {
    return (
      <AccessDeniedDisplay title="Access Denied" message="You can only view your own claims." />
    )
  }

  const handleCreate = () => router.push(`/board/${year}/candidates/${login}/claims/create`)
  const handleClaimClick = (key: string) =>
    router.push(`/board/${year}/candidates/${login}/claims/${key}`)

  const sectionConfig = [
    {
      type: ClaimStatusEnum.Draft,
      title: 'Draft Claims',
      items: claims.filter((c) => c.status === ClaimStatusEnum.Draft),
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

  return (
    <div className="container mx-auto px-4 py-8 dark:bg-[#212529]">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-600 dark:text-white">Your Claims</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">@{login}</p>
        </div>
        <ActionButton onClick={handleCreate}>
          <FaPlus className="mr-2" />
          {'Create Claim'}
        </ActionButton>
      </div>
      {sectionConfig.map(({ type: statusType, title, items }) => (
        <SecondaryCard key={title} title={title}>
          {items.length == 0 ? (
            <p> No {title.toLowerCase()}. </p>
          ) : (
            <div className="grid gap-2">
              {statusType === ClaimStatusEnum.Approved && items.length > 1 ? (
                <DndContext
                  sensors={sensors}
                  collisionDetection={closestCenter}
                  onDragEnd={handleDragEnd}
                >
                  <SortableContext items={approvedOrder} strategy={verticalListSortingStrategy}>
                    {items.map((claim) => (
                      <SortableClaimItem key={claim.key} claim={claim} onClick={handleClaimClick} />
                    ))}
                  </SortableContext>
                </DndContext>
              ) : (
                items.map((claim) => (
                  <ClaimItem key={claim.key} claim={claim} onClick={handleClaimClick} />
                ))
              )}
            </div>
          )}
        </SecondaryCard>
      ))}
    </div>
  )
}

export default CandidateClaimsPage
