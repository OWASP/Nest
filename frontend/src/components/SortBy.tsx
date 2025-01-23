import {
  SelectContent,
  SelectItem,
  SelectLabel,
  SelectRoot,
  SelectTrigger,
  SelectValueText,
} from 'components/ui/select'

interface SortOption {
  value: string
  label: string
}

interface SortByProps {
  options: any
  selectedOption: string
  onSortChange: (value: string) => void
}

const SortBy = ({ options, selectedOption, onSortChange }: SortByProps) => {
  console.log(selectedOption)
  if (!options || options.length === 0) return null
  return (
    <SelectRoot
      collection={options}
      size="sm"
      className="w-56"
      onValueChange={(e) => {
        onSortChange(e.value[0])
      }}
    >
      <SelectTrigger>
        <SelectValueText placeholder={`Sort by : ${selectedOption || 'Default'}`} />
      </SelectTrigger>
      <SelectContent className="w-80 p-1 dark:bg-[#323232]">
        {options.items.map((sortAttribute) => (
          <SelectItem
            className="hover p-2 hover:bg-[#D1DBE6] dark:hover:bg-[#454545]"
            item={sortAttribute}
            key={sortAttribute.value}
          >
            {sortAttribute.label}
          </SelectItem>
        ))}
      </SelectContent>
    </SelectRoot>
  )
}

export default SortBy
