'use client'

import { useApolloClient, useMutation } from '@apollo/client/react'
import { Autocomplete, AutocompleteItem } from '@heroui/react'
import { addToast } from '@heroui/toast'
import debounce from 'lodash/debounce'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import { FaCircleInfo, FaUserPlus, FaXmark } from 'react-icons/fa6'

import { IssueCertificateDocument } from 'types/__generated__/certificateMutations.generated'
import { SearchChapterNamesDocument } from 'types/__generated__/chapterQueries.generated'
import { SearchProjectNamesDocument } from 'types/__generated__/projectQueries.generated'
import {
  GetEntityContributorsDocument,
  SearchUserLoginsDocument,
} from 'types/__generated__/userQueries.generated'
import { ExtendedSession } from 'types/auth'
import { extractGraphQLErrors } from 'utils/helpers/handleGraphQLError'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import { FormButtons } from 'components/forms/shared/FormButtons'
import { FormContainer } from 'components/forms/shared/FormContainer'
import { FormTextarea } from 'components/forms/shared/FormTextarea'
import { FormTextInput } from 'components/forms/shared/FormTextInput'
import { validateRequired } from 'components/forms/shared/formValidationUtils'
import { useFormValidation } from 'components/forms/shared/useFormValidation'
import LoadingSpinner from 'components/LoadingSpinner'

const AUTOCOMPLETE_INPUT_PROPS = {
  classNames: {
    label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
    input: 'text-gray-800 dark:text-gray-200',
    inputWrapper: 'bg-gray-50 dark:bg-gray-800',
    helperWrapper: 'min-w-0 max-w-full w-full',
    errorMessage: 'break-words whitespace-normal max-w-full w-full',
  },
}

const AUTOCOMPLETE_CLASS_NAMES = { base: 'w-full min-w-0', selectorButton: 'hidden' }

interface FormData {
  recipientLogins: string[]
  title: string
  message: string
  projectKey: string
  chapterKey: string
}

const INITIAL_FORM: FormData = {
  recipientLogins: [],
  title: '',
  message:
    'In recognition of exceptional contributions to the global OWASP open-source ecosystem and commitment to collaborative innovation.',
  projectKey: '',
  chapterKey: '',
}

type EntitySelectorInputProps = {
  value: string
  onChange: (key: string) => void
  entityType: 'project' | 'chapter'
}

