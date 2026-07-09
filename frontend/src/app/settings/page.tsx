'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/modal'
import { addToast } from '@heroui/toast'
import debounce from 'lodash/debounce'
import { useSession } from 'next-auth/react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { FaBell, FaBellSlash, FaFloppyDisk, FaXmark } from 'react-icons/fa6'

import { SEARCH_CHAPTERS } from 'server/queries/chapterQueries'
import { SEARCH_PROJECTS } from 'server/queries/projectQueries'
import {
  CANCEL_SNAPSHOT_SUBSCRIPTION,
  CREATE_SNAPSHOT_SUBSCRIPTION,
  GET_MY_SUBSCRIPTION,
  UPDATE_SNAPSHOT_SUBSCRIPTION,
} from 'server/queries/subscriptionQueries'
import ActionButton from 'components/ActionButton'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const GLOBAL_CONTENT_FIELDS = [
  { key: 'includeChapters', label: 'Chapters' },
  { key: 'includeEvents', label: 'Events' },
  { key: 'includePosts', label: 'Posts' },
  { key: 'includeUsers', label: 'Users' },
] as const

type GlobalContentKey = (typeof GLOBAL_CONTENT_FIELDS)[number]['key']

const PROJECT_CONTENT_FIELDS = [
  { key: 'includeIssues', label: 'Issues' },
  { key: 'includePullRequests', label: 'Pull Requests' },
  { key: 'includeReleases', label: 'Releases' },
] as const

type ProjectContentKey = (typeof PROJECT_CONTENT_FIELDS)[number]['key']

interface EntityItem {
  id: string
  name: string
}

interface ProjectPreference {
  project: EntityItem
  includeIssues: boolean
  includePullRequests: boolean
  includeReleases: boolean
}

interface SubscriptionData {
  id: string
  frequency: string
  isActive: boolean
  includeChapters: boolean
  includeEvents: boolean
  includePosts: boolean
  includeUsers: boolean
  projectPreferences: ProjectPreference[]
  chapters: EntityItem[]
  createdAt: string
  updatedAt: string
}

interface GetSubscriptionResponse {
  mySubscription?: SubscriptionData | null
}

interface MutationResponse {
  ok: boolean
  message: string
  subscription?: SubscriptionData | null
}

