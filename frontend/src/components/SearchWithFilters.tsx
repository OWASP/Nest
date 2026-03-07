import { Select, SelectItem } from '@heroui/select'
import React from 'react'
import type { SearchWithFiltersProps } from 'types/searchWithFilters'
import SearchBar from 'components/Search'
import SortBy from 'components/SortBy'

const SearchWithFilters: React.FC<SearchWithFiltersProps> = ({
  isLoaded,
  searchQuery,
  sortBy,
  order,
  category,
  sortOptions,
  categoryOptions,
  searchPlaceholder = 'Search...',
  onSearch,
  onSortChange,
  onOrderChange,
  onCategoryChange,
}) => {
  return (
    <div className="flex w-full max-w-4xl flex-col items-center gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      {categoryOptions && categoryOptions.length > 1 && (
        <div className="inline-flex h-12 shrink-0 items-center rounded-lg border border-gray-300 bg-gray-100 pl-3 shadow-sm transition-all duration-200 hover:shadow-md dark:border-gray-600 dark:bg-[#323232]">
          <Select
            aria-label="Filter by category"
            labelPlacement="outside-left"
            size="md"
            label="Category :"
            classNames={{
              label: 'font-medium text-sm text-gray-700 dark:text-gray-300 w-auto select-none pe-0',
              trigger:
                'bg-transparent data-[hover=true]:bg-transparent focus:outline-none focus:underline border-none shadow-none text-nowrap min-h-8 h-8 text-sm font-medium text-gray-800 dark:text-gray-200 hover:text-gray-900 dark:hover:text-gray-100 transition-all duration-0 w-36',
              value: 'text-gray-800 dark:text-gray-200 font-medium',
              selectorIcon: 'text-gray-500 dark:text-gray-400 transition-transform duration-200',
              popoverContent:
                'bg-white dark:bg-[#2a2a2a] border border-gray-200 dark:border-gray-600 rounded-md shadow-lg min-w-36 p-1 focus:outline-none',
              listbox: 'p-0 focus:outline-none',
            }}
            selectedKeys={new Set([category || ''])}
            onSelectionChange={(keys) => {
              const selected = Array.from(keys as Set<React.Key>)
              onCategoryChange(String(selected[0] ?? ''))
            }}
          >
            {categoryOptions.map((option) => (
              <SelectItem
                key={option.key}
                textValue={option.label}
                classNames={{
                  base: 'text-sm text-gray-700 dark:text-gray-300 hover:bg-transparent dark:hover:bg-transparent focus:bg-gray-100 dark:focus:bg-[#404040] focus:outline-none rounded-sm px-3 py-2 cursor-pointer data-[selected=true]:bg-blue-50 dark:data-[selected=true]:bg-blue-900/20 data-[selected=true]:text-blue-600 dark:data-[selected=true]:text-blue-400 data-[focus=true]:bg-gray-100 dark:data-[focus=true]:bg-[#404040]',
                }}
              >
                {option.label}
              </SelectItem>
            ))}
          </Select>
        </div>
      )}

      <div className="w-full flex-1">
        <SearchBar
          isLoaded={isLoaded}
          onSearch={onSearch}
          placeholder={searchPlaceholder}
          initialValue={searchQuery}
        />
      </div>

      <div className="shrink-0">
        <SortBy
          sortOptions={sortOptions}
          selectedSortOption={sortBy || 'default'}
          selectedOrder={order || 'desc'}
          onSortChange={onSortChange}
          onOrderChange={onOrderChange}
        />
      </div>
    </div>
  )
}

export default SearchWithFilters
