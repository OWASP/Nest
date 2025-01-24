import { faArrowDownWideShort, faArrowUpWideShort } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  SelectContent,
  SelectItem,
  SelectLabel,
  SelectRoot,
  SelectTrigger,
  SelectValueText,
} from 'components/ui/select'

const SortBy = ({
  sortOptions,
  selectedSortOption,
  selectedOrder,
  onSortChange,
  onOrderChange,
}: any) => {
  if (!sortOptions || sortOptions.length === 0) return null

  return (
    <div className="flex items-center gap-4">
      {/* Sort Attribute Dropdown */}
      <div className="rounded-xl bg-gray-200 px-2 shadow-sm dark:bg-[#323232]">
        <SelectRoot
          collection={sortOptions}
          size="sm"
          onValueChange={(e) => {
            onSortChange(e.value)
          }}
        >
          <div className="flex items-center gap-2">
            <SelectLabel className="font-small text-sm text-gray-600 dark:text-gray-300">
              Sort By:
            </SelectLabel>
            <SelectTrigger className="w-auto min-w-[8rem] text-sm">
              <SelectValueText
                placeholder={
                  selectedSortOption === 'default'
                    ? 'Default'
                    : sortOptions.items.find((item) => item.value === selectedSortOption)?.label
                }
              />
            </SelectTrigger>
          </div>
          <SelectContent className="text-md text-md min-w-36 dark:bg-[#323232]">
            {sortOptions.items.map((attribute) => (
              <SelectItem
                item={attribute}
                key={attribute.value}
                className="p-1 hover:bg-[#D1DBE6] dark:hover:bg-[#454545]"
              >
                {attribute.label}
              </SelectItem>
            ))}
          </SelectContent>
        </SelectRoot>
      </div>

      {/* Sort Order Dropdown */}
      {selectedSortOption !== 'default' && (
        <div className="flex items-center rounded-lg bg-gray-200 shadow-sm dark:bg-[#323232]">
          <button
            onClick={() => onOrderChange(selectedOrder === 'asc' ? 'desc' : 'asc')}
            className="flex items-center justify-center rounded-lg p-2 hover:bg-gray-300 dark:text-gray-300 dark:hover:bg-[#454545]"
          >
            {selectedOrder === 'asc' ? (
              <FontAwesomeIcon
                icon={faArrowUpWideShort}
                className="h-5 w-5 text-gray-600 dark:text-gray-200"
              />
            ) : (
              <FontAwesomeIcon
                icon={faArrowDownWideShort}
                className="h-5 w-5 text-gray-600 dark:text-gray-200"
              />
            )}
          </button>
        </div>
      )}
    </div>
  )
}

export default SortBy
