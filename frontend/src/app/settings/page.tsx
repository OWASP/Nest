'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/modal'
import { addToast } from '@heroui/toast'
import { useSearchParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useCallback, useEffect, useState } from 'react'
import { FaBell, FaBellSlash, FaFloppyDisk, FaTrash } from 'react-icons/fa6'

import {
  CANCEL_ENTITY_SUBSCRIPTION,
  CANCEL_SNAPSHOT_SUBSCRIPTION,
  CREATE_SNAPSHOT_SUBSCRIPTION,
  DELETE_ENTITY_SUBSCRIPTION,
  GET_MY_ENTITY_SUBSCRIPTIONS,
  GET_MY_SNAPSHOT_SUBSCRIPTION,
  REACTIVATE_ENTITY_SUBSCRIPTION,
  UPDATE_ENTITY_SUBSCRIPTION,
  UPDATE_SNAPSHOT_SUBSCRIPTION,
} from 'server/queries/subscriptionQueries'
import { decodeRelayId } from 'utils/decodeRelayId'

import ActionButton from 'components/ActionButton'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const MAX_ENTITY_SUBSCRIPTIONS = 5

const SNAPSHOT_CONTENT_FIELDS = [
  { key: 'includeChapters', label: 'Chapters' },
  { key: 'includeEvents', label: 'Events' },
  { key: 'includeIssues', label: 'Issues' },
  { key: 'includePosts', label: 'Posts' },
  { key: 'includeProjects', label: 'Projects' },
  { key: 'includePullRequests', label: 'Pull Requests' },
  { key: 'includeReleases', label: 'Releases' },
  { key: 'includeUsers', label: 'Users' },
] as const

type SnapshotContentKey = (typeof SNAPSHOT_CONTENT_FIELDS)[number]['key']

interface SnapshotSubscriptionData {
  id: string
  frequency: string
  isActive: boolean
  includeChapters: boolean
  includeEvents: boolean
  includeIssues: boolean
  includePosts: boolean
  includeProjects: boolean
  includePullRequests: boolean
  includeReleases: boolean
  includeUsers: boolean
  createdAt: string
  updatedAt: string
}

interface MutationResponse {
  ok: boolean
  message: string
  subscription?: unknown
}

const DEFAULT_SNAPSHOT_PREFERENCES: Record<SnapshotContentKey, boolean> = {
  includeChapters: true,
  includeEvents: true,
  includeIssues: true,
  includePosts: true,
  includeProjects: true,
  includePullRequests: true,
  includeReleases: true,
  includeUsers: true,
}

function ContentToggleGrid<K extends string>({
  fields,
  preferences,
  onToggle,
}: Readonly<{
  fields: readonly { key: K; label: string }[]
  preferences: Record<K, boolean>
  onToggle: (key: K) => void
}>) {
  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
      {fields.map(({ key, label }) => (
        <button
          key={key}
          type="button"
          onClick={() => onToggle(key)}
          aria-pressed={preferences[key]}
          className={`flex cursor-pointer items-center justify-between gap-2 rounded-md border px-3 py-2 text-sm font-medium transition-all ${
            preferences[key]
              ? 'border-[#1D7BD7]/40 bg-[#1D7BD7]/10 text-[#1D7BD7]'
              : 'border-gray-200 text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:text-gray-400 dark:hover:border-gray-600'
          }`}
        >
          <span className="truncate">{label}</span>
          <div
            className={`flex h-4 w-7 shrink-0 items-center rounded-full p-0.5 transition-colors ${
              preferences[key] ? 'bg-[#1D7BD7]' : 'bg-gray-300 dark:bg-gray-600'
            }`}
          >
            <div
              className={`h-3 w-3 rounded-full bg-white shadow-sm transition-transform ${
                preferences[key] ? 'translate-x-3' : 'translate-x-0'
              }`}
            />
          </div>
        </button>
      ))}
    </div>
  )
}

