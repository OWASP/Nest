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
  sortOrderOptions,
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
            <SelectTrigger className="min-w-20 text-sm">
              <SelectValueText placeholder={selectedSortOption} />
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
        <div className="rounded-xl bg-gray-200 px-2 shadow-sm dark:bg-[#323232]">
          <SelectRoot
            collection={sortOrderOptions}
            size="md"
            onValueChange={(e) => {
              onOrderChange(e.value)
            }}
          >
            <div className="flex items-center gap-2">
              <SelectLabel className="font-small text-sm text-gray-600 dark:text-gray-300">
                Order:
              </SelectLabel>
              <SelectTrigger className="min-w-12 text-sm">
                <SelectValueText placeholder={selectedOrder} />
              </SelectTrigger>
            </div>
            <SelectContent className="text-md min-w-24 dark:bg-[#323232]">
              {sortOrderOptions.items.map((order) => (
                <SelectItem
                  item={order}
                  key={order.value}
                  className="p-1 hover:bg-[#D1DBE6] dark:hover:bg-[#454545]"
                >
                  {order.label}
                </SelectItem>
              ))}
            </SelectContent>
          </SelectRoot>
        </div>
      )}
    </div>
  )
}

export default SortBy
