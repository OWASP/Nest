import { Select, SelectItem } from '@heroui/select'
import type React from 'react'
import { useEffect, useMemo, useRef, useState } from 'react'

interface CountryFilterProps {
  countries: string[]
  selectedCountry: string
  onCountryChange: (country: string) => void
  isLoading?: boolean
}

const CountryFilter: React.FC<CountryFilterProps> = ({
  countries,
  selectedCountry,
  onCountryChange,
  isLoading = false,
}) => {
  const [filterText, setFilterText] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const allOptions = useMemo(
    () => [{ key: '', label: 'All Countries' }, ...countries.map((c) => ({ key: c, label: c }))],
    [countries]
  )

  const filteredOptions = useMemo(
    () =>
      filterText
        ? allOptions.filter((o) => o.label.toLowerCase().includes(filterText.toLowerCase()))
        : allOptions,
    [allOptions, filterText]
  )

  useEffect(() => {
    if (filterText) {
      requestAnimationFrame(() => inputRef.current?.focus())
    }
  }, [filterText])

  return (
    <div className="inline-flex h-12 items-center rounded-lg border border-gray-300 bg-gray-100 pl-3 shadow-sm transition-all duration-200 hover:shadow-md dark:border-gray-600 dark:bg-[#323232]">
      <Select
        labelPlacement="outside-left"
        size="md"
        label="Country :"
        isLoading={isLoading}
        classNames={{
          label: 'font-medium text-sm text-gray-700 dark:text-gray-300 w-auto select-none pe-0',
          trigger:
            'bg-transparent data-[hover=true]:bg-transparent focus:outline-none focus:underline border-none shadow-none text-nowrap w-40 min-h-8 h-8 text-sm font-medium text-gray-800 dark:text-gray-200 hover:text-gray-900 dark:hover:text-gray-100 transition-all duration-0',
          value: 'text-gray-800 dark:text-gray-200 font-medium',
          selectorIcon: 'text-gray-500 dark:text-gray-400 transition-transform duration-200',
          popoverContent:
            'bg-white dark:bg-[#2a2a2a] border border-gray-200 dark:border-gray-600 rounded-md shadow-lg min-w-44 max-h-72 p-1 focus:outline-none overflow-y-auto',
          listbox: 'p-0 focus:outline-none',
        }}
        scrollShadowProps={{
          isEnabled: false,
        }}
        listboxProps={{
          topContent: (
            <div className="sticky top-0 z-10 bg-white px-2 pt-1 pb-1.5 dark:bg-[#2a2a2a]">
              <input
                ref={inputRef}
                type="text"
                className="w-full rounded-md border border-gray-200 bg-gray-50 px-2.5 py-1.5 text-sm text-gray-800 outline-none placeholder:text-gray-400 focus:border-blue-400 dark:border-gray-600 dark:bg-[#383838] dark:text-gray-200 dark:placeholder:text-gray-500 dark:focus:border-blue-500"
                placeholder="Type to search..."
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
                onClick={(e) => e.stopPropagation()}
                onKeyDown={(e) => e.stopPropagation()}
              />
            </div>
          ),
        }}
        selectedKeys={[selectedCountry]}
        onOpenChange={(open) => {
          if (open) {
            setTimeout(() => inputRef.current?.focus(), 0)
          } else {
            setFilterText('')
          }
        }}
        onChange={(e) => {
          onCountryChange((e.target as HTMLSelectElement).value)
        }}
      >
        {filteredOptions.map((option) => (
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
  )
}

export default CountryFilter
