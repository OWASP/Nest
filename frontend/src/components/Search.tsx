import React, { useCallback } from 'react'
import TagManager from 'react-gtm-module'
import Autocomplete from 'components/AutoSuggestion'

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
  indexName,
  onReady,
}) => {
  const handleSearchChange = useCallback(
    (query: string) => {
      onSearch(query)
      TagManager.dataLayer({
        dataLayer: {
          event: 'search',
          search_term: query,
          page_path: window.location.pathname,
        },
      })
    },
    [onSearch]
  )

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
