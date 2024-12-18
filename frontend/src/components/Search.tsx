import { debounce } from 'lodash'
import { Search, X } from 'lucide-react'
import React, { useCallback, useRef, useState } from 'react'
interface SearchProps {
  // eslint-disable-next-line no-unused-vars
  onSearch: (query: string) => void
  placeholder: string
}

const SearchComponent: React.FC<SearchProps> = ({ onSearch, placeholder }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedSearch = useCallback(
    debounce((query: string) => {
      onSearch(query)
    }, 500),
    []
  )

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
    debouncedSearch(e.target.value)
  }
  const handleClearSearch = () => {
    setSearchQuery('')
    onSearch('')
    inputRef.current?.focus()
  }

  return (
    <div className="w-full max-w-md p-4">
      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <input
          ref={inputRef}
          type="text"
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder={placeholder}
          className="h-12 w-full rounded-lg border border-gray-300 pl-10 pr-10 text-lg text-black transition duration-300 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {searchQuery && (
          <button
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full p-1 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-300"
            onClick={handleClearSearch}
          >
            <X className="h-4 w-4 text-gray-400" />
          </button>
        )}
      </div>
    </div>
  )
}

export default SearchComponent
