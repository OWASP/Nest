'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/modal'
import { addToast } from '@heroui/toast'
import debounce from 'lodash/debounce'
import { useSession } from 'next-auth/react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { FaBell, FaBellSlash, FaFloppyDisk, FaPlus, FaTrash, FaXmark } from 'react-icons/fa6'

import { SEARCH_CHAPTERS } from 'server/queries/chapterQueries'
import { SEARCH_COMMITTEES } from 'server/queries/committeeQueries'
import { SEARCH_PROJECTS } from 'server/queries/projectQueries'
import {
  CANCEL_ENTITY_SUBSCRIPTION,
  CANCEL_SNAPSHOT_SUBSCRIPTION,
  CREATE_ENTITY_SUBSCRIPTION,
  CREATE_SNAPSHOT_SUBSCRIPTION,
  DELETE_ENTITY_SUBSCRIPTION,
  GET_MY_ENTITY_SUBSCRIPTIONS,
  GET_MY_SNAPSHOT_SUBSCRIPTION,
  REACTIVATE_ENTITY_SUBSCRIPTION,
  UPDATE_ENTITY_SUBSCRIPTION,
  UPDATE_SNAPSHOT_SUBSCRIPTION,
} from 'server/queries/subscriptionQueries'
import ActionButton from 'components/ActionButton'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const MAX_ENTITY_SUBSCRIPTIONS = 5

function decodeRelayId(globalId: string): number {
  // Try parsing as plain integer first
  const asInt = Number.parseInt(globalId, 10)
  if (!Number.isNaN(asInt)) {
    return asInt
  }
  // Try base64 decoding (relay global ID format: base64("TypeName:id"))
  try {
    const decoded = atob(globalId)
    const parts = decoded.split(':')
    return Number.parseInt(parts.at(-1)!, 10)
  } catch {
    // Fallback: extract any number from the string
    const match = /\d+/.exec(globalId)
    return match ? Number.parseInt(match[0], 10) : 0
  }
}

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

const ENTITY_CONTENT_FIELDS = [
  { key: 'includeIssues', label: 'Issues' },
  { key: 'includePullRequests', label: 'Pull Requests' },
  { key: 'includeReleases', label: 'Releases' },
] as const

type EntityContentKey = (typeof ENTITY_CONTENT_FIELDS)[number]['key']

const ENTITY_TYPE_OPTIONS = [
  {
    key: 'project',
    label: 'Projects',
    searchQuery: SEARCH_PROJECTS,
    searchResultKey: 'searchProjects',
  },
  {
    key: 'chapter',
    label: 'Chapters',
    searchQuery: SEARCH_CHAPTERS,
    searchResultKey: 'searchChapters',
  },
  {
    key: 'committee',
    label: 'Committees',
    searchQuery: SEARCH_COMMITTEES,
    searchResultKey: 'searchCommittees',
  },
] as const

interface EntityItem {
  id: string
  name: string
}

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

interface EntityPreferenceData {
  id: string
  chapter: EntityItem | null
  committee: EntityItem | null
  project: EntityItem | null
  includeIssues: boolean
  includePullRequests: boolean
  includeReleases: boolean
}

