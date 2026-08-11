'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Modal, ModalBody, ModalContent, ModalFooter, ModalHeader } from '@heroui/modal'
import { addToast } from '@heroui/toast'
import Link from 'next/link'
import { useSession } from 'next-auth/react'
import { useCallback, useMemo, useState } from 'react'
import { FaBell, FaCheck, FaPlus } from 'react-icons/fa6'

import {
  CREATE_SNAPSHOT_SUBSCRIPTION,
  GET_MY_SNAPSHOT_SUBSCRIPTIONS,
  UPDATE_SNAPSHOT_SUBSCRIPTION,
} from 'server/queries/subscriptionQueries'
import { decodeRelayId } from 'utils/decodeRelayId'
import ActionButton from 'components/ActionButton'

const MAX_SUBSCRIPTIONS = 5

interface SubscribedEntity {
  id: number
  name: string
}

interface SnapshotSubscriptionData {
  id: string
  name: string
  frequency: string
  isActive: boolean
  subscribedProjects: SubscribedEntity[]
  subscribedChapters: SubscribedEntity[]
  subscribedCommittees: SubscribedEntity[]
}

interface SubscribeButtonProps {
  entityType: 'project' | 'chapter' | 'committee'
  entityId: string
  entityName: string
}

const M2M_FIELD_MAP = {
  project: 'subscribedProjects',
  chapter: 'subscribedChapters',
  committee: 'subscribedCommittees',
} as const

const M2M_INPUT_MAP = {
  project: 'subscribedProjectIds',
  chapter: 'subscribedChapterIds',
  committee: 'subscribedCommitteeIds',
} as const

