import { faArrowDownWideShort, faArrowUpWideShort } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Select, SelectItem } from '@heroui/select'
import { Tooltip } from '@heroui/tooltip'
import { SortByProps } from 'types/sortBy'

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
      <div className="rounded-lg px-2 shadow-md">
        <Select
          className="min-w-56"
          labelPlacement="outside-left"
          label="Sort By :"
          selectedKeys={sortOptions
            .filter((item: { key: string; label: string }) => item.key === selectedSortOption)
            .map((item) => item.key)}
          onChange={(e) => {
            onSortChange((e.target as HTMLSelectElement).value)
          }}
        >
          {sortOptions.map((option: { label: string; key: string }) => (
            <SelectItem key={option.key}>{option.label}</SelectItem>
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
            onClick={() => onOrderChange(selectedOrder === 'asc' ? 'desc' : 'asc')}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-gray-200 p-0 shadow-sm hover:bg-gray-300 dark:bg-[#323232] dark:text-gray-300 dark:hover:bg-[#454545]"
          >
            {selectedOrder === 'asc' ? (
              <FontAwesomeIcon
                icon={faArrowUpWideShort}
                className="h-4 w-4 text-gray-600 dark:text-gray-200"
              />
            ) : (
              <FontAwesomeIcon
                icon={faArrowDownWideShort}
                className="h-4 w-4 text-gray-600 dark:text-gray-200"
              />
            )}
          </button>
        </Tooltip>
      )}
    </div>
  )
}

export default SortBy