interface EntitySubscriptionData {
  id: string
  name: string
  frequency: string
  isActive: boolean
  entityPreferences: EntityPreferenceData[]
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

function EntityPicker({
  label,
  selectedItems,
  onAdd,
  onRemove,
  searchQuery,
  searchResultKey,
}: Readonly<{
  label: string
  selectedItems: EntityItem[]
  onAdd: (item: EntityItem) => void
  onRemove: (id: string) => void
  searchQuery: ReturnType<typeof import('@apollo/client').gql>
  searchResultKey: string
}>) {
  const client = useApolloClient()
  const [inputValue, setInputValue] = useState('')
  const [suggestions, setSuggestions] = useState<EntityItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const selectedItemsRef = useRef(selectedItems)
  const requestIdRef = useRef(0)

  useEffect(() => {
    selectedItemsRef.current = selectedItems
  }, [selectedItems])

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const fetchSuggestions = useCallback(
    debounce(async (query: string) => {
      const trimmed = query.trim()
      if (trimmed.length < 3) {
        ++requestIdRef.current
        setSuggestions([])
        setIsLoading(false)
        return
      }

      const currentRequestId = ++requestIdRef.current
      setIsLoading(true)
      try {
        const { data } = await client.query({
          query: searchQuery,
          variables: { query: trimmed },
        })
        if (currentRequestId !== requestIdRef.current) return
        const results: EntityItem[] = data?.[searchResultKey as keyof typeof data] || []
        const selectedIds = new Set(selectedItemsRef.current.map((item) => item.id))
        setSuggestions(results.filter((item) => !selectedIds.has(item.id)))
      } catch {
        if (currentRequestId === requestIdRef.current) {
          setSuggestions([])
        }
      } finally {
        if (currentRequestId === requestIdRef.current) {
          setIsLoading(false)
        }
      }
    }, 300),
    [client, searchQuery, searchResultKey]
  )

  useEffect(() => {
    fetchSuggestions(inputValue)
    return () => {
      fetchSuggestions.cancel()
    }
  }, [inputValue, fetchSuggestions])

  const handleSelect = (item: EntityItem) => {
    onAdd(item)
    setInputValue('')
    setSuggestions([])
    setShowDropdown(false)
  }

  const renderSuggestions = () => {
    if (isLoading) {
      return <div className="px-3 py-2 text-sm text-gray-500">Searching...</div>
    }
    if (suggestions.length === 0) {
      return <div className="px-3 py-2 text-sm text-gray-500">No results found</div>
    }
    const accessibleRole = 'option'
    return suggestions.map((item) => (
      <button
        key={item.id}
        type="button"
        role={accessibleRole}
        aria-selected={false}
        onMouseDown={(e) => e.preventDefault()}
        onClick={() => handleSelect(item)}
        className="w-full cursor-pointer rounded-sm px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 focus:bg-gray-100 focus:outline-none dark:text-gray-300 dark:hover:bg-[#404040] dark:focus:bg-[#404040]"
      >
        {item.name}
      </button>
    ))
  }

  const isPopupOpen = showDropdown && inputValue.trim().length >= 3
  const suggestionsId = `${label.toLowerCase()}-suggestions`

  const listboxRole = 'listbox'

  return (
    <div className="space-y-3">
      <h3 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">{label}</h3>

      <div className="relative">
        <div className="flex min-h-10 flex-wrap items-center gap-1.5 rounded-lg border border-gray-300 bg-transparent px-3 py-2 focus-within:border-[#1D7BD7] dark:border-gray-600">
          {selectedItems.map((item) => (
            <span
              key={item.id}
              className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-300"
            >
              {item.name}
              <button
                type="button"
                onClick={() => onRemove(item.id)}
                className="ml-0.5 cursor-pointer rounded-sm p-0.5 hover:bg-gray-200 dark:hover:bg-gray-600"
                aria-label={`Remove ${item.name}`}
              >
                <FaXmark className="h-2.5 w-2.5" />
              </button>
            </span>
          ))}
          <input
            type="text"
            role="combobox"
            aria-autocomplete="list"
            aria-expanded={isPopupOpen}
            aria-controls={isPopupOpen ? suggestionsId : undefined}
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value)
              setShowDropdown(true)
            }}
            onFocus={() => setShowDropdown(true)}
            onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
            placeholder={selectedItems.length > 0 ? '' : `Search ${label.toLowerCase()}...`}
            aria-label={`Search ${label.toLowerCase()}...`}
            className="min-w-[120px] flex-1 bg-transparent text-sm outline-none placeholder:text-gray-400 dark:text-gray-200"
          />
        </div>

        {isPopupOpen && (
          <div
            id={suggestionsId}
            role={listboxRole}
            aria-label={`${label} suggestions`}
            className="absolute z-[1000] mt-1 w-full rounded-md border border-gray-200 bg-white p-1 shadow-lg dark:border-gray-600 dark:bg-[#2a2a2a]"
          >
            {renderSuggestions()}
          </div>
        )}
      </div>
    </div>
  )
}

