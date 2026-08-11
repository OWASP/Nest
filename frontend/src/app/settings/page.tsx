'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/modal'
import { addToast } from '@heroui/toast'
import { Tooltip } from '@heroui/tooltip'
import debounce from 'lodash/debounce'
import { useSession } from 'next-auth/react'
import { useCallback, useEffect, useState } from 'react'
import { FaBell, FaFloppyDisk, FaPlus, FaTrash } from 'react-icons/fa6'

import { SEARCH_CHAPTERS } from 'server/queries/chapterQueries'
import { SEARCH_COMMITTEES } from 'server/queries/committeeQueries'
import { SEARCH_PROJECTS } from 'server/queries/projectQueries'
import {
  CREATE_SNAPSHOT_SUBSCRIPTION,
  DELETE_SNAPSHOT_SUBSCRIPTION,
  GET_MY_SNAPSHOT_SUBSCRIPTIONS,
  UPDATE_SNAPSHOT_SUBSCRIPTION,
} from 'server/queries/subscriptionQueries'
import { decodeRelayId } from 'utils/decodeRelayId'
import ActionButton from 'components/ActionButton'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const MAX_SUBSCRIPTIONS = 5

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

interface SubscribedEntity {
  id: number
  name: string
}

interface SnapshotSubscriptionData {
  id: string
  name: string
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
  subscribedProjects: SubscribedEntity[]
  subscribedChapters: SubscribedEntity[]
  subscribedCommittees: SubscribedEntity[]
  createdAt: string
  updatedAt: string
}

interface MutationResponse {
  ok: boolean
  message: string
  subscription?: unknown
}

