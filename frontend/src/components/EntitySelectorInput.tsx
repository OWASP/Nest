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
}

const EntitySelectorInput: React.FC<EntitySelectorInputProps> = ({
  value,
  onChange,
  entityType,
}) => {
  const client = useApolloClient()
  const [inputValue, setInputValue] = useState(value)
  const pendingSelectionRef = useRef(false)

  const isProject = entityType === 'project'
  const prefix = isProject ? /^www-project-/ : /^www-chapter-/
  const stripPrefix = (key: string) => key.replace(prefix, '')

  const fetcher = useCallback(
    async (q: string) => {
      if (isProject) {
        const { data } = await client.query({
          query: SearchProjectNamesDocument,
          variables: { query: q },
        })
        return data?.searchProjects || []
      } else {
        const { data } = await client.query({
          query: SearchChapterNamesDocument,
          variables: { query: q },
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
    if (!value) setInputValue('')
  }, [value])

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
    onChange(matched ? stripPrefix(matched.key) : '')
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

export default EntitySelectorInput