function FrequencySelector({
  hasActiveSubscription,
  frequency,
  setFrequency,
}: Readonly<{
  hasActiveSubscription: boolean
  frequency: string
  setFrequency: (f: 'weekly' | 'monthly') => void
}>) {
  return (
    <SecondaryCard>
      <h2 className="mb-4 text-xl font-semibold">
        {hasActiveSubscription ? 'Frequency' : 'Choose Frequency'}
      </h2>
      <div className="flex gap-3">
        {(['weekly', 'monthly'] as const).map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => setFrequency(option)}
            className={`flex cursor-pointer items-center gap-3 rounded-md border px-5 py-3 text-sm font-medium transition-all ${
              frequency === option
                ? 'border-[#1D7BD7]/40 bg-[#1D7BD7]/10 text-[#1D7BD7]'
                : 'border-gray-200 text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:text-gray-400 dark:hover:border-gray-600'
            }`}
          >
            <div
              className={`flex h-4 w-4 items-center justify-center rounded-full border-2 transition-colors ${
                frequency === option ? 'border-[#1D7BD7]' : 'border-gray-300 dark:border-gray-600'
              }`}
            >
              {frequency === option && <div className="h-2 w-2 rounded-full bg-[#1D7BD7]" />}
            </div>
            {option.charAt(0).toUpperCase() + option.slice(1)}
          </button>
        ))}
      </div>
    </SecondaryCard>
  )
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
      {hasActiveSubscription ? (
        <SecondaryCard>
          <div className="flex items-start gap-3">
            <FaBell className="mt-0.5 text-green-600 dark:text-green-400" />
            <div>
              <h2 className="font-semibold text-green-800 dark:text-green-300">
                Subscription Active
              </h2>
              <p className="mt-1 text-sm text-green-700 dark:text-green-400">
                You are currently receiving <strong>{subscription?.frequency}</strong> digest
                emails.
              </p>
            </div>
          </div>
        </SecondaryCard>
      ) : (
        <SecondaryCard>
          <div className="flex items-start gap-3">
            <FaBellSlash className="mt-0.5 text-gray-500 dark:text-gray-400" />
            <div>
              <h2 className="font-semibold text-gray-700 dark:text-gray-300">Not Subscribed</h2>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Subscribe to get curated OWASP community updates delivered to your inbox.
              </p>
            </div>
          </div>
        </SecondaryCard>
      )}

      <FrequencySelector
        hasActiveSubscription={hasActiveSubscription}
        frequency={frequency}
        setFrequency={setFrequency}
      />

      <SecondaryCard>
        <h2 className="mb-4 text-xl font-semibold">Content Preferences</h2>
        <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
          Choose which types of OWASP content to include in your snapshot digests.
        </p>
        <ContentToggleGrid
          fields={SNAPSHOT_CONTENT_FIELDS}
          preferences={preferences}
          onToggle={togglePreference}
        />
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

interface LocalEntityPreference {
  entityType: 'project' | 'chapter' | 'committee'
  entity: EntityItem
  includeIssues: boolean
  includePullRequests: boolean
  includeReleases: boolean
}

interface LocalEntitySubscription {
  id: string | null
  name: string
  frequency: 'weekly' | 'monthly'
  preferences: LocalEntityPreference[]
  isNew: boolean
}

