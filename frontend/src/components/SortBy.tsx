import {
  faArrowDownShortWide,
  faArrowUpWideShort,
  faCheck,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from 'react-tooltip'
import { SortByProps } from 'types/sortBy'
import {
  SelectContent,
  SelectItem,
  SelectLabel,
  SelectRoot,
  SelectTrigger,
  SelectValueText,
} from 'components/ui/Select'
import { Button } from '@chakra-ui/react'
const SortBy = ({
  sortOptions,
  selectedSortOption,
  selectedOrder,
  onSortChange,
  onOrderChange,
}: SortByProps) => {
  if (!sortOptions || sortOptions.items.length === 0) return null

  return (
    <div className="flex items-center gap-4">
      {/* Sort Attribute Dropdown */}
      <div className="rounded-xl bg-gray-200 px-3 shadow-sm dark:bg-[#323232]">
        <SelectRoot
          key={selectedSortOption}
          collection={sortOptions}
          size="sm"
          onValueChange={(e) => {
            onSortChange(e.value[0])
          }}
        >
          <div className="flex items-center gap-2">
            <SelectLabel className="font-small text-sm text-gray-600 dark:text-gray-300">
              Sort By:
            </SelectLabel>
            <SelectTrigger className="width-auto text-sm">
              <SelectValueText
                paddingRight={'1.4rem'}
                width={'auto'}
                textWrap="nowrap"
                placeholder={
                  sortOptions.items.find((item) => item.value === selectedSortOption)?.label
                }
              />
            </SelectTrigger>
          </div>
          <SelectContent className="text-md text-md min-w-36 dark:bg-[#323232]">
            {sortOptions.items.map((attribute) => (
              <SelectItem
                item={attribute}
                key={attribute.value}
                className="p-1 px-3 hover:bg-[#D1DBE6] dark:hover:bg-[#454545]"
              >
                {attribute.label}
                {attribute.value === selectedSortOption && (
                  <FontAwesomeIcon
                    icon={faCheck}
                    className="text-sm text-blue-500 dark:text-sky-600"
                  />
                )}
              </SelectItem>
            ))}
          </SelectContent>
        </SelectRoot>
      </div>

      {/* Sort Order Dropdown */}
      {selectedSortOption !== 'default' && (
        <div className="relative flex items-center">
          <Button
            data-tooltip-id="sort-order-tooltip"
            data-tooltip-content={selectedOrder === 'asc' ? 'Ascending Order' : 'Descending Order'}
            onClick={() => onOrderChange(selectedOrder === 'asc' ? 'desc' : 'asc')}
            className="flex items-center justify-center rounded-lg bg-gray-200 p-2 shadow-sm hover:bg-gray-300 dark:bg-[#323232] dark:text-gray-300 dark:hover:bg-[#454545]"
          >
            {selectedOrder === 'asc' ? (
              <FontAwesomeIcon
                icon={faArrowDownShortWide}
                className="h-5 w-5 text-gray-600 dark:text-gray-200"
              />
            ) : (
              <FontAwesomeIcon
                icon={faArrowUpWideShort}
                className="h-5 w-5 text-gray-600 dark:text-gray-200"
              />
            )}
          </Button>
          <Tooltip
            id="sort-order-tooltip"
            className="rounded-lg bg-white px-1 py-0 text-sm text-gray-600 shadow-md"
          />
        </div>
      )}
    </div>
  )
}

export default SortBy
