'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Modal, ModalBody, ModalContent, ModalFooter, ModalHeader } from '@heroui/modal'
import { addToast } from '@heroui/toast'
import { Tooltip } from '@heroui/tooltip'
import Link from 'next/link'
import { useSession } from 'next-auth/react'
import { useCallback, useState } from 'react'
import { FaBell, FaBellSlash, FaCheck } from 'react-icons/fa6'

import {
  CREATE_ENTITY_SUBSCRIPTION,
  GET_MY_ENTITY_SUBSCRIPTIONS,
} from 'server/queries/subscriptionQueries'
import { decodeRelayId } from 'utils/decodeRelayId'

const MAX_ENTITY_SUBSCRIPTIONS = 5

interface EntitySubscriptionData {
  id: string
  frequency: string
  isActive: boolean
  chapter?: { id: string; name: string } | null
  committee?: { id: string; name: string } | null
  project?: { id: string; name: string } | null
}

interface SubscribeButtonProps {
  entityType: 'project' | 'chapter' | 'committee'
  entityId: string
  entityName: string
}

const CONTENT_TOGGLES = [
  { key: 'includeIssues' as const, label: 'Issues' },
  { key: 'includePullRequests' as const, label: 'Pull Requests' },
  { key: 'includeReleases' as const, label: 'Releases' },
]

export default function SubscribeButton({
  entityType,
  entityId,
  entityName,
}: Readonly<SubscribeButtonProps>) {
  const { status } = useSession()
  const [showModal, setShowModal] = useState(false)
  const [frequency, setFrequency] = useState<'weekly' | 'monthly'>('weekly')
  const [toggles, setToggles] = useState({
    includeIssues: true,
    includePullRequests: true,
    includeReleases: true,
  })

  const { data, refetch } = useQuery<{
    myEntitySubscriptions: EntitySubscriptionData[]
  }>(GET_MY_ENTITY_SUBSCRIPTIONS, {
    skip: status !== 'authenticated',
    errorPolicy: 'all',
  })

  const subscriptions = data?.myEntitySubscriptions ?? []
  const activeCount = subscriptions.filter((s) => s.isActive).length
  const decodedEntityId = decodeRelayId(entityId)

  const existingSub = subscriptions.find((sub) => {
    const entityField = sub[entityType] as { id: string } | null | undefined
    if (!entityField) return false
    return decodeRelayId(entityField.id) === decodedEntityId
  })

  const isSubscribed = existingSub?.isActive === true
  const hasInactiveSub = existingSub != null && !existingSub.isActive

  const [createSubscription, { loading: creating }] = useMutation<{
    createEntitySubscription: { ok: boolean; message: string }
  }>(CREATE_ENTITY_SUBSCRIPTION, {
    onCompleted: (data) => {
      const result = data.createEntitySubscription
      if (result.ok) {
        addToast({
          title: 'Subscribed!',
          description: `You are now subscribed to ${entityName}.`,
          color: 'success',
        })
        setShowModal(false)
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

  const handleSubscribe = useCallback(() => {
    createSubscription({
      variables: {
        inputData: {
          entityType,
          entityId: decodedEntityId,
          frequency,
          ...toggles,
        },
      },
    })
  }, [createSubscription, entityType, decodedEntityId, frequency, toggles])

  const handleToggle = useCallback((key: keyof typeof toggles) => {
    setToggles((prev) => ({ ...prev, [key]: !prev[key] }))
  }, [])

  if (status !== 'authenticated') return null

  const canSubscribe = activeCount < MAX_ENTITY_SUBSCRIPTIONS

  const renderButton = () => {
    if (isSubscribed) {
      return (
        <Link
          href="/settings?tab=entity"
          className="flex h-10 cursor-pointer items-center gap-1.5 rounded-md border border-green-500/40 bg-green-500/10 px-2 py-2 text-sm font-medium text-green-600 transition-all hover:bg-green-500/20 dark:text-green-400"
          aria-label={`Subscribed to ${entityName} — click to manage`}
        >
          <FaCheck className="h-3 w-3" />
          Subscribed
        </Link>
      )
    }

    if (hasInactiveSub) {
      return (
        <Link
          href="/settings?tab=entity"
          className="flex h-10 cursor-pointer items-center gap-1.5 rounded-md border border-amber-500/40 bg-amber-500/10 px-2 py-2 text-sm font-medium text-amber-600 transition-all hover:bg-amber-500/20 dark:text-amber-400"
          aria-label={`Manage inactive subscription for ${entityName}`}
        >
          <FaBellSlash className="h-3 w-3" />
          Manage
        </Link>
      )
    }

    if (canSubscribe) {
      return (
        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="flex h-10 cursor-pointer items-center gap-1.5 rounded-md border border-[#1D7BD7] px-2 py-2 text-sm font-medium text-[#1D7BD7] transition-all hover:bg-[#1D7BD7] hover:text-white"
          aria-label={`Subscribe to ${entityName}`}
        >
          <FaBell className="h-3 w-3" />
          Subscribe
        </button>
      )
    }

    return (
      <Tooltip content={`Maximum ${MAX_ENTITY_SUBSCRIPTIONS} subscriptions reached`}>
        <button
          type="button"
          disabled
          className="flex h-10 cursor-not-allowed items-center gap-1.5 rounded-md border border-gray-300 px-2 py-2 text-sm font-medium text-gray-400 opacity-50 dark:border-gray-600"
          aria-label="Subscription limit reached"
        >
          <FaBell className="h-3 w-3" />
          Subscribe
        </button>
      </Tooltip>
    )
  }

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

          <ModalBody className="space-y-5 px-5 py-4">
            <div>
              <h3 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">
                Frequency
              </h3>
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
              <h3 className="mb-2 text-sm font-semibold text-gray-600 dark:text-gray-300">
                Content
              </h3>
              <div className="flex flex-wrap gap-2">
                {CONTENT_TOGGLES.map(({ key, label }) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => handleToggle(key)}
                    aria-pressed={toggles[key]}
                    className={`flex cursor-pointer items-center gap-2 rounded-md border px-3 py-2 text-sm font-medium transition-all ${
                      toggles[key]
                        ? 'border-[#1D7BD7]/40 bg-[#1D7BD7]/10 text-[#1D7BD7]'
                        : 'border-gray-200 text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:text-gray-400 dark:hover:border-gray-600'
                    }`}
                  >
                    <span>{label}</span>
                    <div
                      className={`flex h-4 w-7 shrink-0 items-center rounded-full p-0.5 transition-colors ${
                        toggles[key] ? 'bg-[#1D7BD7]' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <div
                        className={`h-3 w-3 rounded-full bg-white shadow-sm transition-transform ${
                          toggles[key] ? 'translate-x-3' : 'translate-x-0'
                        }`}
                      />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </ModalBody>

          <ModalFooter className="flex justify-end gap-3 border-t border-gray-200 px-5 py-4 dark:border-gray-700">
            <Button
              variant="bordered"
              onPress={() => setShowModal(false)}
              className="flex items-center gap-2 rounded-md border border-gray-300 bg-transparent px-3 py-2 text-gray-600 transition-all hover:bg-gray-100 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700"
            >
              Cancel
            </Button>
            <Button
              onPress={handleSubscribe}
              isDisabled={creating}
              className="flex items-center gap-2 rounded-md border border-[#1D7BD7] bg-transparent px-3 py-2 text-[#1D7BD7] transition-all hover:bg-[#1D7BD7] hover:text-white dark:hover:text-white"
            >
              <FaBell className="h-3 w-3" />
              {creating ? 'Subscribing...' : 'Subscribe'}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}
