import { faArrowDown, faCheck } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from 'components/ui/dropdownMenu'

interface SortOption {
  value: string
  label: string
}

interface SortByProps {
  options: SortOption[]
  selectedOption: string
  onSortChange: (value: string) => void
}

const SortBy = ({ options, selectedOption, onSortChange }: SortByProps) => {
  if (!options || options.length === 0) return null

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          className="h-10 w-[100px] justify-between border-2 bg-white text-[#292e36] dark:bg-[#3C3C3C] dark:text-[#D1D5DB]"
        >
          <span>Sort By </span>
          <FontAwesomeIcon icon={faArrowDown} />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[180px] bg-white text-[#4B5563] dark:bg-[#3C3C3C] dark:text-[#D1D5DB]">
        {options.map((option) => (
          <DropdownMenuItem
            key={option.value}
            onSelect={() => onSortChange(option.value)}
            className="justify-between"
          >
            {option.label}
            {option.value === selectedOption && <FontAwesomeIcon icon={faCheck} />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default SortBy