const EntitySelectorInput: React.FC<EntitySelectorInputProps> = ({
  value,
  onChange,
  entityType,
}) => {
  const client = useApolloClient()
  const [inputValue, setInputValue] = useState(value)
  const [items, setItems] = useState<{ id: string; key: string; name: string }[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const pendingSelectionRef = useRef(false)

  const isProject = entityType === 'project'
  const prefix = isProject ? /^www-project-/ : /^www-chapter-/
  const stripPrefix = (key: string) => key.replace(prefix, '')

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const fetchSuggestions = useCallback(
    debounce(async (query: string) => {
      const q = query.trim()
      if (q.length < 3) {
        setItems([])
        setIsLoading(false)
        return
      }
      setIsLoading(true)
      try {
        if (isProject) {
          const { data } = await client.query({
            query: SearchProjectNamesDocument,
            variables: { query: q },
          })
          setItems(data?.searchProjects || [])
        } else {
          const { data } = await client.query({
            query: SearchChapterNamesDocument,
            variables: { query: q },
          })
          setItems(data?.searchChapters || [])
        }
      } catch {
        setIsLoading(false)
      }
    }, 300),
    [client, isProject]
  )

  useEffect(() => {
    if (!value) setInputValue('')
  }, [value])
  useEffect(() => {
    fetchSuggestions(inputValue)
    return () => {
      fetchSuggestions.cancel()
    }
  }, [inputValue, fetchSuggestions])

  const handleSelectionChange = (key: React.Key | null) => {
    const selected = key ? items.find((item) => item.key === key || item.id === key) : null
    if (selected) {
      pendingSelectionRef.current = true
      setInputValue(selected.name)
      onChange(stripPrefix(selected.key))
    } else if (!key) {
      onChange('')
    }
  }

  const handleInputChange = (newValue: string) => {
    if (pendingSelectionRef.current) {
      pendingSelectionRef.current = false
      return
    }
    setInputValue(newValue)
    if (!newValue.trim()) {
      onChange('')
      return
    }
    const matched = items.find(
      (item) =>
        item.name.toLowerCase() === newValue.trim().toLowerCase() ||
        stripPrefix(item.key).toLowerCase() === newValue.trim().toLowerCase()
    )
    onChange(matched ? stripPrefix(matched.key) : stripPrefix(newValue))
  }

  return (
    <div className="w-full min-w-0 overflow-hidden">
      <Autocomplete
        id={isProject ? 'projectKey' : 'chapterKey'}
        label={isProject ? 'Project Name' : 'Chapter Name'}
        labelPlacement="outside"
        placeholder={isProject ? 'Start typing project name...' : 'Start typing chapter name...'}
        inputValue={inputValue}
        onInputChange={handleInputChange}
        onSelectionChange={handleSelectionChange}
        menuTrigger="input"
        isLoading={isLoading}
        allowsCustomValue
        classNames={AUTOCOMPLETE_CLASS_NAMES}
        inputProps={AUTOCOMPLETE_INPUT_PROPS}
      >
        {items.map((item) => (
          <AutocompleteItem key={item.key || item.id} textValue={item.name}>
            {item.name}
          </AutocompleteItem>
        ))}
      </Autocomplete>
    </div>
  )
}

type UserSelectorInputProps = {
  logins: string[]
  onChange: (logins: string[]) => void
  projectKey?: string
  chapterKey?: string
  disabled?: boolean
  error?: string
  touched?: boolean
}

const UserSelectorInput: React.FC<UserSelectorInputProps> = ({
  logins,
  onChange,
  projectKey,
  chapterKey,
  disabled = false,
  error,
  touched,
}) => {
  const client = useApolloClient()
  const [inputValue, setInputValue] = useState('')
  const [items, setItems] = useState<
    { id: string; login: string; name: string; avatarUrl: string }[]
  >([])
  const [suggestedContributors, setSuggestedContributors] = useState<typeof items>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (!projectKey && !chapterKey) {
      setSuggestedContributors([])
      return
    }
    let active = true
    client
      .query({
        query: GetEntityContributorsDocument,
        variables: { projectKey: projectKey || null, chapterKey: chapterKey || null },
      })
      .then(({ data }) => {
        if (active) setSuggestedContributors(data?.entityContributors || [])
      })
      .catch(() => {
        if (active) setSuggestedContributors([])
      })
    return () => {
      active = false
    }
  }, [client, projectKey, chapterKey])

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const fetchSuggestions = useCallback(
    debounce(async (query: string) => {
      const q = query.trim()
      if (q.length < 2) {
        setItems([])
        setIsLoading(false)
        return
      }
      setIsLoading(true)
      try {
        const { data } = await client.query({
          query: SearchUserLoginsDocument,
          variables: { query: q },
        })
        setItems(data?.searchUsers || [])
      } catch {
        setItems([])
      } finally {
        setIsLoading(false)
      }
    }, 300),
    [client]
  )

  useEffect(() => {
    fetchSuggestions(inputValue)
    return () => {
      fetchSuggestions.cancel()
    }
  }, [inputValue, fetchSuggestions])

  const addUser = (raw: string) => {
    const login = raw.trim().replace(/^@/, '')
    if (login && !logins.includes(login)) onChange([...logins, login])
    setInputValue('')
  }

  const displayItems = inputValue.trim().length >= 2 ? items : suggestedContributors

  const handleSelectionChange = (key: React.Key | null) => {
    if (!key) return
    const selected = displayItems.find((item) => item.login === key || item.id === key)
    addUser(selected?.login ?? (typeof key === 'string' ? key : ''))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if ((e.key === 'Enter' || e.key === ',' || e.key === ' ') && inputValue.trim()) {
      e.preventDefault()
      addUser(inputValue)
    }
  }

  return (
    <div className="flex w-full min-w-0 flex-col gap-2.5 lg:col-span-2">
      <Autocomplete
        id="recipientLogins"
        label="Recipient GitHub Username(s)"
        isRequired
        isDisabled={disabled}
        labelPlacement="outside"
        placeholder={
          disabled
            ? 'Select a Project or Chapter first...'
            : suggestedContributors.length > 0
              ? 'Select a contributor or type username...'
              : 'Type username and press Enter or select...'
        }
        description={
          disabled ? '⚠ Select a Project or Chapter above to enable this field.' : undefined
        }
        inputValue={inputValue}
        onInputChange={setInputValue}
        onSelectionChange={handleSelectionChange}
        onKeyDown={handleKeyDown}
        menuTrigger="input"
        isLoading={isLoading}
        allowsCustomValue
        isInvalid={touched && !!error}
        errorMessage={touched ? error : undefined}
        classNames={AUTOCOMPLETE_CLASS_NAMES}
        inputProps={{
          classNames: {
            ...AUTOCOMPLETE_INPUT_PROPS.classNames,
            description: 'text-xs text-amber-600 dark:text-amber-400',
          },
        }}
      >
        {displayItems.map((user) => (
          <AutocompleteItem key={user.login} textValue={user.login}>
            <div className="flex items-center gap-2.5 py-0.5">
              {user.avatarUrl ? (
                <Image
                  src={user.avatarUrl}
                  alt={user.login}
                  width={24}
                  height={24}
                  className="h-6 w-6 shrink-0 rounded-full object-cover"
                />
              ) : (
                <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-bold text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                  {user.login[0]?.toUpperCase()}
                </div>
              )}
              <div className="flex flex-col">
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {user.name || user.login}
                </span>
                <span className="text-xs text-gray-400">@{user.login}</span>
              </div>
            </div>
          </AutocompleteItem>
        ))}
      </Autocomplete>

      {!disabled && suggestedContributors.length > 0 && (
        <div className="flex flex-col gap-1.5 rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-800/60">
          <div className="flex items-center justify-between text-xs font-semibold text-gray-600 dark:text-gray-300">
            <span className="flex items-center gap-1.5">
              <FaUserPlus className="h-3.5 w-3.5 shrink-0 text-[#1D7BD7]" />
              Suggested Contributors ({suggestedContributors.length})
            </span>
            <button
              type="button"
              onClick={() =>
                onChange([...new Set([...logins, ...suggestedContributors.map((c) => c.login)])])
              }
              className="text-xs font-semibold text-[#1D7BD7] hover:underline"
            >
              + Add All
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {suggestedContributors.map((user) => {
              const isAdded = logins.includes(user.login)
              return (
                <button
                  key={user.login}
                  type="button"
                  disabled={isAdded}
                  onClick={() => addUser(user.login)}
                  className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs transition ${
                    isAdded
                      ? 'cursor-not-allowed border-gray-200 bg-gray-100 text-gray-400 opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-500'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400 hover:bg-gray-100 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
                  }`}
                >
                  {user.avatarUrl && (
                    <Image
                      src={user.avatarUrl}
                      alt={user.login}
                      width={16}
                      height={16}
                      className="h-4 w-4 shrink-0 rounded-full object-cover"
                    />
                  )}
                  <span>@{user.login}</span>
                  {isAdded && <span className="text-[10px]">✓</span>}
                </button>
              )
            })}
          </div>
        </div>
      )}

      {logins.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 pt-1">
          {logins.map((login) => (
            <div
              key={login}
              className="inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-gray-100 px-3 py-1 text-xs font-medium text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
            >
              <span>@{login}</span>
              <button
                type="button"
                onClick={() => onChange(logins.filter((l) => l !== login))}
                className="rounded-full p-0.5 text-gray-400 transition hover:bg-gray-200 hover:text-gray-700 dark:hover:bg-gray-700 dark:hover:text-gray-200"
              >
                <FaXmark className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const IssueCertificatePage: React.FC = () => {
  const router = useRouter()
  const { data: session, status } = useSession()

  const extendedSession = session as ExtendedSession | undefined
  const isAuthorized = extendedSession?.user?.isLeader || extendedSession?.user?.isChapterLeader

  const [formData, setFormData] = useState<FormData>(INITIAL_FORM)
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [backendErrors, setBackendErrors] = useState<Record<string, string>>({})
  const [showBanner, setShowBanner] = useState(true)

  const [issueCertificate, { loading }] = useMutation(IssueCertificateDocument)

  useEffect(() => {
    if (status === 'loading') return
    if (!session) {
      router.push('/auth/login')
      return
    }
    if (!isAuthorized) {
      addToast({
        title: 'Access Denied',
        description: 'Only OWASP project leaders or chapter leaders can issue certificates.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
      router.push('/')
    }
  }, [session, status, router, isAuthorized])

  const touch = (field: string) => setTouched((prev) => ({ ...prev, [field]: true }))

  const handleFieldChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (backendErrors[field]) setBackendErrors(({ [field]: _, ...rest }) => rest)
    touch(field)
  }

  const errors = useFormValidation(
    [
      {
        field: 'recipientLogins',
        shouldValidate: !!touched.recipientLogins,
        validator: () =>
          formData.recipientLogins.length === 0
            ? 'At least one Recipient GitHub Username is required.'
            : undefined,
      },
      {
        field: 'title',
        shouldValidate: !!touched.title,
        validator: () => validateRequired(formData.title, 'Certificate title'),
      },
      {
        field: 'message',
        shouldValidate: !!touched.message,
        validator: () => validateRequired(formData.message, 'Certificate body message'),
      },
    ],
    [formData, touched, backendErrors]
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setTouched({ recipientLogins: true, title: true, message: true })

    if (formData.recipientLogins.length === 0 || !formData.title.trim() || !formData.message.trim())
      return

    if (!formData.projectKey.trim() && !formData.chapterKey.trim()) {
      addToast({
        title: 'Validation Error',
        description: 'Please select either a Project Name or a Chapter Name.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
      return
    }

    try {
      await issueCertificate({
        variables: {
          inputData: {
            recipientLogins: formData.recipientLogins,
            title: formData.title.trim(),
            message: formData.message.trim(),
            projectKey: formData.projectKey.trim() || null,
            chapterKey: formData.chapterKey.trim() || null,
          },
        },
      })
      addToast({
        title: 'Success',
        description: `Certificate(s) successfully issued to ${formData.recipientLogins.map((l) => `@${l}`).join(', ')}.`,
        color: 'success',
        variant: 'solid',
        timeout: 4000,
        shouldShowTimeoutProgress: true,
      })
      setFormData(INITIAL_FORM)
      setTouched({})
      setBackendErrors({})
    } catch (err) {
      const { validationErrors, hasValidationErrors } = extractGraphQLErrors(err)
      if (hasValidationErrors) {
        setBackendErrors(validationErrors)
      } else {
        addToast({
          title: 'Failed to Issue Certificate',
          description:
            err instanceof Error ? err.message : 'Unable to complete the requested operation.',
          color: 'danger',
          variant: 'solid',
          timeout: 3000,
          shouldShowTimeoutProgress: true,
        })
      }
    }
  }

  if (status === 'loading') return <LoadingSpinner />

  if (!session || !isAuthorized) {
    return (
      <div className="container mx-auto flex min-h-[50vh] items-center justify-center px-4 py-16">
        <AccessDeniedDisplay
          title="Access Denied"
          message="Only OWASP project leaders or chapter leaders can issue certificates."
        />
      </div>
    )
  }

  const hasEntity = formData.projectKey.trim() || formData.chapterKey.trim()

  return (
    <FormContainer title="Issue Certificate" onSubmit={handleSubmit}>
      {showBanner && (
        <div className="flex items-start justify-between gap-3 rounded-lg border border-l-[3px] border-gray-200 border-l-[#1D7BD7] bg-gray-50 px-4 py-3 dark:border-gray-700 dark:border-l-[#1D7BD7] dark:bg-gray-800/60">
          <div className="flex items-start gap-2.5">
            <FaCircleInfo className="mt-0.5 h-4 w-4 shrink-0 text-[#1D7BD7]" />
            <p className="text-sm text-gray-600 dark:text-gray-300">
              At least one of{' '}
              <span className="font-semibold text-gray-800 dark:text-gray-100">Project Name</span>{' '}
              or{' '}
              <span className="font-semibold text-gray-800 dark:text-gray-100">Chapter Name</span>{' '}
              should be provided to associate this certificate with an OWASP entity.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowBanner(false)}
            aria-label="Dismiss notice"
            className="ml-1 shrink-0 rounded p-1 text-gray-400 transition hover:bg-gray-200 hover:text-gray-600 dark:text-gray-500 dark:hover:bg-gray-700 dark:hover:text-gray-300"
          >
            <FaXmark className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      <section className="flex flex-col gap-6">
        <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
          <FormTextInput
            id="certificate-title"
            label="Certificate Title"
            placeholder="e.g. Certificate of Acknowledgement"
            value={formData.title}
            onValueChange={(value) => handleFieldChange('title', value)}
            error={errors.title || backendErrors.title}
            touched={touched.title}
            required
          />
          <FormTextarea
            id="certificate-message"
            label="Certificate Body Message"
            placeholder="Write a personalized recognition message for the contributor..."
            value={formData.message}
            onChange={(e) => handleFieldChange('message', e.target.value)}
            error={errors.message}
            touched={touched.message}
            required
          />
        </div>
      </section>

      <section className="flex flex-col gap-3 text-gray-600 dark:text-gray-300">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <EntitySelectorInput
            entityType="project"
            value={formData.projectKey}
            onChange={(key) => setFormData((prev) => ({ ...prev, projectKey: key }))}
          />
          <EntitySelectorInput
            entityType="chapter"
            value={formData.chapterKey}
            onChange={(key) => setFormData((prev) => ({ ...prev, chapterKey: key }))}
          />
        </div>
      </section>

      <UserSelectorInput
        logins={formData.recipientLogins}
        onChange={(logins) => {
          setFormData((prev) => ({ ...prev, recipientLogins: logins }))
          touch('recipientLogins')
        }}
        projectKey={formData.projectKey}
        chapterKey={formData.chapterKey}
        disabled={!hasEntity}
        error={
          errors.recipientLogins || backendErrors.recipientLogins || backendErrors.recipientLogin
        }
        touched={touched.recipientLogins}
      />

      <FormButtons loading={loading} submitText="Issue Certificate" />
    </FormContainer>
  )
}

export default IssueCertificatePage