function entityPreferenceFromServer(pref: EntityPreferenceData): LocalEntityPreference | null {
  if (pref.project) {
    return {
      entityType: 'project',
      entity: pref.project,
      includeIssues: pref.includeIssues,
      includePullRequests: pref.includePullRequests,
      includeReleases: pref.includeReleases,
    }
  }
  if (pref.chapter) {
    return {
      entityType: 'chapter',
      entity: pref.chapter,
      includeIssues: pref.includeIssues,
      includePullRequests: pref.includePullRequests,
      includeReleases: pref.includeReleases,
    }
  }
  if (pref.committee) {
    return {
      entityType: 'committee',
      entity: pref.committee,
      includeIssues: pref.includeIssues,
      includePullRequests: pref.includePullRequests,
      includeReleases: pref.includeReleases,
    }
  }
  return null
}

function EntityPreferenceCard({
  preference,
  onToggle,
  onRemove,
}: Readonly<{
  preference: LocalEntityPreference
  onToggle: (key: EntityContentKey) => void
  onRemove: () => void
}>) {
  const typeLabel = preference.entityType.charAt(0).toUpperCase() + preference.entityType.slice(1)
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200">
            {preference.entity.name}
          </h4>
          <span className="text-xs text-gray-400">{typeLabel}</span>
        </div>
        <button
          type="button"
          onClick={onRemove}
          className="cursor-pointer rounded-sm p-1 text-gray-400 hover:bg-gray-100 hover:text-red-500 dark:hover:bg-gray-700 dark:hover:text-red-400"
          aria-label={`Remove ${preference.entity.name}`}
        >
          <FaXmark className="h-3.5 w-3.5" />
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {ENTITY_CONTENT_FIELDS.map(({ key, label }) => {
          const isOn = preference[key]
          return (
            <button
              key={key}
              type="button"
              onClick={() => onToggle(key)}
              className={`flex cursor-pointer items-center gap-2 rounded-md border px-3 py-1.5 text-xs font-medium transition-all ${
                isOn
                  ? 'border-[#1D7BD7]/40 bg-[#1D7BD7]/10 text-[#1D7BD7]'
                  : 'border-gray-200 text-gray-500 hover:border-gray-300 dark:border-gray-700 dark:text-gray-400 dark:hover:border-gray-600'
              }`}
            >
              <span>{label}</span>
              <div
                className={`flex h-3.5 w-6 shrink-0 items-center rounded-full p-0.5 transition-colors ${
                  isOn ? 'bg-[#1D7BD7]' : 'bg-gray-300 dark:bg-gray-600'
                }`}
              >
                <div
                  className={`h-2.5 w-2.5 rounded-full bg-white shadow-sm transition-transform ${
                    isOn ? 'translate-x-2.5' : 'translate-x-0'
                  }`}
                />
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}

function EntitySubscriptionCard({
  subscription,
  onSave,
  onUnsubscribe,
  onTrashDelete,
  onReactivate,
  isSaving,
  isActive = true,
}: Readonly<{
  subscription: LocalEntitySubscription
  onSave: (sub: LocalEntitySubscription) => void
  onUnsubscribe?: (sub: LocalEntitySubscription) => void
  onTrashDelete?: (sub: LocalEntitySubscription) => void
  onReactivate?: (sub: LocalEntitySubscription) => void
  isSaving: boolean
  isActive?: boolean
}>) {
  const [localSub, setLocalSub] = useState(subscription)
  const [activeEntityType, setActiveEntityType] = useState<'project' | 'chapter' | 'committee'>(
    'project'
  )
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showUnsubscribeModal, setShowUnsubscribeModal] = useState(false)

  useEffect(() => {
    setLocalSub(subscription)
  }, [subscription])

  const handleNameChange = (name: string) => {
    setLocalSub((prev) => ({ ...prev, name }))
  }

  const handleFrequencyChange = (frequency: 'weekly' | 'monthly') => {
    setLocalSub((prev) => ({ ...prev, frequency }))
  }

  const handleAddEntity = (item: EntityItem) => {
    setLocalSub((prev) => {
      if (
        prev.preferences.some((p) => p.entity.id === item.id && p.entityType === activeEntityType)
      )
        return prev
      return {
        ...prev,
        preferences: [
          ...prev.preferences,
          {
            entityType: activeEntityType,
            entity: item,
            includeIssues: true,
            includePullRequests: true,
            includeReleases: true,
          },
        ],
      }
    })
  }

  const handleRemoveEntity = (entityId: string) => {
    setLocalSub((prev) => ({
      ...prev,
      preferences: prev.preferences.filter((p) => p.entity.id !== entityId),
    }))
  }

  const handleToggleContent = (entityId: string, key: EntityContentKey) => {
    setLocalSub((prev) => ({
      ...prev,
      preferences: prev.preferences.map((p) =>
        p.entity.id === entityId ? { ...p, [key]: !p[key] } : p
      ),
    }))
  }

  const currentEntityTypeConfig = ENTITY_TYPE_OPTIONS.find((o) => o.key === activeEntityType)!
  const selectedItemsForPicker = localSub.preferences
    .filter((p) => p.entityType === activeEntityType)
    .map((p) => p.entity)

  const destructiveButtonStyles =
    'flex items-center gap-2 rounded-md border border-red-500 bg-transparent px-2 py-2 text-red-600 transition-all hover:bg-red-600 hover:text-white dark:text-red-400 dark:hover:bg-red-600 dark:hover:text-white'
  const saveButtonLabel = subscription.isNew ? 'Create Subscription' : 'Save Changes'

  return (
    <SecondaryCard>
      <div>
        {/* Card header with trash icon */}
        <div className="mb-4 flex items-start justify-between">
          <div className="flex-1">
            <label
              htmlFor={`sub-name-${subscription.id || 'new'}`}
              className="mb-1 block text-sm font-semibold text-gray-600 dark:text-gray-300"
            >
              Subscription Name
            </label>
            <input
              id={`sub-name-${subscription.id || 'new'}`}
              type="text"
              value={localSub.name}
              onChange={(e) => handleNameChange(e.target.value)}
              placeholder="e.g. My OWASP Projects"
              className="w-full rounded-lg border border-gray-300 bg-transparent px-3 py-2 text-sm outline-none focus:border-[#1D7BD7] dark:border-gray-600 dark:text-gray-200"
              maxLength={100}
              disabled={!isActive}
            />
          </div>
          {!subscription.isNew && onTrashDelete && (
            <button
              type="button"
              onClick={() => setShowDeleteModal(true)}
              className="mt-1 ml-3 cursor-pointer rounded p-1.5 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20 dark:hover:text-red-400"
              aria-label="Delete subscription permanently"
            >
              <FaTrash className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        <div className="mb-4">
          <h3 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">Frequency</h3>
          <div className="flex gap-3">
            {(['weekly', 'monthly'] as const).map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => handleFrequencyChange(option)}
                className={`flex cursor-pointer items-center gap-3 rounded-md border px-5 py-3 text-sm font-medium transition-all ${
                  localSub.frequency === option
                    ? 'border-[#1D7BD7]/40 bg-[#1D7BD7]/10 text-[#1D7BD7]'
                    : 'border-gray-200 text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:text-gray-400 dark:hover:border-gray-600'
                }`}
              >
                <div
                  className={`flex h-4 w-4 items-center justify-center rounded-full border-2 transition-colors ${
                    localSub.frequency === option
                      ? 'border-[#1D7BD7]'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                >
                  {localSub.frequency === option && (
                    <div className="h-2 w-2 rounded-full bg-[#1D7BD7]" />
                  )}
                </div>
                {option.charAt(0).toUpperCase() + option.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-4">
          <h3 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">
            Add Entities
          </h3>
          <div className="mb-3 flex gap-2">
            {ENTITY_TYPE_OPTIONS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => setActiveEntityType(key)}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition-all ${
                  activeEntityType === key
                    ? 'bg-[#1D7BD7] text-white'
                    : 'bg-gray-200 text-gray-600 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-400 dark:hover:bg-gray-600'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
          <EntityPicker
            label={currentEntityTypeConfig.label}
            selectedItems={selectedItemsForPicker}
            onAdd={handleAddEntity}
            onRemove={handleRemoveEntity}
            searchQuery={currentEntityTypeConfig.searchQuery}
            searchResultKey={currentEntityTypeConfig.searchResultKey}
          />
        </div>

        {localSub.preferences.length > 0 && (
          <div className="mb-4 flex flex-col gap-3">
            {localSub.preferences.map((pref) => (
              <EntityPreferenceCard
                key={`${pref.entityType}-${pref.entity.id}`}
                preference={pref}
                onToggle={(key) => handleToggleContent(pref.entity.id, key)}
                onRemove={() => handleRemoveEntity(pref.entity.id)}
              />
            ))}
          </div>
        )}

        {/* Card footer buttons */}
        <div className="flex justify-end gap-3">
          {isActive ? (
            <>
              {!subscription.isNew && onUnsubscribe && (
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
                onClick={() => onSave(localSub)}
                isDisabled={isSaving || localSub.preferences.length === 0}
              >
                <FaFloppyDisk />
                {isSaving ? 'Saving...' : saveButtonLabel}
              </ActionButton>
            </>
          ) : (
            onReactivate && (
              <ActionButton onClick={() => onReactivate(subscription)} isDisabled={isSaving}>
                <FaBell />
                {isSaving ? 'Subscribing...' : 'Subscribe'}
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
              Are you sure you want to permanently delete &quot;
              {localSub.name || 'this subscription'}&quot;? All entity preferences will be removed
              and this cannot be undone.
            </p>
          </ModalBody>
          <ModalFooter className="flex justify-end gap-3 border-t border-gray-200 px-5 py-4 dark:border-gray-700">
            <ActionButton onClick={() => setShowDeleteModal(false)}>Cancel</ActionButton>
            <Button
              onPress={() => {
                setShowDeleteModal(false)
                onTrashDelete?.(subscription)
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
                onUnsubscribe?.(subscription)
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
  const [showCreateForm, setShowCreateForm] = useState(false)

  const { data, loading, error, refetch } = useQuery<{
    myEntitySubscriptions?: EntitySubscriptionData[]
  }>(GET_MY_ENTITY_SUBSCRIPTIONS, {
    skip: status !== 'authenticated',
    errorPolicy: 'all',
  })

  const subscriptions = data?.myEntitySubscriptions ?? []
  const activeCount = subscriptions.filter((s) => s.isActive).length
  const canCreateMore = activeCount < MAX_ENTITY_SUBSCRIPTIONS

  const [createEntitySubscription, { loading: creating }] = useMutation<{
    createEntitySubscription: MutationResponse
  }>(CREATE_ENTITY_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.createEntitySubscription
      if (result.ok) {
        addToast({
          title: 'Created!',
          description: 'Entity subscription created successfully.',
          color: 'success',
        })
        setShowCreateForm(false)
        refetch()
      } else {
        addToast({ title: 'Error', description: result.message, color: 'danger' })
      }
    },
    onError: () => {
      addToast({
        title: 'Error',
        description: 'Failed to create entity subscription.',
        color: 'danger',
      })
    },
  })

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

  const isMutating = creating || updating || cancelling || deleting || reactivating

  const handleSave = (sub: LocalEntitySubscription) => {
    const entityPreferences = sub.preferences.map((p) => ({
      entityType: p.entityType,
      entityId: decodeRelayId(p.entity.id),
      includeIssues: p.includeIssues,
      includePullRequests: p.includePullRequests,
      includeReleases: p.includeReleases,
    }))

    if (sub.isNew) {
      createEntitySubscription({
        variables: {
          inputData: {
            name: sub.name.trim(),
            frequency: sub.frequency,
            entityPreferences,
          },
        },
      })
    } else {
      updateEntitySubscription({
        variables: {
          subscriptionId: decodeRelayId(sub.id!),
          inputData: {
            name: sub.name.trim(),
            frequency: sub.frequency,
            entityPreferences,
          },
        },
      })
    }
  }

  const handleUnsubscribe = (sub: LocalEntitySubscription) => {
    if (sub.id) {
      cancelEntitySubscription({
        variables: { subscriptionId: decodeRelayId(sub.id) },
      })
    }
  }

  const handleTrashDelete = (sub: LocalEntitySubscription) => {
    if (sub.id) {
      deleteEntitySubscription({
        variables: { subscriptionId: decodeRelayId(sub.id) },
      })
    }
  }

  const handleReactivate = (sub: LocalEntitySubscription) => {
    if (sub.id) {
      reactivateEntitySubscription({
        variables: { subscriptionId: decodeRelayId(sub.id) },
      })
    }
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

  const newSubscription: LocalEntitySubscription = {
    id: null,
    name: '',
    frequency: 'weekly',
    preferences: [],
    isNew: true,
  }

  return (
    <>
      <SecondaryCard>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Entity Subscriptions</h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Subscribe to specific projects, chapters, or committees.{' '}
              <span className="font-medium">
                {activeCount}/{MAX_ENTITY_SUBSCRIPTIONS} subscriptions used.
              </span>
            </p>
          </div>
          {!showCreateForm && (
            <ActionButton
              onClick={() => setShowCreateForm(true)}
              isDisabled={!canCreateMore}
              tooltipLabel={
                canCreateMore ? 'Create new subscription' : 'Maximum subscriptions reached'
              }
            >
              <FaPlus />
              New
            </ActionButton>
          )}
        </div>
      </SecondaryCard>

      {showCreateForm && (
        <div>
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-lg font-semibold">New Entity Subscription</h3>
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="cursor-pointer rounded-sm p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              aria-label="Cancel creation"
            >
              <FaXmark className="h-4 w-4" />
            </button>
          </div>
          <EntitySubscriptionCard
            subscription={newSubscription}
            onSave={handleSave}
            isSaving={creating}
          />
        </div>
      )}

      {/* Active subscriptions */}
      {subscriptions
        .filter((s) => s.isActive)
        .map((sub) => {
          const localSub: LocalEntitySubscription = {
            id: sub.id,
            name: sub.name,
            frequency: sub.frequency as 'weekly' | 'monthly',
            preferences: sub.entityPreferences
              .map(entityPreferenceFromServer)
              .filter((p): p is LocalEntityPreference => p !== null),
            isNew: false,
          }
          return (
            <EntitySubscriptionCard
              key={sub.id}
              subscription={localSub}
              onSave={handleSave}
              onUnsubscribe={handleUnsubscribe}
              onTrashDelete={handleTrashDelete}
              isSaving={isMutating}
              isActive
            />
          )
        })}

      {/* Inactive subscriptions */}
      {subscriptions
        .filter((s) => !s.isActive)
        .map((sub) => {
          const localSub: LocalEntitySubscription = {
            id: sub.id,
            name: sub.name,
            frequency: sub.frequency as 'weekly' | 'monthly',
            preferences: sub.entityPreferences
              .map(entityPreferenceFromServer)
              .filter((p): p is LocalEntityPreference => p !== null),
            isNew: false,
          }
          return (
            <EntitySubscriptionCard
              key={sub.id}
              subscription={localSub}
              onSave={handleSave}
              onReactivate={handleReactivate}
              onTrashDelete={handleTrashDelete}
              isSaving={isMutating}
              isActive={false}
            />
          )
        })}

      {subscriptions.length === 0 && !showCreateForm && (
        <SecondaryCard>
          <div className="py-4 text-center text-gray-500 dark:text-gray-400">
            <p>No entity subscriptions yet.</p>
            <p className="mt-1 text-sm">Click &quot;New&quot; to create your first subscription.</p>
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
  const [activeSubTab, setActiveSubTab] = useState<SubTabKey>('snapshot')

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
