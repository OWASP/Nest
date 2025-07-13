'use client'

import { useMutation, useQuery } from '@apollo/client'
import {
  faSpinner,
  faKey,
  faPlus,
  faTrash,
  faCopy,
  faEye,
  faEyeSlash,
  faInfoCircle,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/modal'
import { Input } from '@heroui/react'
import { addToast } from '@heroui/toast'
import { format, addDays } from 'date-fns'
import { useState } from 'react'
import { CREATE_API_KEY, GET_API_KEYS, REVOKE_API_KEY } from 'server/queries/apiKeyQueries'
import type { ApiKey } from 'types/apikey'
import SecondaryCard from 'components/SecondaryCard'
import { ApiKeysSkeleton } from 'components/skeletons/ApiKeySkelton'

export default function Page() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyExpiry, setNewKeyExpiry] = useState('')
  const [showNewKey, setShowNewKey] = useState(false)
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<string | null>(null)
  const [includeRevoked, setIncludeRevoked] = useState(false)
  const [keyToRevoke, setKeyToRevoke] = useState<ApiKey | null>(null)

  const { loading, error, data, refetch } = useQuery(GET_API_KEYS, {
    variables: { includeRevoked },
    notifyOnNetworkStatusChange: true,
    errorPolicy: 'all',
  })

  const [createApiKey, { loading: createLoading }] = useMutation(CREATE_API_KEY, {
    onCompleted: (data) => {
      const result = data.createApiKey
      if (!result?.ok) {
        addToast({
          title: 'Error',
          description: result.message || 'Failed to create API key',
          color: 'danger',
        })
        return
      }
      setNewlyCreatedKey(result.rawKey)
      addToast({
        title: 'API Key Created',
        description: "Copy it now - you won't see it again!",
        color: 'success',
      })
      refetch()
    },
    onError: () => {
      addToast({ title: 'Error', description: 'Failed to create API key', color: 'danger' })
    },
  })

  const [revokeApiKey] = useMutation(REVOKE_API_KEY, {
    onCompleted: () => {
      addToast({ title: 'Success', description: 'API key revoked', color: 'success' })
      refetch()
    },
    onError: () => {
      addToast({ title: 'Error', description: 'Failed to revoke API key', color: 'danger' })
    },
  })

  const activeKeyCount = data?.activeApiKeyCount || 0
  const canCreateNewKey = activeKeyCount < 5
  const defaultExpiryDate = format(addDays(new Date(), 30), 'yyyy-MM-dd')

  const handleCreateKey = () => {
    if (!newKeyName.trim()) {
      addToast({ title: 'Error', description: 'Please provide a name', color: 'danger' })
      return
    }
    const variables: { name: string; expiresAt?: Date } = { name: newKeyName.trim() }
    if (newKeyExpiry) variables.expiresAt = new Date(newKeyExpiry)
    createApiKey({ variables })
  }

  const handleCopyKey = () => {
    if (newlyCreatedKey) {
      navigator.clipboard.writeText(newlyCreatedKey)
      addToast({ title: 'Copied', description: 'API key copied to clipboard', color: 'success' })
    }
  }

  const openCreateModal = () => {
    setIsCreateModalOpen(true)
    setNewKeyExpiry(defaultExpiryDate)
  }

  const closeCreateModal = () => {
    setIsCreateModalOpen(false)
    setNewKeyName('')
    setNewKeyExpiry('')
    setNewlyCreatedKey(null)
    setShowNewKey(false)
  }

  const handleRevokeKey = async () => {
    if (keyToRevoke) {
      await revokeApiKey({ variables: { publicId: keyToRevoke.publicId } })
      setKeyToRevoke(null)
    }
  }

  if (loading && !data) {
    return <ApiKeysSkeleton />
  }

  return (
    <div className="flex min-h-[80vh] flex-col items-center p-8">
      <div className="w-full max-w-4xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold">API Key Management</h1>
          <p className="mt-2 text-gray-500 dark:text-gray-400">
            Create and manage API keys for programmatic access to the API.
          </p>
        </div>

        <SecondaryCard>
          <div className="flex items-start gap-3">
            <FontAwesomeIcon
              icon={faInfoCircle}
              className="mt-0.5 text-blue-600 dark:text-blue-400"
            />
            <div>
              <h3 className="font-semibold text-blue-800 dark:text-blue-300">API Key Limits</h3>
              <p className="mt-1 text-sm text-blue-700 dark:text-blue-400">
                You can have a maximum of <strong>5 active API keys</strong> at any time. Currently:{' '}
                <strong>{activeKeyCount}/5 active keys</strong>.
                {!canCreateNewKey && (
                  <span className="mt-1 block">
                    To create a new key, you need to revoke one of your existing active keys first.
                  </span>
                )}
              </p>
            </div>
          </div>
        </SecondaryCard>

        <SecondaryCard>
          <div className="mb-4 flex items-center gap-3">
            <FontAwesomeIcon icon={faKey} className="text-gray-600 dark:text-gray-400" />
            <h2 className="text-xl font-semibold">Your API Keys</h2>
          </div>

          <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="show-revoked"
                checked={includeRevoked}
                onChange={() => setIncludeRevoked(!includeRevoked)}
                className="mr-2 h-4 w-4 rounded border-gray-300"
              />
              <label htmlFor="show-revoked" className="text-sm text-gray-600 dark:text-gray-400">
                Show revoked keys
              </label>
            </div>
            <Button
              onPress={openCreateModal}
              isDisabled={!canCreateNewKey || includeRevoked}
              className="rounded-sm bg-black font-medium text-white transition-colors hover:bg-gray-900/90 disabled:bg-gray-300 disabled:text-gray-500"
            >
              <FontAwesomeIcon icon={faPlus} className="mr-1" />
              Create New Key ({activeKeyCount}/5)
            </Button>
          </div>

          {error ? (
            <div className="rounded-md bg-red-50 p-4 text-red-700 dark:bg-red-900/20 dark:text-red-400">
              Error loading API keys
            </div>
          ) : loading ? (
            <div className="space-y-4">
              <ApiKeysSkeleton />
            </div>
          ) : !data?.apiKeys?.length ? (
            <div className="rounded-md bg-gray-50 p-8 text-center text-gray-500 dark:bg-gray-800/50 dark:text-gray-400">
              You don't have any API keys yet.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="py-3 text-left font-semibold">Name</th>
                    <th className="py-3 text-left font-semibold">ID</th>
                    <th className="py-3 text-left font-semibold">Created</th>
                    <th className="py-3 text-left font-semibold">Expires</th>
                    <th className="py-3 text-left font-semibold">Status</th>
                    <th className="py-3 text-right font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.apiKeys.map((key: ApiKey) => (
                    <tr
                      key={key.publicId}
                      className={`border-b border-gray-200 dark:border-gray-700 ${key.isRevoked ? 'opacity-60' : ''}`}
                    >
                      <td className="py-3">{key.name}</td>
                      <td className="py-3 font-mono text-sm">{key.publicId}</td>
                      <td className="py-3">{format(new Date(key.createdAt), 'PP')}</td>
                      <td className="py-3">
                        {key.expiresAt ? format(new Date(key.expiresAt), 'PP') : 'Never'}
                      </td>
                      <td>
                        <span
                          className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                            key.isRevoked
                              ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                              : 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                          }`}
                        >
                          {key.isRevoked ? 'Revoked' : 'Active'}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        {!key.isRevoked && (
                          <Button
                            variant="light"
                            size="sm"
                            onPress={() => setKeyToRevoke(key)}
                            className="text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                          >
                            <FontAwesomeIcon icon={faTrash} />
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </SecondaryCard>

        <SecondaryCard>
          <h2 className="mb-4 text-xl font-semibold">API Key Usage</h2>
          <div className="space-y-4">
            <p>
              Include your API key in the{' '}
              <code className="mx-1 rounded bg-gray-100 px-1 py-0.5 font-mono dark:bg-gray-800">
                X-API-Key
              </code>{' '}
              header:
            </p>
            <div className="rounded-md bg-gray-100 p-4 font-mono text-sm dark:bg-gray-800">
              <pre>X-API-Key: YOUR_API_KEY</pre>
            </div>
            <div className="rounded-md border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-900/30 dark:bg-yellow-900/10">
              <p className="text-yellow-800 dark:text-yellow-400">
                <strong>Important:</strong> Keep your API keys secure and never share them publicly.
                If a key is compromised, revoke it immediately and create a new one.
              </p>
            </div>
          </div>
        </SecondaryCard>
      </div>

      <Modal isOpen={isCreateModalOpen} onClose={closeCreateModal} size="lg">
        <ModalContent>
          <ModalHeader>Create New API Key</ModalHeader>
          <ModalBody>
            {newlyCreatedKey ? (
              <div className="space-y-4">
                <div className="rounded-md bg-green-50 p-4 dark:bg-green-900/20">
                  <p className="font-medium text-green-800 dark:text-green-400">
                    API key created successfully!
                  </p>
                  <p className="text-sm text-yellow-800 dark:text-yellow-400">
                    Important: Copy it now as you won't be able to see it again.
                  </p>
                </div>
                <div>
                  <label htmlFor="api-key" className="mb-2 block text-sm font-medium">
                    API Key
                  </label>
                  <div className="flex gap-2">
                    <Input
                      id="api-key"
                      type={showNewKey ? 'text' : 'password'}
                      value={newlyCreatedKey}
                      readOnly
                      className="flex-1 font-mono"
                    />
                    <Button
                      variant="light"
                      size="sm"
                      onPress={() => setShowNewKey(!showNewKey)}
                      isIconOnly
                    >
                      <FontAwesomeIcon icon={showNewKey ? faEyeSlash : faEye} />
                    </Button>
                    <Button variant="bordered" onPress={handleCopyKey} size="sm">
                      <FontAwesomeIcon icon={faCopy} className="mr-2" />
                      Copy
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label htmlFor="api-key-name" className="mb-2 block text-sm font-medium">
                    API Key Name
                  </label>
                  <Input
                    id="api-key-name"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    placeholder="e.g., Development, Production, CI/CD"
                  />
                </div>
                <div>
                  <label htmlFor="expiration-date" className="mb-2 block text-sm font-medium">
                    Expiration Date
                  </label>
                  <Input
                    id="expiration-date"
                    type="date"
                    value={newKeyExpiry}
                    onChange={(e) => setNewKeyExpiry(e.target.value)}
                    min={format(new Date(), 'yyyy-MM-dd')}
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Default: 30 days from today ({format(addDays(new Date(), 30), 'PP')}).
                  </p>
                  <div className="mt-2 flex gap-2">
                    <Button
                      size="sm"
                      variant="bordered"
                      onPress={() => setNewKeyExpiry(format(addDays(new Date(), 90), 'yyyy-MM-dd'))}
                    >
                      90 days
                    </Button>
                    <Button
                      size="sm"
                      variant="bordered"
                      onPress={() =>
                        setNewKeyExpiry(format(addDays(new Date(), 365), 'yyyy-MM-dd'))
                      }
                    >
                      1 year
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </ModalBody>
          <ModalFooter>
            {newlyCreatedKey ? (
              <Button color="primary" onPress={closeCreateModal}>
                Done
              </Button>
            ) : (
              <>
                <Button variant="light" onPress={closeCreateModal}>
                  Cancel
                </Button>
                <Button
                  color="primary"
                  onPress={handleCreateKey}
                  isDisabled={createLoading || !newKeyName.trim() || !newKeyExpiry}
                >
                  {createLoading && <FontAwesomeIcon icon={faSpinner} spin className="mr-2" />}
                  Create API Key
                </Button>
              </>
            )}
          </ModalFooter>
        </ModalContent>
      </Modal>

      <Modal isOpen={!!keyToRevoke} onClose={() => setKeyToRevoke(null)} size="md">
        <ModalContent>
          <ModalHeader>Revoke API Key</ModalHeader>
          <ModalBody>
            <p>
              Are you sure you want to revoke the key named <strong>"{keyToRevoke?.name}"</strong>?
              This action cannot be undone and will immediately disable the key.
            </p>
            <div className="mt-3 rounded-md bg-yellow-50 p-3 dark:bg-yellow-900/20">
              <p className="text-sm text-yellow-800 dark:text-yellow-400">
                <FontAwesomeIcon icon={faInfoCircle} className="mr-2" />
                After revoking this key, you'll be able to create a new one if needed.
              </p>
            </div>
          </ModalBody>
          <ModalFooter>
            <Button variant="light" onPress={() => setKeyToRevoke(null)}>
              Cancel
            </Button>
            <Button color="danger" onPress={handleRevokeKey}>
              Revoke Key
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  )
}