export default function SubscribeButton({
  entityType,
  entityId,
  entityName,
}: Readonly<SubscribeButtonProps>) {
  const { status } = useSession()
  const [showModal, setShowModal] = useState(false)
  const [modalView, setModalView] = useState<'list' | 'create'>('list')
  const [selectedSubId, setSelectedSubId] = useState<string | null>(null)
  const [newName, setNewName] = useState('')
  const [newFrequency, setNewFrequency] = useState<'weekly' | 'monthly'>('weekly')

  const { data, refetch } = useQuery<{
    mySnapshotSubscriptions: SnapshotSubscriptionData[]
  }>(GET_MY_SNAPSHOT_SUBSCRIPTIONS, {
    skip: status !== 'authenticated',
    errorPolicy: 'all',
  })

  const subscriptions = useMemo(
    () => data?.mySnapshotSubscriptions ?? [],
    [data?.mySnapshotSubscriptions]
  )
  const activeSubscriptions = subscriptions.filter((s) => s.isActive)
  const decodedEntityId = decodeRelayId(entityId)

  // Check if entity is already in any subscription
  const m2mField = M2M_FIELD_MAP[entityType]
  const subscribedSub = activeSubscriptions.find((sub) => {
    const entities = sub[m2mField] as SubscribedEntity[]
    return entities.some((e) => e.id === decodedEntityId)
  })
  const isSubscribed = subscribedSub != null

  // Add entity to existing subscription
  const [updateSubscription, { loading: updating }] = useMutation<{
    updateSnapshotSubscription: { ok: boolean; message: string }
  }>(UPDATE_SNAPSHOT_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.updateSnapshotSubscription
      if (result.ok) {
        addToast({
          title: 'Added!',
          description: `${entityName} added to subscription.`,
          color: 'success',
        })
        setShowModal(false)
        refetch()
      } else {
        addToast({ title: 'Error', description: result.message, color: 'danger' })
      }
    },
    onError: () => {
      addToast({ title: 'Error', description: 'Failed to update subscription.', color: 'danger' })
    },
  })

  // Create new subscription with this entity
  const [createSubscription, { loading: creating }] = useMutation<{
    createSnapshotSubscription: { ok: boolean; message: string }
  }>(CREATE_SNAPSHOT_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.createSnapshotSubscription
      if (result.ok) {
        addToast({
          title: 'Subscribed!',
          description: `Created subscription with ${entityName}.`,
          color: 'success',
        })
        setShowModal(false)
        setNewName('')
        setNewFrequency('weekly')
        refetch()
      } else {
        addToast({ title: 'Error', description: result.message, color: 'danger' })
      }
    },
    onError: () => {
      addToast({
        title: 'Error',
        description: 'Failed to create subscription.',
        color: 'danger',
      })
    },
  })

  const handleAddToExisting = useCallback(() => {
    if (!selectedSubId) return

    const sub = subscriptions.find((s) => s.id === selectedSubId)
    if (!sub) return

    const existingIds = (sub[m2mField] as SubscribedEntity[]).map((e) => e.id)
    const inputField = M2M_INPUT_MAP[entityType]

    updateSubscription({
      variables: {
        subscriptionId: decodeRelayId(selectedSubId),
        inputData: {
          [inputField]: [...existingIds, decodedEntityId],
        },
      },
    })
  }, [selectedSubId, subscriptions, m2mField, entityType, updateSubscription, decodedEntityId])

  const handleCreateNew = useCallback(() => {
    const inputField = M2M_INPUT_MAP[entityType]

    createSubscription({
      variables: {
        inputData: {
          name: newName || undefined,
          frequency: newFrequency,
          [inputField]: [decodedEntityId],
        },
      },
    })
  }, [createSubscription, entityType, decodedEntityId, newName, newFrequency])

  const openModal = () => {
    setShowModal(true)
    setSelectedSubId(null)
    setNewName('')
    setNewFrequency('weekly')
    setModalView(activeSubscriptions.length > 0 ? 'list' : 'create')
  }

  if (status !== 'authenticated') return null

  const renderButton = () => {
    if (isSubscribed) {
      return (
        <Link
          href="/settings"
          className="flex h-10 cursor-pointer items-center gap-1.5 rounded-md border border-green-500/40 bg-green-500/10 px-2 py-2 text-sm font-medium text-green-600 transition-all hover:bg-green-500/20 dark:text-green-400"
          aria-label={`Subscribed to ${entityName} — click to manage`}
        >
          <FaCheck className="h-3 w-3" />
          Subscribed
        </Link>
      )
    }

    return (
      <button
        type="button"
        onClick={openModal}
        className="flex h-10 cursor-pointer items-center gap-1.5 rounded-md border border-[#1D7BD7] px-2 py-2 text-sm font-medium text-[#1D7BD7] transition-all hover:bg-[#1D7BD7] hover:text-white"
        aria-label={`Subscribe to ${entityName}`}
      >
        <FaBell className="h-3 w-3" />
        Subscribe
      </button>
    )
  }

  const isBusy = updating || creating

  return (
    <>
      {renderButton()}

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} size="md">
        <ModalContent className="rounded-lg bg-white shadow-xl dark:border dark:border-gray-800 dark:bg-[#212529]">
          <ModalHeader className="border-b border-gray-200 px-5 py-4 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              Subscribe to {entityName}
            </h2>
          </ModalHeader>

          <ModalBody className="space-y-4 px-5 py-4">
            {modalView === 'list' && (
              <>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Choose a subscription to add this {entityType} to:
                </p>

                <div className="flex flex-col gap-3">
                  {activeSubscriptions.map((sub) => {
                    const alreadyHasEntity = (sub[m2mField] as SubscribedEntity[]).some(
                      (e) => e.id === decodedEntityId
                    )

                    let buttonClasses =
                      'border-gray-200 text-gray-700 hover:border-gray-300 dark:border-gray-700 dark:text-gray-300 dark:hover:border-gray-600'
                    if (alreadyHasEntity) {
                      buttonClasses =
                        'cursor-not-allowed border-gray-200 bg-gray-50 text-gray-400 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-500'
                    } else if (selectedSubId === sub.id) {
                      buttonClasses = 'border-[#1D7BD7] bg-[#1D7BD7]/5 text-[#1D7BD7]'
                    }

                    return (
                      <button
                        key={sub.id}
                        type="button"
                        disabled={alreadyHasEntity}
                        onClick={() => setSelectedSubId(sub.id)}
                        className={`flex w-full cursor-pointer items-center justify-between rounded-md border px-4 py-3 text-left text-sm transition-all ${buttonClasses}`}
                      >
                        <div>
                          <span className="font-medium">{sub.name || 'Unnamed Subscription'}</span>
                          <span className="ml-2 text-xs text-gray-400">
                            {sub.frequency.charAt(0).toUpperCase() + sub.frequency.slice(1)}
                          </span>
                        </div>
                        {alreadyHasEntity && (
                          <span className="text-xs text-gray-400">Already added</span>
                        )}
                        {selectedSubId === sub.id && !alreadyHasEntity && (
                          <FaCheck className="h-3 w-3 text-[#1D7BD7]" />
                        )}
                      </button>
                    )
                  })}
                </div>

                {activeSubscriptions.length < MAX_SUBSCRIPTIONS && (
                  <button
                    type="button"
                    onClick={() => setModalView('create')}
                    className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-md border-2 border-dashed border-gray-300 px-4 py-3 text-sm font-medium text-gray-500 transition-all hover:border-[#1D7BD7] hover:text-[#1D7BD7] dark:border-gray-700 dark:text-gray-400"
                  >
                    <FaPlus className="h-3 w-3" />
                    Create New Subscription
                  </button>
                )}
              </>
            )}

            {modalView === 'create' && (
              <>
                {activeSubscriptions.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setModalView('list')}
                    className="cursor-pointer text-sm text-[#1D7BD7] hover:underline"
                  >
                    ← Back to existing subscriptions
                  </button>
                )}

                <div>
                  <h3 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">
                    Name
                  </h3>
                  <input
                    type="text"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="e.g., My Weekly Digest"
                    className="w-full rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-800 transition-colors outline-none focus:border-[#1D7BD7] dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>

                <div>
                  <h3 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">
                    Frequency
                  </h3>
                  <div className="inline-flex rounded-lg border border-gray-200 p-0.5 dark:border-gray-700">
                    {(['weekly', 'monthly'] as const).map((option) => (
                      <button
                        key={option}
                        type="button"
                        onClick={() => setNewFrequency(option)}
                        aria-pressed={newFrequency === option}
                        className={`rounded-md px-3 py-1 text-sm font-medium transition-all ${
                          newFrequency === option
                            ? 'bg-[#1D7BD7] text-white shadow-sm'
                            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                        }`}
                      >
                        {option.charAt(0).toUpperCase() + option.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
          </ModalBody>

          <ModalFooter className="flex justify-end gap-3 border-t border-gray-200 px-5 py-4 dark:border-gray-700">
            <ActionButton onClick={() => setShowModal(false)}>Cancel</ActionButton>
            {modalView === 'list' ? (
              <ActionButton onClick={handleAddToExisting} isDisabled={!selectedSubId || isBusy}>
                <FaBell className="h-3 w-3" />
                {updating ? 'Adding...' : 'Add to Subscription'}
              </ActionButton>
            ) : (
              <ActionButton onClick={handleCreateNew} isDisabled={isBusy}>
                <FaBell className="h-3 w-3" />
                {creating ? 'Creating...' : 'Create & Subscribe'}
              </ActionButton>
            )}
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}
