'use client'

import { useApolloClient } from '@apollo/client/react'
import { Autocomplete, AutocompleteItem } from '@heroui/react'
import { useDebouncedSuggestions } from 'hooks/useDebouncedSuggestions'
import Image from 'next/image'
import React, { useCallback, useEffect, useState } from 'react'
import { FaUserPlus, FaXmark } from 'react-icons/fa6'

import {
  GetEntityContributorsDocument,
  SearchUserLoginsDocument,
} from 'types/__generated__/userQueries.generated'

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

export type UserSelectorInputProps = {
  logins: string[]
  onChange: (logins: string[]) => void
  projectKey?: string
  chapterKey?: string
  disabled?: boolean
  error?: string
  touched?: boolean
}

type UserItem = { id: string; login: string; name: string; avatarUrl: string }

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
  const [suggestedContributors, setSuggestedContributors] = useState<UserItem[]>([])

  // Fetch entity contributors whenever projectKey / chapterKey changes
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

  const fetcher = useCallback(
    async (q: string) => {
      const { data } = await client.query({
        query: SearchUserLoginsDocument,
        variables: { query: q },
      })
      return data?.searchUsers || []
    },
    [client]
  )

  const { items, isLoading } = useDebouncedSuggestions<UserItem>(inputValue, fetcher, {
    minLength: 2,
  })

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

export default UserSelectorInput
