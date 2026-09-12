'use client'

import { useApolloClient } from '@apollo/client/react'
import { Autocomplete, AutocompleteItem } from '@heroui/react'
import { useDebouncedSuggestions } from 'hooks/useDebouncedSuggestions'
import React, { useCallback, useEffect, useRef, useState } from 'react'

import { SearchChapterNamesDocument } from 'types/__generated__/chapterQueries.generated'
import { SearchProjectNamesDocument } from 'types/__generated__/projectQueries.generated'

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

export type EntitySelectorInputProps = {
  value: string
  onChange: (key: string) => void
  entityType: 'project' | 'chapter'
  error?: string
}

const EntitySelectorInput: React.FC<EntitySelectorInputProps> = ({
  value,
  onChange,
  entityType,
  error,
}) => {
  const client = useApolloClient()
  const [inputValue, setInputValue] = useState(value)
  const pendingSelectionRef = useRef(false)
  const lastKeyRef = useRef<string>('')
  const isExplicitEditRef = useRef(false)

  const isProject = entityType === 'project'
  const stripPrefix = useCallback(
    (key: string) => key.replace(isProject ? /^www-project-/ : /^www-chapter-/, ''),
    [isProject]
  )

  const fetcher = useCallback(
    async (q: string) => {
      if (isProject) {
        const { data } = await client.query({
          query: SearchProjectNamesDocument,
          variables: { query: q },
          fetchPolicy: 'network-only',
        })
        return data?.searchProjects || []
      } else {
        const { data } = await client.query({
          query: SearchChapterNamesDocument,
          variables: { query: q },
          fetchPolicy: 'network-only',
        })
        return data?.searchChapters || []
      }
    },
    [client, isProject]
  )

  const { items, isLoading } = useDebouncedSuggestions<{
    id: string
    key: string
    name: string
  }>(inputValue, fetcher, { minLength: 3 })

  useEffect(() => {
    if (!value && lastKeyRef.current !== '') {
      setInputValue('')
      lastKeyRef.current = ''
      isExplicitEditRef.current = false
    }
  }, [value])

  useEffect(() => {
    if (!inputValue.trim()) {
      if (lastKeyRef.current !== '') {
        lastKeyRef.current = ''
        onChange('')
      }
      isExplicitEditRef.current = false
      return
    }

    if (!isExplicitEditRef.current) {
      return
    }

    const matched = items.find(
      (item) =>
        item.name.toLowerCase() === inputValue.trim().toLowerCase() ||
        stripPrefix(item.key).toLowerCase() === inputValue.trim().toLowerCase()
    )
    const newKey = matched ? stripPrefix(matched.key) : ''
    if (lastKeyRef.current !== newKey) {
      lastKeyRef.current = newKey
      onChange(newKey)
    }
    if (matched) {
      isExplicitEditRef.current = false
    }
  }, [inputValue, items, onChange, stripPrefix])

  const handleSelectionChange = (key: React.Key | null) => {
    const selected = key ? items.find((item) => item.key === key || item.id === key) : null
    if (selected) {
      pendingSelectionRef.current = true
      isExplicitEditRef.current = false
      const strippedKey = stripPrefix(selected.key)
      setInputValue(selected.name)
      lastKeyRef.current = strippedKey
      onChange(strippedKey)
    } else if (!key) {
      isExplicitEditRef.current = false
      lastKeyRef.current = ''
      onChange('')
    }
  }

  const handleInputChange = (newValue: string) => {
    if (pendingSelectionRef.current) {
      pendingSelectionRef.current = false
      return
    }
    isExplicitEditRef.current = true
    setInputValue(newValue)
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
        isInvalid={!!error}
        errorMessage={error}
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

export default EntitySelectorInput
