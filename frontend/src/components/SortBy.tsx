import { Select, SelectItem } from '@heroui/select'
import { Tooltip } from '@heroui/tooltip'
import { FaArrowDownWideShort, FaArrowUpWideShort } from 'react-icons/fa6'
import type { SortByProps } from 'types/sortBy'

const SortBy = ({
  sortOptions,
  selectedSortOption,
  selectedOrder,
  onSortChange,
  onOrderChange,
}: SortByProps) => {
  if (!sortOptions || sortOptions.length === 0) return null
  return (
    <div className="flex items-center gap-2">
      {/* Sort Attribute Dropdown */}
      <div className="inline-flex h-12 items-center rounded-lg border border-gray-300 bg-gray-100 pl-3 shadow-sm transition-all duration-200 hover:shadow-md dark:border-gray-600 dark:bg-[#323232]">
        <Select
          className=""
          labelPlacement="outside-left"
          size="md"
          label="Sort By :"
          classNames={{
            label: 'font-medium text-sm text-gray-700 dark:text-gray-300 w-auto select-none pe-0',
            trigger:
              'bg-transparent data-[hover=true]:bg-transparent focus:outline-none focus:underline border-none shadow-none text-nowrap w-32 min-h-8 h-8 text-sm font-medium text-gray-800 dark:text-gray-200 hover:text-gray-900 dark:hover:text-gray-100 transition-all duration-0',
            value: 'text-gray-800 dark:text-gray-200 font-medium',
            selectorIcon: 'text-gray-500 dark:text-gray-400 transition-transform duration-200',
            popoverContent:
              'bg-white dark:bg-[#2a2a2a] border border-gray-200 dark:border-gray-600 rounded-md shadow-lg min-w-36 p-1 focus:outline-none',
            listbox: 'p-0 focus:outline-none',
          }}
          selectedKeys={sortOptions
            .filter((item: { key: string; label: string }) => item.key === selectedSortOption)
            .map((item) => item.key)}
          onChange={(e) => {
            onSortChange((e.target as HTMLSelectElement).value)
          }}
        >
          {sortOptions.map((option: { label: string; key: string }) => (
            <SelectItem
              key={option.key}
              classNames={{
                base: 'text-sm text-gray-700 dark:text-gray-300 hover:bg-transparent dark:hover:bg-transparent focus:bg-gray-100 dark:focus:bg-[#404040] focus:outline-none rounded-sm px-3 py-2 cursor-pointer data-[selected=true]:bg-blue-50 dark:data-[selected=true]:bg-blue-900/20 data-[selected=true]:text-blue-600 dark:data-[selected=true]:text-blue-400 data-[focus=true]:bg-gray-100 dark:data-[focus=true]:bg-[#404040]',
              }}
            >
              {option.label}
            </SelectItem>
          ))}
        </Select>
      </div>

      {/* Sort Order Dropdown */}
      {selectedSortOption !== 'default' && (
        <Tooltip
          content={selectedOrder === 'asc' ? 'Ascending Order' : 'Descending Order'}
          showArrow
          placement="top-start"
          delay={100}
          closeDelay={100}
        >
          <button
            type="button"
            onClick={() => onOrderChange(selectedOrder === 'asc' ? 'desc' : 'asc')}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                onOrderChange(selectedOrder === 'asc' ? 'desc' : 'asc')
              }
            }}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-gray-300 bg-gray-100 p-0 shadow-sm transition-all duration-200 hover:bg-gray-200 hover:shadow-md focus:ring-2 focus:ring-gray-300 focus:ring-offset-1 focus:outline-none dark:border-gray-600 dark:bg-[#323232] dark:hover:bg-[#404040] dark:focus:ring-gray-500"
            aria-label={
              selectedOrder === 'asc' ? 'Sort in ascending order' : 'Sort in descending order'
            }
          >
            {selectedOrder === 'asc' ? (
              <FaArrowUpWideShort className="h-4 w-4 text-gray-600 dark:text-gray-300" />
            ) : (
              <FaArrowDownWideShort className="h-4 w-4 text-gray-600 dark:text-gray-300" />
            )}
          </button>
        </Tooltip>
      )}
    </div>
  )
}

export default SortBy