const DEFAULT_PREFERENCES: Record<SnapshotContentKey, boolean> = {
  includeChapters: false,
  includeEvents: false,
  includeIssues: false,
  includePosts: false,
  includeProjects: false,
  includePullRequests: false,
  includeReleases: false,
  includeUsers: false,
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

function EntityMultiSelect({
  label,
  searchQuery,
  searchResultKey,
  selectedEntities,
  onAdd,
  onRemove,
}: Readonly<{
  label: string
  searchQuery: ReturnType<typeof import('@apollo/client').gql>
  searchResultKey: string
  selectedEntities: SubscribedEntity[]
  onAdd: (entity: SubscribedEntity) => void
  onRemove: (id: number) => void
}>) {
  const client = useApolloClient()
  const [inputValue, setInputValue] = useState('')
  const [items, setItems] = useState<{ id: string; name: string }[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const fetchSuggestions = useCallback(
    debounce(async (query: string) => {
      const trimmedQuery = query.trim()
      if (trimmedQuery.length < 2) {
        setItems([])
        setIsLoading(false)
        return
      }

      setIsLoading(true)
      try {
        const { data } = await client.query({
          query: searchQuery,
          variables: { query: trimmedQuery },
        })

        const results =
          ((data as Record<string, unknown>)?.[searchResultKey] as
            { id: string; name: string }[] | undefined) || []
        const selectedIds = new Set(selectedEntities.map((e) => e.id))
        const filtered = results.filter((r) => !selectedIds.has(decodeRelayId(r.id)))
        setItems(filtered.slice(0, 5))
      } catch {
        setItems([])
      } finally {
        setIsLoading(false)
      }
    }, 300),
    [client, searchQuery, searchResultKey, selectedEntities]
  )

  useEffect(() => {
    fetchSuggestions(inputValue)
    return () => {
      fetchSuggestions.cancel()
    }
  }, [inputValue, fetchSuggestions])

  return (
    <div>
      <h4 className="mb-1.5 text-sm font-semibold text-gray-600 dark:text-gray-300">{label}</h4>

      <div className="relative flex min-h-[36px] flex-wrap items-center gap-1.5 rounded-md border border-gray-200 bg-gray-50 px-2 py-1 transition-colors focus-within:border-[#1D7BD7] hover:border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:focus-within:border-[#1D7BD7] dark:hover:border-gray-600">
        {selectedEntities.map((entity) => (
          <span
            key={entity.id}
            className="inline-flex items-center gap-1 rounded-md bg-gray-500 px-2 py-0.5 text-xs font-medium text-white dark:bg-gray-600"
          >
            {entity.name}
            <button
              type="button"
              onClick={() => onRemove(entity.id)}
              className="ml-0.5 cursor-pointer rounded-full p-0.5 text-white/80 transition-colors hover:bg-white/20 hover:text-white"
              aria-label={`Remove ${entity.name}`}
            >
              ×
            </button>
          </span>
        ))}

        <div className="min-w-[120px] flex-1">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            className="w-full border-none bg-transparent py-0.5 text-sm text-gray-800 outline-none dark:text-gray-200"
            aria-label={`Search ${label.toLowerCase()}`}
          />
        </div>

        {(items.length > 0 || isLoading) && inputValue.trim().length >= 2 && (
          <div className="absolute top-[calc(100%+4px)] left-0 z-50 w-full overflow-hidden rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-[#2a2a2a]">
            {isLoading ? (
              <div className="px-4 py-3 text-sm text-gray-400">Searching...</div>
            ) : (
              items.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => {
                    onAdd({ id: decodeRelayId(item.id), name: item.name })
                    setInputValue('')
                    setItems([])
                  }}
                  className="flex w-full cursor-pointer items-center px-4 py-3 text-left text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-white/5"
                >
                  {item.name}
                </button>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function SubscriptionCard({
  subscription,
  onSave,
  onDelete,
  isMutating,
}: Readonly<{
  subscription: SnapshotSubscriptionData
  onSave: (
    id: string,
    data: {
      name: string
      frequency: string
      preferences: Record<SnapshotContentKey, boolean>
      projectIds: number[]
      chapterIds: number[]
      committeeIds: number[]
    }
  ) => void
  onDelete?: (id: string) => void
  isMutating: boolean
}>) {
  const [name, setName] = useState(subscription.name)
  const [frequency, setFrequency] = useState<'weekly' | 'monthly'>(
    subscription.frequency as 'weekly' | 'monthly'
  )
  const [preferences, setPreferences] = useState<Record<SnapshotContentKey, boolean>>({
    includeChapters: subscription.includeChapters,
    includeEvents: subscription.includeEvents,
    includeIssues: subscription.includeIssues,
    includePosts: subscription.includePosts,
    includeProjects: subscription.includeProjects,
    includePullRequests: subscription.includePullRequests,
    includeReleases: subscription.includeReleases,
    includeUsers: subscription.includeUsers,
  })
  const [projects, setProjects] = useState<SubscribedEntity[]>(subscription.subscribedProjects)
  const [chapters, setChapters] = useState<SubscribedEntity[]>(subscription.subscribedChapters)
  const [committees, setCommittees] = useState<SubscribedEntity[]>(
    subscription.subscribedCommittees
  )

  const [showDeleteModal, setShowDeleteModal] = useState(false)

  useEffect(() => {
    setName(subscription.name)
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
    setProjects(subscription.subscribedProjects)
    setChapters(subscription.subscribedChapters)
    setCommittees(subscription.subscribedCommittees)
  }, [subscription])

  const togglePreference = useCallback((key: SnapshotContentKey) => {
    setPreferences((prev) => ({ ...prev, [key]: !prev[key] }))
  }, [])

  const handleSave = () => {
    onSave(subscription.id, {
      name,
      frequency,
      preferences,
      projectIds: projects.map((p) => p.id),
      chapterIds: chapters.map((c) => c.id),
      committeeIds: committees.map((c) => c.id),
    })
  }

  const isActive = subscription.isActive
  const hasAtLeastOnePreference = Object.values(preferences).some(Boolean)

  const destructiveButtonStyles =
    'flex items-center gap-2 rounded-md border border-red-500 bg-transparent px-2 py-2 text-red-600 transition-all hover:bg-red-600 hover:text-white dark:text-red-400 dark:hover:bg-red-600 dark:hover:text-white'

  return (
    <SecondaryCard>
      <div>
        <div className="mb-4 flex items-center justify-between gap-4">
          <div className="flex-1">
            {isActive ? (
              <>
                <h3 className="sr-only">{name || 'Active Subscription'}</h3>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Subscription name"
                  className="w-full bg-transparent text-xl font-bold text-gray-900 transition-colors outline-none placeholder:text-gray-300 dark:text-white dark:placeholder:text-gray-700"
                />
              </>
            ) : (
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">{name}</h3>
            )}
          </div>
          <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            <FaBell className="h-3 w-3" />
            Active
          </span>
        </div>

        {isActive && (
          <>
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

            <div className="mb-4">
              <h4 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">
                Content
              </h4>
              <ContentToggleGrid
                fields={SNAPSHOT_CONTENT_FIELDS}
                preferences={preferences}
                onToggle={togglePreference}
              />
            </div>

            <div className="mt-6 mb-6 flex flex-col gap-6">
              <EntityMultiSelect
                label="Projects"
                searchQuery={SEARCH_PROJECTS}
                searchResultKey="searchProjects"
                selectedEntities={projects}
                onAdd={(entity) => setProjects((prev) => [...prev, entity])}
                onRemove={(id) => setProjects((prev) => prev.filter((p) => p.id !== id))}
              />

              <EntityMultiSelect
                label="Chapters"
                searchQuery={SEARCH_CHAPTERS}
                searchResultKey="searchChapters"
                selectedEntities={chapters}
                onAdd={(entity) => setChapters((prev) => [...prev, entity])}
                onRemove={(id) => setChapters((prev) => prev.filter((c) => c.id !== id))}
              />

              <EntityMultiSelect
                label="Committees"
                searchQuery={SEARCH_COMMITTEES}
                searchResultKey="searchCommittees"
                selectedEntities={committees}
                onAdd={(entity) => setCommittees((prev) => [...prev, entity])}
                onRemove={(id) => setCommittees((prev) => prev.filter((c) => c.id !== id))}
              />
            </div>
          </>
        )}

        <div className="flex justify-end gap-3">
          {isActive ? (
            <>
              {onDelete && (
                <Button
                  variant="bordered"
                  onPress={() => setShowDeleteModal(true)}
                  className={destructiveButtonStyles}
                >
                  <FaTrash />
                  Delete
                </Button>
              )}
              {hasAtLeastOnePreference ? (
                <ActionButton onClick={handleSave} isDisabled={isMutating}>
                  <FaFloppyDisk />
                  {isMutating ? 'Saving...' : 'Save Changes'}
                </ActionButton>
              ) : (
                <Tooltip content="Select at least one content type">
                  <div className="inline-block cursor-not-allowed">
                    <ActionButton onClick={handleSave} isDisabled={true}>
                      <FaFloppyDisk />
                      Save Changes
                    </ActionButton>
                  </div>
                </Tooltip>
              )}
            </>
          ) : null}
        </div>
      </div>

      <Modal isOpen={showDeleteModal} onClose={() => setShowDeleteModal(false)} size="md">
        <ModalContent className="rounded-lg bg-white shadow-xl dark:border dark:border-gray-800 dark:bg-[#212529]">
          <ModalHeader className="border-b border-gray-200 px-5 py-4 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">Confirm Delete</h2>
          </ModalHeader>
          <ModalBody className="px-5 py-4">
            <p className="text-gray-600 dark:text-gray-300">
              Are you sure you want to permanently delete &quot;{name}&quot;? This cannot be undone.
            </p>
          </ModalBody>
          <ModalFooter className="flex justify-end gap-3 border-t border-gray-200 px-5 py-4 dark:border-gray-700">
            <ActionButton onClick={() => setShowDeleteModal(false)}>Cancel</ActionButton>
            <Button
              onPress={() => {
                setShowDeleteModal(false)
                onDelete?.(subscription.id)
              }}
              className={destructiveButtonStyles}
            >
              <FaTrash />
              Yes, Delete
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </SecondaryCard>
  )
}

function SubscriptionContent() {
  const { status } = useSession()

  const { data, loading, error, refetch } = useQuery<{
    mySnapshotSubscriptions?: SnapshotSubscriptionData[]
  }>(GET_MY_SNAPSHOT_SUBSCRIPTIONS, {
    skip: status !== 'authenticated',
    errorPolicy: 'all',
  })

  const subscriptions = data?.mySnapshotSubscriptions ?? []
  const activeCount = subscriptions.filter((s) => s.isActive).length

  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newName, setNewName] = useState('')
  const [newFrequency, setNewFrequency] = useState<'weekly' | 'monthly'>('weekly')
  const [newPreferences, setNewPreferences] = useState<Record<SnapshotContentKey, boolean>>({
    ...DEFAULT_PREFERENCES,
  })
  const [newProjects, setNewProjects] = useState<SubscribedEntity[]>([])
  const [newChapters, setNewChapters] = useState<SubscribedEntity[]>([])
  const [newCommittees, setNewCommittees] = useState<SubscribedEntity[]>([])

  const toggleNewPreference = useCallback((key: SnapshotContentKey) => {
    setNewPreferences((prev) => ({ ...prev, [key]: !prev[key] }))
  }, [])

  const [createSubscription, { loading: creating }] = useMutation<{
    createSnapshotSubscription: MutationResponse
  }>(CREATE_SNAPSHOT_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.createSnapshotSubscription
      if (result.ok) {
        addToast({
          title: 'Subscribed!',
          description: 'Your new subscription has been created.',
          color: 'success',
        })
        setShowCreateForm(false)
        setNewName('')
        setNewFrequency('weekly')
        setNewPreferences({ ...DEFAULT_PREFERENCES })
        setNewProjects([])
        setNewChapters([])
        setNewCommittees([])
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

  const [deleteSubscription, { loading: deleting }] = useMutation<{
    deleteSnapshotSubscription: MutationResponse
  }>(DELETE_SNAPSHOT_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.deleteSnapshotSubscription
      if (result.ok) {
        addToast({
          title: 'Deleted',
          description: 'Subscription permanently deleted.',
          color: 'success',
        })
        refetch()
      } else {
        addToast({ title: 'Error', description: result.message, color: 'danger' })
      }
    },
    onError: () => {
      addToast({ title: 'Error', description: 'Failed to delete subscription.', color: 'danger' })
    },
  })

  const isMutating = creating || updating || deleting

  const handleSave = (
    id: string,
    data: {
      name: string
      frequency: string
      preferences: Record<SnapshotContentKey, boolean>
      projectIds: number[]
      chapterIds: number[]
      committeeIds: number[]
    }
  ) => {
    updateSubscription({
      variables: {
        subscriptionId: decodeRelayId(id),
        inputData: {
          name: data.name,
          frequency: data.frequency,
          ...data.preferences,
          subscribedProjectIds: data.projectIds,
          subscribedChapterIds: data.chapterIds,
          subscribedCommitteeIds: data.committeeIds,
        },
      },
    })
  }

  const handleDelete = (id: string) => {
    deleteSubscription({ variables: { subscriptionId: decodeRelayId(id) } })
  }

  const hasAtLeastOneNewPreference = Object.values(newPreferences).some(Boolean)

  const handleCreate = () => {
    createSubscription({
      variables: {
        inputData: {
          name: newName || undefined,
          frequency: newFrequency,
          ...newPreferences,
          subscribedProjectIds: newProjects.map((p) => p.id),
          subscribedChapterIds: newChapters.map((c) => c.id),
          subscribedCommitteeIds: newCommittees.map((c) => c.id),
        },
      },
    })
  }

  if (loading) {
    return <LoadingSpinner />
  }

  if (error && subscriptions.length === 0) {
    return (
      <SecondaryCard>
        <div className="rounded-md bg-red-50 p-4 text-red-700 dark:bg-red-900/20 dark:text-red-400">
          Failed to load subscriptions. Please try again later.
        </div>
      </SecondaryCard>
    )
  }

  return (
    <>
      <SecondaryCard>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Subscriptions</h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Manage your OWASP community update subscriptions.{' '}
              <span className="font-medium">
                {activeCount}/{MAX_SUBSCRIPTIONS} active.
              </span>
            </p>
          </div>
        </div>
      </SecondaryCard>

      {subscriptions
        .filter((s) => s.isActive)
        .map((sub) => (
          <SubscriptionCard
            key={sub.id}
            subscription={sub}
            onSave={handleSave}
            onDelete={handleDelete}
            isMutating={isMutating}
          />
        ))}

      {subscriptions.length === 0 && !showCreateForm && (
        <SecondaryCard>
          <div className="py-4 text-center text-gray-500 dark:text-gray-400">
            <p>No subscriptions yet.</p>
            <p className="mt-1 text-sm">
              Create one to get curated OWASP community updates delivered to your inbox.
            </p>
          </div>
        </SecondaryCard>
      )}

      {showCreateForm && (
        <SecondaryCard>
          <h3 className="mb-4 text-lg font-semibold text-gray-800 dark:text-gray-100">
            New Subscription
          </h3>
          <div className="mb-4">
            <h4 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">Name</h4>
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="e.g., My Weekly Digest"
              className="w-full rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-800 transition-colors outline-none focus:border-[#1D7BD7] dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
            />
          </div>
          <div className="mb-4">
            <h4 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">
              Frequency
            </h4>
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

          <div className="mb-4">
            <h4 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">Content</h4>
            <ContentToggleGrid
              fields={SNAPSHOT_CONTENT_FIELDS}
              preferences={newPreferences}
              onToggle={toggleNewPreference}
            />
          </div>

          <div className="mt-6 mb-6 flex flex-col gap-6">
            <EntityMultiSelect
              label="Projects"
              searchQuery={SEARCH_PROJECTS}
              searchResultKey="searchProjects"
              selectedEntities={newProjects}
              onAdd={(entity) => setNewProjects((prev) => [...prev, entity])}
              onRemove={(id) => setNewProjects((prev) => prev.filter((p) => p.id !== id))}
            />

            <EntityMultiSelect
              label="Chapters"
              searchQuery={SEARCH_CHAPTERS}
              searchResultKey="searchChapters"
              selectedEntities={newChapters}
              onAdd={(entity) => setNewChapters((prev) => [...prev, entity])}
              onRemove={(id) => setNewChapters((prev) => prev.filter((c) => c.id !== id))}
            />

            <EntityMultiSelect
              label="Committees"
              searchQuery={SEARCH_COMMITTEES}
              searchResultKey="searchCommittees"
              selectedEntities={newCommittees}
              onAdd={(entity) => setNewCommittees((prev) => [...prev, entity])}
              onRemove={(id) => setNewCommittees((prev) => prev.filter((c) => c.id !== id))}
            />
          </div>

          <div className="flex justify-end gap-3">
            <ActionButton
              onClick={() => {
                setShowCreateForm(false)
                setNewName('')
                setNewPreferences({ ...DEFAULT_PREFERENCES })
                setNewProjects([])
                setNewChapters([])
                setNewCommittees([])
              }}
            >
              Cancel
            </ActionButton>
            {hasAtLeastOneNewPreference ? (
              <ActionButton onClick={handleCreate} isDisabled={creating}>
                <FaBell />
                {creating ? 'Creating...' : 'Create Subscription'}
              </ActionButton>
            ) : (
              <Tooltip content="Select at least one content type">
                <div className="inline-block cursor-not-allowed">
                  <ActionButton onClick={handleCreate} isDisabled={true}>
                    <FaBell />
                    Create Subscription
                  </ActionButton>
                </div>
              </Tooltip>
            )}
          </div>
        </SecondaryCard>
      )}

      {activeCount < MAX_SUBSCRIPTIONS && !showCreateForm && (
        <button
          type="button"
          onClick={() => setShowCreateForm(true)}
          className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg border-2 border-dashed border-gray-300 px-4 py-4 text-sm font-medium text-gray-500 transition-all hover:border-[#1D7BD7] hover:text-[#1D7BD7] dark:border-gray-700 dark:text-gray-400 dark:hover:border-[#1D7BD7] dark:hover:text-[#1D7BD7]"
          aria-label="Add new subscription"
        >
          <FaPlus className="h-3 w-3" />
          New Subscription
        </button>
      )}
    </>
  )
}

const SETTINGS_TABS = [{ key: 'subscriptions', label: 'Subscriptions' }] as const

type SettingsTabKey = (typeof SETTINGS_TABS)[number]['key']

export default function SettingsPage() {
  const { status } = useSession()
  const [activeTab, setActiveTab] = useState<SettingsTabKey>('subscriptions')

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

        {activeTab === 'subscriptions' && <SubscriptionContent />}
      </div>
    </div>
  )
}
