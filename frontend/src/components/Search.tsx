import React, { useState } from 'react'
import Autocomplete from './AutoSuggestion'

interface SearchProps {
  /* eslint-disable-next-line */
  onSearch: (query: string) => void
  placeholder: string
  initialValue?: string
}

const SearchComponent: React.FC<SearchProps> = ({ onSearch, placeholder, initialValue = '' }) => {
  const [searchQuery, setSearchQuery] = useState(initialValue)

  const handleSearchChange = (query: string) => {
    setSearchQuery(query)
    onSearch(query)
  }

  return (
    <div className="w-full max-w-md p-4">
      <div className="relative">
        <Autocomplete
          initialValue={searchQuery}
          onChange={handleSearchChange}
          placeholder={placeholder}
        />
      </div>
    </div>
  )
}

export default SearchComponent
