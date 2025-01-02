import React, { useCallback } from 'react'
import Autocomplete from 'components/AutoSuggestion'
import TagManager from 'react-gtm-module'

interface SearchProps {
  onSearch: (query: string) => void
  placeholder: string
  initialValue?: string
  indexName: string
  onReady: () => void
}

const SearchComponent: React.FC<SearchProps> = ({
  onSearch,
  placeholder,
  initialValue = '',
  indexName = 'issue_suggestions',
  onReady,
}) => {
  const handleSearchChange = useCallback(
    (query: string) => {
      onSearch(query)
    },
    [onSearch]
  )
  TagManager.dataLayer({
    dataLayer: {
      event: 'search',
      search_term: searchQuery,
      page_path: window.location.pathname,
    },
  })
  return (
    <div className="w-full max-w-md p-4">
      <div className="relative">
        <Autocomplete
          indexName={indexName}
          initialValue={initialValue}
          onChange={handleSearchChange}
          placeholder={placeholder}
          onReady={onReady}
        />
      </div>
    </div>
  )
}

export default SearchComponent
