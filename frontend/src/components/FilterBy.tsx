import { Select, SelectItem } from '@heroui/select'

interface FilterByProps {
  filterOptions?: string[]
  onFilterChange: (value: string) => void
  selectedOption: string
  defaultValue: string
  customFilter: string
  isLoaded: boolean
}

const FilterBy = ({
  filterOptions,
  onFilterChange,
  selectedOption,
  defaultValue,
  customFilter,
  isLoaded,
}: FilterByProps) => {
  if (!filterOptions || filterOptions.length === 0) return null

  const allOptions = [
    { key: '', label: defaultValue },
    ...filterOptions.map((option: string) => ({ key: option, label: option })),
  ]

  return isLoaded ? (
    <div className="flex items-center gap-2">
      <div className="inline-flex h-12 items-center rounded-lg border border-gray-300 bg-gray-100 pl-3 shadow-sm transition-all duration-200 hover:shadow-md dark:border-gray-600 dark:bg-[#323232]">
        <Select
          className=""
          labelPlacement="outside-left"
          size="md"
          label={`Filter by ${customFilter}:`}
          classNames={{
            label: 'font-medium text-sm text-gray-700 dark:text-gray-300 w-auto select-none pe-0',
            trigger:
              'bg-transparent data-[hover=true]:bg-transparent focus:outline-none focus:underline border-none shadow-none text-nowrap w-36 min-h-8 h-8 text-sm font-medium text-gray-800 dark:text-gray-200 hover:text-gray-900 dark:hover:text-gray-100 transition-all duration-0',
            value: 'text-gray-800 dark:text-gray-200 font-medium',
            selectorIcon: 'text-gray-500 dark:text-gray-400 transition-transform duration-200',
            popoverContent:
              'bg-white dark:bg-[#2a2a2a] border border-gray-200 dark:border-gray-600 rounded-md shadow-lg min-w-36 p-1 focus:outline-none',
            listbox: 'p-0 focus:outline-none',
          }}
          onChange={(e) => {
            onFilterChange((e.target as HTMLSelectElement).value)
          }}
          selectedKeys={[selectedOption]}
        >
          {allOptions.map((option: { key: string; label: string }) => (
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
    </div>
  ) : null
}

export default FilterBy