const DEFAULT_GLOBAL_PREFERENCES: Record<GlobalContentKey, boolean> = {
  includeChapters: true,
  includeEvents: true,
  includePosts: true,
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

function ProjectPreferenceCard({
  preference,
  onToggle,
  onRemove,
}: Readonly<{
  preference: ProjectPreference
  onToggle: (key: ProjectContentKey) => void
  onRemove: () => void
}>) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200">
          {preference.project.name}
        </h4>
        <button
          type="button"
          onClick={onRemove}
          className="cursor-pointer rounded-sm p-1 text-gray-400 hover:bg-gray-100 hover:text-red-500 dark:hover:bg-gray-700 dark:hover:text-red-400"
          aria-label={`Remove ${preference.project.name}`}
        >
          <FaXmark className="h-3.5 w-3.5" />
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {PROJECT_CONTENT_FIELDS.map(({ key, label }) => {
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

function GlobalContentPreferences({
  globalPreferences,
  toggleGlobalPreference,
}: Readonly<{
  globalPreferences: Record<GlobalContentKey, boolean>
  toggleGlobalPreference: (key: GlobalContentKey) => void
}>) {
  return (
    <SecondaryCard>
      <h2 className="mb-4 text-xl font-semibold">General Subscriptions</h2>
      <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
        Manage your general OWASP subscriptions.
      </p>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {GLOBAL_CONTENT_FIELDS.map(({ key, label }) => (
          <button
            key={key}
            type="button"
            onClick={() => toggleGlobalPreference(key)}
            className={`flex cursor-pointer items-center justify-between gap-2 rounded-md border px-3 py-2 text-sm font-medium transition-all ${
              globalPreferences[key]
                ? 'border-[#1D7BD7]/40 bg-[#1D7BD7]/10 text-[#1D7BD7]'
                : 'border-gray-200 text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:text-gray-400 dark:hover:border-gray-600'
            }`}
          >
            <span className="truncate">{label}</span>
            <div
              className={`flex h-4 w-7 shrink-0 items-center rounded-full p-0.5 transition-colors ${
                globalPreferences[key] ? 'bg-[#1D7BD7]' : 'bg-gray-300 dark:bg-gray-600'
              }`}
            >
              <div
                className={`h-3 w-3 rounded-full bg-white shadow-sm transition-transform ${
                  globalPreferences[key] ? 'translate-x-3' : 'translate-x-0'
                }`}
              />
            </div>
          </button>
        ))}
      </div>
    </SecondaryCard>
  )
}

function ProjectSubscriptions({
  projectPreferences,
  handleAddProject,
  handleRemoveProject,
  handleToggleProjectContent,
}: Readonly<{
  projectPreferences: ProjectPreference[]
  handleAddProject: (item: EntityItem) => void
  handleRemoveProject: (projectId: string) => void
  handleToggleProjectContent: (projectId: string, key: ProjectContentKey) => void
}>) {
  const selectedProjectItems = projectPreferences.map((p) => p.project)

  return (
    <SecondaryCard>
      <h2 className="mb-2 text-xl font-semibold">Project Subscriptions</h2>
      <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
        Select projects and choose which updates you would like to receive (Issues, Pull Requests,
        Releases). Leave this empty if you don't want project-specific updates.
      </p>

      <EntityPicker
        label="Projects"
        selectedItems={selectedProjectItems}
        onAdd={handleAddProject}
        onRemove={handleRemoveProject}
        searchQuery={SEARCH_PROJECTS}
        searchResultKey="searchProjects"
      />

      {projectPreferences.length > 0 && (
        <div className="mt-4 flex flex-col gap-3">
          {projectPreferences.map((pref) => (
            <ProjectPreferenceCard
              key={pref.project.id}
              preference={pref}
              onToggle={(key) => handleToggleProjectContent(pref.project.id, key)}
              onRemove={() => handleRemoveProject(pref.project.id)}
            />
          ))}
        </div>
      )}
    </SecondaryCard>
  )
}

function ChapterFilters({
  includeChapters,
  selectedChapters,
  handleAddChapter,
  handleRemoveChapter,
}: Readonly<{
  includeChapters: boolean
  selectedChapters: EntityItem[]
  handleAddChapter: (item: EntityItem) => void
  handleRemoveChapter: (id: string) => void
}>) {
  if (!includeChapters) return null

  return (
    <SecondaryCard>
      <h2 className="mb-2 text-xl font-semibold">Chapter Subscriptions</h2>
      <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
        Optionally select specific chapters to follow. Leave empty to receive updates about all
        chapters.
      </p>
      <EntityPicker
        label="Chapters"
        selectedItems={selectedChapters}
        onAdd={handleAddChapter}
        onRemove={handleRemoveChapter}
        searchQuery={SEARCH_CHAPTERS}
        searchResultKey="searchChapters"
      />
    </SecondaryCard>
  )
}

function SubscriptionContent() {
  const { status } = useSession()
  const [frequency, setFrequency] = useState<'weekly' | 'monthly'>('weekly')
  const [globalPreferences, setGlobalPreferences] = useState<Record<GlobalContentKey, boolean>>(
    DEFAULT_GLOBAL_PREFERENCES
  )
  const [projectPreferences, setProjectPreferences] = useState<ProjectPreference[]>([])
  const [selectedChapters, setSelectedChapters] = useState<EntityItem[]>([])

  const { data, loading, error, refetch } = useQuery<GetSubscriptionResponse>(GET_MY_SUBSCRIPTION, {
    skip: status !== 'authenticated',
    errorPolicy: 'all',
  })

  const subscription = data?.mySubscription
  const hasActiveSubscription = subscription?.isActive === true

  useEffect(() => {
    if (subscription?.isActive) {
      setFrequency(subscription.frequency as 'weekly' | 'monthly')
      setGlobalPreferences({
        includeChapters: subscription.includeChapters,
        includeEvents: subscription.includeEvents,
        includePosts: subscription.includePosts,
        includeUsers: subscription.includeUsers,
      })
      setProjectPreferences(subscription.projectPreferences || [])
      setSelectedChapters(subscription.chapters || [])
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
        setGlobalPreferences(DEFAULT_GLOBAL_PREFERENCES)
        setFrequency('weekly')
        setProjectPreferences([])
        setSelectedChapters([])
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

  const toggleGlobalPreference = useCallback((key: GlobalContentKey) => {
    setGlobalPreferences((prev) => {
      const next = { ...prev, [key]: !prev[key] }
      if (key === 'includeChapters' && !next.includeChapters) {
        setSelectedChapters([])
      }
      return next
    })
  }, [])

  const handleAddProject = useCallback((item: EntityItem) => {
    setProjectPreferences((prev) => {
      if (prev.some((p) => p.project.id === item.id)) return prev
      return [
        ...prev,
        {
          project: item,
          includeIssues: true,
          includePullRequests: true,
          includeReleases: true,
        },
      ]
    })
  }, [])

  const handleRemoveProject = useCallback((projectId: string) => {
    setProjectPreferences((prev) => prev.filter((p) => p.project.id !== projectId))
  }, [])

  const handleToggleProjectContent = useCallback((projectId: string, key: ProjectContentKey) => {
    setProjectPreferences((prev) =>
      prev.map((p) => (p.project.id === projectId ? { ...p, [key]: !p[key] } : p))
    )
  }, [])

  const handleAddChapter = useCallback((item: EntityItem) => {
    setSelectedChapters((prev) => [...prev, item])
  }, [])

  const handleRemoveChapter = useCallback((id: string) => {
    setSelectedChapters((prev) => prev.filter((c) => c.id !== id))
  }, [])

  const getMutationVariables = () => ({
    inputData: {
      frequency,
      ...globalPreferences,
      subscribedChapterIds: selectedChapters.map((c) => Number.parseInt(c.id, 10)),
      projectPreferences: projectPreferences.map((p) => ({
        projectId: Number.parseInt(p.project.id, 10),
        includeIssues: p.includeIssues,
        includePullRequests: p.includePullRequests,
        includeReleases: p.includeReleases,
      })),
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
      <GlobalContentPreferences
        globalPreferences={globalPreferences}
        toggleGlobalPreference={toggleGlobalPreference}
      />
      <ProjectSubscriptions
        projectPreferences={projectPreferences}
        handleAddProject={handleAddProject}
        handleRemoveProject={handleRemoveProject}
        handleToggleProjectContent={handleToggleProjectContent}
      />
      <ChapterFilters
        includeChapters={globalPreferences.includeChapters}
        selectedChapters={selectedChapters}
        handleAddChapter={handleAddChapter}
        handleRemoveChapter={handleRemoveChapter}
      />

      <div className="flex justify-end gap-3">
        {hasActiveSubscription && (
          <Button
            variant="bordered"
            onPress={handleCancel}
            isDisabled={cancelling}
            className="flex items-center gap-2 rounded-md border border-red-500 bg-transparent px-2 py-2 text-red-600 transition-all hover:bg-red-600 hover:text-white dark:text-red-400 dark:hover:bg-red-600 dark:hover:text-white"
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
              Are you sure you want to unsubscribe? All your preferences including selected
              projects, content types, and chapter filters will be lost.
            </p>
          </ModalBody>
          <ModalFooter className="flex justify-end gap-3 border-t border-gray-200 px-5 py-4 dark:border-gray-700">
            <ActionButton onClick={() => setShowCancelModal(false)}>Keep Subscription</ActionButton>
            <Button
              onPress={handleConfirmCancel}
              isDisabled={cancelling}
              className="flex items-center gap-2 rounded-md border border-red-500 bg-transparent px-2 py-2 text-red-600 transition-all hover:bg-red-600 hover:text-white dark:text-red-400 dark:hover:bg-red-600 dark:hover:text-white"
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
