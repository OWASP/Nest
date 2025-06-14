import { faArrowDownWideShort, faArrowUpWideShort } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Select, SelectItem } from '@heroui/select'
import { Tooltip } from '@heroui/tooltip'
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
      <div className="inline-flex h-12 items-center rounded-lg bg-gray-200 dark:bg-[#323232]">
        <Select
          className=""
          labelPlacement="outside-left"
          size="md"
          label="Sort By :"
          classNames={{
            label:
              'font-small text-sm text-gray-600 hover:cursor-pointer dark:text-gray-300 pl-[1.4rem] w-auto',
            trigger: 'bg-gray-200 dark:bg-[#323232] pl-0 text-nowrap w-32',
            popoverContent: 'text-md min-w-36 dark:bg-[#323232] rounded-none p-0',
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
                base: 'text-sm hover:bg-[#D1DBE6] dark:hover:bg-[#454545] rounded-none px-3 py-0.5',
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