function SnapshotSubscriptionContent() {
  const { status } = useSession()
  const [frequency, setFrequency] = useState<'weekly' | 'monthly'>('weekly')
  const [preferences, setPreferences] = useState<Record<SnapshotContentKey, boolean>>(
    DEFAULT_SNAPSHOT_PREFERENCES
  )

  const { data, loading, error, refetch } = useQuery<{
    mySnapshotSubscription?: SnapshotSubscriptionData | null
  }>(GET_MY_SNAPSHOT_SUBSCRIPTION, {
    skip: status !== 'authenticated',
    errorPolicy: 'all',
  })

  const subscription = data?.mySnapshotSubscription
  const hasActiveSubscription = subscription?.isActive === true

  useEffect(() => {
    if (subscription?.isActive) {
      setFrequency(subscription.frequency as 'weekly' | 'monthly')
      setPreferences({
        includeChapters: subscription.includeChapters,
        includeEvents: subscription.includeEvents,
        includeIssues: subscription.includeIssues,
        includePosts: subscription.includePosts,
        includeProjects: subscription.includeProjects,
        includePullRequests: subscription.includePullRequests,
        includeReleases: subscription.includeReleases,
        includeUsers: subscription.includeUsers,
      })
    }
  }, [subscription])

  const [createSubscription, { loading: creating }] = useMutation<{
    createSnapshotSubscription: MutationResponse
  }>(CREATE_SNAPSHOT_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.createSnapshotSubscription
      if (result.ok) {
        addToast({
          title: 'Subscribed!',
          description: 'You will receive snapshot digest emails.',
          color: 'success',
        })
        refetch()
      } else {
        addToast({ title: 'Error', description: result.message, color: 'danger' })
      }
    },
    onError: () => {
      addToast({ title: 'Error', description: 'Failed to create subscription.', color: 'danger' })
    },
  })

  const [updateSubscription, { loading: updating }] = useMutation<{
    updateSnapshotSubscription: MutationResponse
  }>(UPDATE_SNAPSHOT_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.updateSnapshotSubscription
      if (result.ok) {
        addToast({
          title: 'Updated',
          description: 'Your preferences have been saved.',
          color: 'success',
        })
        refetch()
      } else {
        addToast({ title: 'Error', description: result.message, color: 'danger' })
      }
    },
    onError: () => {
      addToast({
        title: 'Error',
        description: 'Failed to update subscription.',
        color: 'danger',
      })
    },
  })

  const [cancelSubscription, { loading: cancelling }] = useMutation<{
    cancelSnapshotSubscription: MutationResponse
  }>(CANCEL_SNAPSHOT_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.cancelSnapshotSubscription
      if (result.ok) {
        addToast({
          title: 'Unsubscribed',
          description: 'You will no longer receive digest emails.',
          color: 'success',
        })
        setPreferences(DEFAULT_SNAPSHOT_PREFERENCES)
        setFrequency('weekly')
        refetch()
      } else {
        addToast({ title: 'Error', description: result.message, color: 'danger' })
      }
    },
    onError: () => {
      addToast({
        title: 'Error',
        description: 'Failed to cancel subscription.',
        color: 'danger',
      })
    },
  })

  const togglePreference = useCallback((key: SnapshotContentKey) => {
    setPreferences((prev) => ({ ...prev, [key]: !prev[key] }))
  }, [])

  const getMutationVariables = () => ({
    inputData: {
      frequency,
      ...preferences,
    },
  })

  const handleSave = () => {
    if (hasActiveSubscription) {
      updateSubscription({ variables: getMutationVariables() })
    } else {
      createSubscription({ variables: getMutationVariables() })
    }
  }

  const isSaving = creating || updating

  const [showCancelModal, setShowCancelModal] = useState(false)

  const handleCancel = () => {
    setShowCancelModal(true)
  }

  const handleConfirmCancel = () => {
    setShowCancelModal(false)
    cancelSubscription()
  }

  if (loading) {
    return <LoadingSpinner />
  }

  if (error && !subscription) {
    return (
      <SecondaryCard>
        <div className="rounded-md bg-red-50 p-4 text-red-700 dark:bg-red-900/20 dark:text-red-400">
          Failed to load subscription settings. Please try again later.
        </div>
      </SecondaryCard>
    )
  }

  const destructiveButtonStyles =
    'flex items-center gap-2 rounded-md border border-red-500 bg-transparent px-2 py-2 text-red-600 transition-all hover:bg-red-600 hover:text-white dark:text-red-400 dark:hover:bg-red-600 dark:hover:text-white'

  return (
    <>
      <SecondaryCard>
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h2 className="text-xl font-semibold">Snapshot Subscription</h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {hasActiveSubscription
                ? 'Manage your general OWASP subscriptions.'
                : 'Subscribe to get curated OWASP community updates delivered to your inbox.'}
            </p>
          </div>
          {hasActiveSubscription && (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
              <FaBell className="h-3 w-3" />
              Active
            </span>
          )}
        </div>

        <div className="mb-4">
          <h3 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">Frequency</h3>
          <div className="inline-flex rounded-lg border border-gray-200 p-0.5 dark:border-gray-700">
            {(['weekly', 'monthly'] as const).map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setFrequency(option)}
                aria-pressed={frequency === option}
                className={`rounded-md px-3 py-1 text-sm font-medium transition-all ${
                  frequency === option
                    ? 'bg-[#1D7BD7] text-white shadow-sm'
                    : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                }`}
              >
                {option.charAt(0).toUpperCase() + option.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">Content</h3>
          <ContentToggleGrid
            fields={SNAPSHOT_CONTENT_FIELDS}
            preferences={preferences}
            onToggle={togglePreference}
          />
        </div>
      </SecondaryCard>

      <div className="flex justify-end gap-3">
        {hasActiveSubscription && (
          <Button
            variant="bordered"
            onPress={handleCancel}
            isDisabled={cancelling}
            className={destructiveButtonStyles}
          >
            <FaBellSlash />
            {cancelling ? 'Cancelling...' : 'Unsubscribe'}
          </Button>
        )}
        <ActionButton onClick={handleSave} isDisabled={isSaving}>
          {hasActiveSubscription ? (
            <>
              <FaFloppyDisk />
              {updating ? 'Saving...' : 'Save Changes'}
            </>
          ) : (
            <>
              <FaBell />
              {creating ? 'Subscribing...' : 'Subscribe'}
            </>
          )}
        </ActionButton>
      </div>

      <Modal isOpen={showCancelModal} onClose={() => setShowCancelModal(false)} size="md">
        <ModalContent className="rounded-lg bg-white shadow-xl dark:border dark:border-gray-800 dark:bg-[#212529]">
          <ModalHeader className="border-b border-gray-200 px-5 py-4 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">Confirm Unsubscribe</h2>
          </ModalHeader>
          <ModalBody className="px-5 py-4">
            <p className="text-gray-600 dark:text-gray-300">
              Are you sure you want to unsubscribe? You will no longer receive snapshot digest
              emails.
            </p>
          </ModalBody>
          <ModalFooter className="flex justify-end gap-3 border-t border-gray-200 px-5 py-4 dark:border-gray-700">
            <ActionButton onClick={() => setShowCancelModal(false)}>Cancel</ActionButton>
            <Button
              onPress={handleConfirmCancel}
              isDisabled={cancelling}
              className={destructiveButtonStyles}
            >
              <FaBellSlash />
              {cancelling ? 'Cancelling...' : 'Yes, Unsubscribe'}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

interface EntitySubscriptionData {
  id: string
  frequency: string
  isActive: boolean
  chapter?: { id: string; name: string } | null
  committee?: { id: string; name: string } | null
  project?: { id: string; name: string } | null
  createdAt: string
  updatedAt: string
}

function getEntityInfo(sub: EntitySubscriptionData): { name: string; type: string } {
  if (sub.project) return { name: sub.project.name, type: 'Project' }
  if (sub.chapter) return { name: sub.chapter.name, type: 'Chapter' }
  if (sub.committee) return { name: sub.committee.name, type: 'Committee' }
  return { name: 'Unknown', type: '' }
}

function EntitySubscriptionCard({
  subscription,
  onSave,
  onUnsubscribe,
  onTrashDelete,
  onReactivate,
  isSaving,
}: Readonly<{
  subscription: EntitySubscriptionData
  onSave: (
    id: string,
    data: {
      frequency: string
    }
  ) => void
  onUnsubscribe?: (id: string) => void
  onTrashDelete?: (id: string) => void
  onReactivate?: (id: string) => void
  isSaving: boolean
}>) {
  const [frequency, setFrequency] = useState<'weekly' | 'monthly'>(
    subscription.frequency as 'weekly' | 'monthly'
  )
  useEffect(() => {
    setFrequency(subscription.frequency as 'weekly' | 'monthly')
  }, [subscription])

  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showUnsubscribeModal, setShowUnsubscribeModal] = useState(false)

  const entityInfo = getEntityInfo(subscription)
  const isActive = subscription.isActive

  const destructiveButtonStyles =
    'flex items-center gap-2 rounded-md border border-red-500 bg-transparent px-2 py-2 text-red-600 transition-all hover:bg-red-600 hover:text-white dark:text-red-400 dark:hover:bg-red-600 dark:hover:text-white'

  return (
    <SecondaryCard>
      <div>
        {/* Card header with entity info and trash icon */}
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
              {entityInfo.name}
            </h3>
            <div className="mt-1 flex items-center gap-2">
              <span className="inline-block rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                {entityInfo.type}
              </span>
              {isActive ? (
                <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
                  <FaBell className="h-3 w-3" />
                  Active
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                  Inactive
                </span>
              )}
            </div>
          </div>
          {onTrashDelete && (
            <button
              type="button"
              onClick={() => setShowDeleteModal(true)}
              className="mt-1 cursor-pointer rounded p-1.5 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20 dark:hover:text-red-400"
              aria-label="Delete subscription permanently"
            >
              <FaTrash className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        {isActive && (
          <>
            {/* Frequency */}
            <div className="mb-4">
              <h4 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">
                Frequency
              </h4>
              <div className="inline-flex rounded-lg border border-gray-200 p-0.5 dark:border-gray-700">
                {(['weekly', 'monthly'] as const).map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setFrequency(option)}
                    aria-pressed={frequency === option}
                    className={`rounded-md px-3 py-1 text-sm font-medium transition-all ${
                      frequency === option
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

        {/* Card footer buttons */}
        <div className="flex justify-end gap-3">
          {isActive ? (
            <>
              {onUnsubscribe && (
                <Button
                  variant="bordered"
                  onPress={() => setShowUnsubscribeModal(true)}
                  className={destructiveButtonStyles}
                >
                  <FaBellSlash />
                  Unsubscribe
                </Button>
              )}
              <ActionButton
                onClick={() => onSave(subscription.id, { frequency })}
                isDisabled={isSaving}
              >
                <FaFloppyDisk />
                {isSaving ? 'Saving...' : 'Save Changes'}
              </ActionButton>
            </>
          ) : (
            onReactivate && (
              <ActionButton onClick={() => onReactivate(subscription.id)} isDisabled={isSaving}>
                <FaBell />
                {isSaving ? 'Reactivating...' : 'Reactivate'}
              </ActionButton>
            )
          )}
        </div>
      </div>

      {/* Delete confirmation modal */}
      <Modal isOpen={showDeleteModal} onClose={() => setShowDeleteModal(false)} size="md">
        <ModalContent className="rounded-lg bg-white shadow-xl dark:border dark:border-gray-800 dark:bg-[#212529]">
          <ModalHeader className="border-b border-gray-200 px-5 py-4 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">Confirm Delete</h2>
          </ModalHeader>
          <ModalBody className="px-5 py-4">
            <p className="text-gray-600 dark:text-gray-300">
              Are you sure you want to permanently delete the subscription for &quot;
              {entityInfo.name}&quot;? This cannot be undone.
            </p>
          </ModalBody>
          <ModalFooter className="flex justify-end gap-3 border-t border-gray-200 px-5 py-4 dark:border-gray-700">
            <ActionButton onClick={() => setShowDeleteModal(false)}>Cancel</ActionButton>
            <Button
              onPress={() => {
                setShowDeleteModal(false)
                onTrashDelete?.(subscription.id)
              }}
              className={destructiveButtonStyles}
            >
              <FaTrash />
              Yes, Delete
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Unsubscribe confirmation modal */}
      <Modal isOpen={showUnsubscribeModal} onClose={() => setShowUnsubscribeModal(false)} size="md">
        <ModalContent className="rounded-lg bg-white shadow-xl dark:border dark:border-gray-800 dark:bg-[#212529]">
          <ModalHeader className="border-b border-gray-200 px-5 py-4 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">Confirm Unsubscribe</h2>
          </ModalHeader>
          <ModalBody className="px-5 py-4">
            <p className="text-gray-600 dark:text-gray-300">
              Are you sure you want to unsubscribe? You will no longer receive snapshot digest
              emails.
            </p>
          </ModalBody>
          <ModalFooter className="flex justify-end gap-3 border-t border-gray-200 px-5 py-4 dark:border-gray-700">
            <ActionButton onClick={() => setShowUnsubscribeModal(false)}>Cancel</ActionButton>
            <Button
              onPress={() => {
                setShowUnsubscribeModal(false)
                onUnsubscribe?.(subscription.id)
              }}
              className={destructiveButtonStyles}
            >
              <FaBellSlash />
              Yes, Unsubscribe
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </SecondaryCard>
  )
}

function EntitySubscriptionContent() {
  const { status } = useSession()

  const { data, loading, error, refetch } = useQuery<{
    myEntitySubscriptions?: EntitySubscriptionData[]
  }>(GET_MY_ENTITY_SUBSCRIPTIONS, {
    skip: status !== 'authenticated',
    errorPolicy: 'all',
  })

  const subscriptions = data?.myEntitySubscriptions ?? []
  const activeCount = subscriptions.filter((s) => s.isActive).length

  const [updateEntitySubscription, { loading: updating }] = useMutation<{
    updateEntitySubscription: MutationResponse
  }>(UPDATE_ENTITY_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.updateEntitySubscription
      if (result.ok) {
        addToast({
          title: 'Updated',
          description: 'Entity subscription updated successfully.',
          color: 'success',
        })
        refetch()
      } else {
        addToast({ title: 'Error', description: result.message, color: 'danger' })
      }
    },
    onError: () => {
      addToast({
        title: 'Error',
        description: 'Failed to update entity subscription.',
        color: 'danger',
      })
    },
  })

  const [cancelEntitySubscription, { loading: cancelling }] = useMutation<{
    cancelEntitySubscription: MutationResponse
  }>(CANCEL_ENTITY_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.cancelEntitySubscription
      if (result.ok) {
        addToast({
          title: 'Unsubscribed',
          description: 'Entity subscription deactivated.',
          color: 'success',
        })
        refetch()
      } else {
        addToast({ title: 'Error', description: result.message, color: 'danger' })
      }
    },
    onError: () => {
      addToast({
        title: 'Error',
        description: 'Failed to unsubscribe.',
        color: 'danger',
      })
    },
  })

  const [deleteEntitySubscription, { loading: deleting }] = useMutation<{
    deleteEntitySubscription: MutationResponse
  }>(DELETE_ENTITY_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.deleteEntitySubscription
      if (result.ok) {
        addToast({
          title: 'Deleted',
          description: 'Entity subscription permanently deleted.',
          color: 'success',
        })
        refetch()
      } else {
        addToast({ title: 'Error', description: result.message, color: 'danger' })
      }
    },
    onError: () => {
      addToast({
        title: 'Error',
        description: 'Failed to delete entity subscription.',
        color: 'danger',
      })
    },
  })

  const [reactivateEntitySubscription, { loading: reactivating }] = useMutation<{
    reactivateEntitySubscription: MutationResponse
  }>(REACTIVATE_ENTITY_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.reactivateEntitySubscription
      if (result.ok) {
        addToast({
          title: 'Reactivated',
          description: 'Entity subscription reactivated.',
          color: 'success',
        })
        refetch()
      } else {
        addToast({ title: 'Error', description: result.message, color: 'danger' })
      }
    },
    onError: () => {
      addToast({
        title: 'Error',
        description: 'Failed to reactivate entity subscription.',
        color: 'danger',
      })
    },
  })

  const isMutating = updating || cancelling || deleting || reactivating

  const handleSave = (
    id: string,
    data: {
      frequency: string
    }
  ) => {
    updateEntitySubscription({
      variables: {
        subscriptionId: decodeRelayId(id),
        inputData: data,
      },
    })
  }

  const handleUnsubscribe = (id: string) => {
    cancelEntitySubscription({
      variables: { subscriptionId: decodeRelayId(id) },
    })
  }

  const handleTrashDelete = (id: string) => {
    deleteEntitySubscription({
      variables: { subscriptionId: decodeRelayId(id) },
    })
  }

  const handleReactivate = (id: string) => {
    reactivateEntitySubscription({
      variables: { subscriptionId: decodeRelayId(id) },
    })
  }

  if (loading) {
    return <LoadingSpinner />
  }

  if (error && subscriptions.length === 0) {
    return (
      <SecondaryCard>
        <div className="rounded-md bg-red-50 p-4 text-red-700 dark:bg-red-900/20 dark:text-red-400">
          Failed to load entity subscriptions. Please try again later.
        </div>
      </SecondaryCard>
    )
  }

  return (
    <>
      <SecondaryCard>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Entity Subscriptions</h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Manage your project, chapter, and committee subscriptions.{' '}
              <span className="font-medium">
                {activeCount}/{MAX_ENTITY_SUBSCRIPTIONS} subscriptions used.
              </span>
            </p>
          </div>
        </div>
      </SecondaryCard>

      {/* Active subscriptions */}
      {subscriptions
        .filter((s) => s.isActive)
        .map((sub) => (
          <EntitySubscriptionCard
            key={sub.id}
            subscription={sub}
            onSave={handleSave}
            onUnsubscribe={handleUnsubscribe}
            onTrashDelete={handleTrashDelete}
            isSaving={isMutating}
          />
        ))}

      {/* Inactive subscriptions */}
      {subscriptions
        .filter((s) => !s.isActive)
        .map((sub) => (
          <EntitySubscriptionCard
            key={sub.id}
            subscription={sub}
            onSave={handleSave}
            onReactivate={handleReactivate}
            onTrashDelete={handleTrashDelete}
            isSaving={isMutating}
          />
        ))}

      {subscriptions.length === 0 && (
        <SecondaryCard>
          <div className="py-4 text-center text-gray-500 dark:text-gray-400">
            <p>No entity subscriptions yet.</p>
            <p className="mt-1 text-sm">
              Visit a project, chapter, or committee page and click &quot;Subscribe&quot; to get
              started.
            </p>
          </div>
        </SecondaryCard>
      )}
    </>
  )
}

const SETTINGS_TABS = [{ key: 'subscriptions', label: 'Subscriptions' }] as const

type SettingsTabKey = (typeof SETTINGS_TABS)[number]['key']

const SUB_TABS = [
  { key: 'snapshot', label: 'Snapshot' },
  { key: 'entity', label: 'Entity' },
] as const

type SubTabKey = (typeof SUB_TABS)[number]['key']

export default function SettingsPage() {
  const { status } = useSession()
  const [activeTab, setActiveTab] = useState<SettingsTabKey>('subscriptions')
  const searchParams = useSearchParams()
  const initialSubTab = searchParams.get('tab') === 'entity' ? 'entity' : 'snapshot'
  const [activeSubTab, setActiveSubTab] = useState<SubTabKey>(initialSubTab)

  if (status === 'loading') {
    return <LoadingSpinner />
  }

  if (status === 'unauthenticated') {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <h2 className="mb-2 text-2xl font-bold text-gray-700 dark:text-gray-300">
            Sign in required
          </h2>
          <p className="text-gray-500 dark:text-gray-400">
            Please sign in to manage your settings.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-[80vh] flex-col items-center p-8">
      <div className="w-full max-w-3xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold">Settings</h1>
        </div>

        <div className="mb-6 flex border-b border-gray-200 dark:border-gray-700">
          {SETTINGS_TABS.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key)}
              className={`border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'subscriptions' && (
          <>
            <div className="mb-6 flex gap-2">
              {SUB_TABS.map((tab) => (
                <button
                  key={tab.key}
                  type="button"
                  onClick={() => setActiveSubTab(tab.key)}
                  className={`rounded-md border border-[#1D7BD7] px-4 py-2 text-sm font-medium transition-all ${
                    activeSubTab === tab.key
                      ? 'bg-[#1D7BD7] text-white'
                      : 'bg-transparent text-[#1D7BD7] hover:bg-[#1D7BD7] hover:text-white dark:hover:text-white'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
            {activeSubTab === 'snapshot' && <SnapshotSubscriptionContent />}
            {activeSubTab === 'entity' && <EntitySubscriptionContent />}
          </>
        )}
      </div>
    </div>
  )
}
