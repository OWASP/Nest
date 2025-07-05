'use client'

import { FetchResult, useMutation, useQuery } from '@apollo/client'
import {
  faSpinner,
  faKey,
  faPlus,
  faTrash,
  faCopy,
  faEye,
  faEyeSlash,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/modal'
import { Input } from '@heroui/react'
import { addToast } from '@heroui/toast'
import { format } from 'date-fns/format'
import { useSession } from 'next-auth/react'
import { useEffect, useState, type FC } from 'react'
import { CREATE_API_KEY, GET_API_KEYS, REVOKE_API_KEY } from 'server/queries/apiKeyQueries'
import { ApiKey, ApiKeyPageContentProps, CreateApiKeyResult } from 'types/apikey'
import { userAuthStatus } from 'utils/constants'
import apolloClient from 'utils/helpers/apolloClient'
import SecondaryCard from 'components/SecondaryCard'

const ApiKeyPageContent: FC<ApiKeyPageContentProps> = ({ isGitHubAuthEnabled }) => {
  const { status } = useSession()
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyExpiry, setNewKeyExpiry] = useState('')
  const [showNewKey, setShowNewKey] = useState(false)
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<string | null>(null)
  const [includeRevoked, setIncludeRevoked] = useState(false)
  const [confirmationModal, setConfirmationModal] = useState<{
    isOpen: boolean
    title: string
    message: string
    onConfirm: () => Promise<FetchResult<unknown>>
  } | null>(null)

  const { loading, error, data, refetch } = useQuery(GET_API_KEYS, {
    variables: { includeRevoked },
    skip: status !== userAuthStatus.AUTHENTICATED,
    client: apolloClient,
  })

  useEffect(() => {
    refetch()
  }, [includeRevoked, refetch, status])

  const [createApiKey, { loading: createLoading }] = useMutation(CREATE_API_KEY, {
    onCompleted: (data) => {
      const result = data.createApiKey as CreateApiKeyResult
      setNewlyCreatedKey(result.rawKey)
      addToast({
        description:
          "API key created successfully. Make sure to copy it now as you won't be able to see it again.",
        title: 'API Key Created',
        timeout: 5000,
        shouldShowTimeoutProgress: true,
        color: 'success',
        variant: 'solid',
      })
      refetch()
    },
    onError: (error) => {
      addToast({
        description: `Failed to create API key: ${error.message}`,
        title: 'Error',
        timeout: 5000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
    },
  })

  const [revokeApiKey] = useMutation(REVOKE_API_KEY, {
    onCompleted: () => {
      addToast({
        description: 'API key revoked successfully.',
        title: 'API Key Revoked',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'success',
        variant: 'solid',
      })
      refetch()
    },
    onError: (error) => {
      addToast({
        description: `Failed to revoke API key: ${error.message}`,
        title: 'Error',
        timeout: 5000,
        color: 'danger',
        variant: 'solid',
      })
    },
  })

  const handleCreateKey = () => {
    if (!newKeyName.trim()) {
      addToast({
        description: 'Please provide a name for your API key.',
        title: 'Validation Error',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
      return
    }

    const variables: { name: string; expiresAt?: Date } = {
      name: newKeyName.trim(),
    }

    if (newKeyExpiry) {
      variables.expiresAt = new Date(newKeyExpiry)
    }

    createApiKey({ variables })
  }

  const handleRevokeKey = (keyId: number) => {
    setConfirmationModal({
      isOpen: true,
      title: 'Revoke API Key',
      message: 'Are you sure you want to revoke this API key? This action cannot be undone.',
      onConfirm: () => revokeApiKey({ variables: { keyId } }),
    })
  }

  const handleCopyKey = () => {
    if (newlyCreatedKey) {
      navigator.clipboard.writeText(newlyCreatedKey)
      addToast({
        description: 'API key copied to clipboard.',
        title: 'Copied',
        timeout: 3000,
        color: 'success',
        variant: 'solid',
      })
    }
  }

  const closeCreateModal = () => {
    setIsCreateModalOpen(false)
    setNewKeyName('')
    setNewKeyExpiry('')
    setNewlyCreatedKey(null)
    setShowNewKey(false)
  }

  if (!isGitHubAuthEnabled) {
    return (
      <div className="flex min-h-[80vh] items-center justify-center">
        <span className="text-lg text-gray-500">API Key Management is not enabled.</span>
      </div>
    )
  }

  if (status === userAuthStatus.LOADING) {
    return (
      <div className="flex min-h-[80vh] items-center justify-center gap-2">
        <FontAwesomeIcon icon={faSpinner} spin height={16} width={16} />
        <span className="text-lg text-gray-500">Checking session...</span>
      </div>
    )
  }

  if (status !== userAuthStatus.AUTHENTICATED) {
    return (
      <div className="flex min-h-[80vh] items-center justify-center">
        <span className="text-lg text-gray-500">You must be logged in to manage API keys.</span>
      </div>
    )
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

        <SecondaryCard icon={faKey} title="Your API Keys" className="mb-6">
          <div className="mb-4 flex justify-between">
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
              onPress={() => setIsCreateModalOpen(true)}
              className="rounded-lg bg-black font-medium text-white transition-colors hover:bg-gray-900/90"
            >
              <FontAwesomeIcon icon={faPlus} className="mr-2" />
              Create New API Key
            </Button>
          </div>

          {loading ? (
            <div className="flex justify-center py-8">
              <FontAwesomeIcon icon={faSpinner} spin height={24} width={24} />
            </div>
          ) : error ? (
            <div className="rounded-md bg-red-50 p-4 text-red-700 dark:bg-red-900/20 dark:text-red-400">
              Error loading API keys: {error.message}
            </div>
          ) : data?.apiKeys?.length === 0 ? (
            <div className="rounded-md bg-gray-50 p-8 text-center text-gray-500 dark:bg-gray-800/50 dark:text-gray-400">
              You don't have any API keys yet. Create one to get started.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="py-3 text-left font-semibold">Name</th>
                    <th className="py-3 text-left font-semibold">Key Suffix</th>
                    <th className="py-3 text-left font-semibold">Created</th>
                    <th className="py-3 text-left font-semibold">Expires</th>
                    <th className="py-3 text-left font-semibold">Status</th>
                    <th className="py-3 text-right font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.apiKeys.map((key: ApiKey) => (
                    <tr
                      key={key.id}
                      className={`border-b border-gray-200 dark:border-gray-700 ${
                        key.revoked ? 'bg-gray-50 dark:bg-gray-800/30' : ''
                      }`}
                    >
                      <td className="py-3">{key.name}</td>
                      <td className="py-3 font-mono text-sm">*******{key.keySuffix}</td>
                      <td className="py-3">{new Date(key.createdAt).toLocaleDateString()}</td>
                      <td className="py-3">
                        {key.expiresAt ? new Date(key.expiresAt).toLocaleDateString() : 'Never'}
                      </td>
                      <td className="py-3">
                        <span
                          className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                            key.revoked
                              ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                              : 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                          }`}
                        >
                          {key.revoked ? 'Revoked' : 'Active'}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        {!key.revoked && (
                          <Button
                            variant="light"
                            size="sm"
                            onPress={() => handleRevokeKey(parseInt(key.id.toString()))}
                            className="text-red-600 hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-900/20 dark:hover:text-red-300"
                          >
                            <FontAwesomeIcon icon={faTrash} className="mr-1" />
                            Revoke
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

        <SecondaryCard title="API Key Usage" className="mb-6">
          <div className="space-y-4">
            <p>
              API keys allow you to authenticate requests to our API. Include your API key in the
              <code className="mx-1 rounded bg-gray-100 px-1 py-0.5 font-mono dark:bg-gray-800">
                X-API-Key
              </code>
              header of your requests:
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

      {/* Create API Key Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={closeCreateModal}
        size="lg"
        scrollBehavior="inside"
      >
        <ModalContent>
          <ModalHeader className="flex flex-col gap-1">Create New API Key</ModalHeader>
          <ModalBody>
            {newlyCreatedKey ? (
              <div className="space-y-4">
                <div className="rounded-md bg-green-50 p-4 dark:bg-green-900/20">
                  <p className="font-medium text-green-800 dark:text-green-400">
                    Your API key has been created successfully.
                  </p>
                  <p className="text-sm text-yellow-800 dark:text-yellow-400">
                    Important: Please copy it now as you won't be able to see it again.
                  </p>
                </div>

                <div className="relative">
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
                  <label htmlFor="key-name" className="mb-2 block text-sm font-medium">
                    API Key Name
                  </label>
                  <Input
                    id="key-name"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    placeholder="e.g., Development, Production, CI/CD"
                  />
                </div>

                <div>
                  <label htmlFor="key-expiry" className="mb-2 block text-sm font-medium">
                    Expiration Date (Optional)
                  </label>
                  <Input
                    id="key-expiry"
                    type="date"
                    value={newKeyExpiry}
                    onChange={(e) => setNewKeyExpiry(e.target.value)}
                    min={format(new Date(), 'yyyy-MM-dd')}
                  />
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
                  isDisabled={createLoading || !newKeyName.trim()}
                  className="bg-owasp-blue hover:bg-owasp-blue/90"
                >
                  {createLoading && <FontAwesomeIcon icon={faSpinner} spin className="mr-2" />}
                  Create API Key
                </Button>
              </>
            )}
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Confirmation Modal */}
      {confirmationModal?.isOpen && (
        <Modal
          isOpen={confirmationModal.isOpen}
          onClose={() => setConfirmationModal(null)}
          size="md"
        >
          <ModalContent>
            <ModalHeader>{confirmationModal.title}</ModalHeader>
            <ModalBody>
              <p>{confirmationModal.message}</p>
            </ModalBody>
            <ModalFooter>
              <Button variant="light" onPress={() => setConfirmationModal(null)}>
                Cancel
              </Button>
              <Button
                color="danger"
                onPress={async () => {
                  await confirmationModal.onConfirm()
                  setConfirmationModal(null)
                }}
              >
                Confirm
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      )}
    </div>
  )
}

export default ApiKeyPageContent
