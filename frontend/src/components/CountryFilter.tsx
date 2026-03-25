import { Autocomplete, AutocompleteItem } from '@heroui/autocomplete'
import type React from 'react'
import { useEffect, useMemo, useState } from 'react'

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
  const options = useMemo(
    () => [{ key: '', label: 'All Countries' }, ...countries.map((c) => ({ key: c, label: c }))],
    [countries]
  )
 const [inputValue, setInputValue] = useState(selectedCountry || 'All Countries')

  useEffect(() => {
    setInputValue(selectedCountry || 'All Countries')
  }, [selectedCountry])
  return (
    <div className="relative inline-flex h-12 items-center rounded-lg border border-r-0 border-gray-300 bg-white shadow-none transition-all duration-200 dark:border-gray-600 dark:bg-gray-800">
      <Autocomplete
        aria-label="Country"
        labelPlacement="outside-left"
        size="md"
        isLoading={isLoading}
        defaultItems={options}
        selectedKey={selectedCountry}
        inputValue={inputValue}
        onInputChange={(value) => {
          setInputValue(value)
        }}
        onSelectionChange={(key) => {
          const selected = (key as string) ?? ''
          onCountryChange(selected)
          setInputValue(selected || 'All Countries')
        }}
        allowsCustomValue={false}
        scrollShadowProps={{
          isEnabled: false,
        }}
        clearButtonProps={{ 'aria-label': 'Clear country selection' }}
        classNames={{
          base: 'w-52',
          clearButton: 'p-0',
          listbox: 'p-0 focus:outline-none',
          popoverContent:
            'z-[1000] mt-1 !w-52 !min-w-52 bg-white dark:bg-[#2a2a2a] border border-gray-200 dark:border-gray-600 rounded-md shadow-lg max-h-72 p-1 focus:outline-none',
          selectorButton: 'text-gray-500 dark:text-gray-400 transition-transform duration-200',
        }}
        inputProps={{
          'aria-label': 'Country',
          classNames: {
            label: 'font-medium text-sm text-gray-700 dark:text-gray-300 w-auto select-none pe-0',
            inputWrapper:
              'bg-transparent data-[hover=true]:bg-transparent focus-within:!bg-transparent border-none shadow-none outline-none ring-0 min-h-8 h-8',
            input:
              'text-sm font-medium text-gray-800 dark:text-gray-200 placeholder:text-gray-400 !outline-none !ring-0 focus:!outline-none focus:!ring-0',
          },
        }}
      >
        {(item) => (
          <AutocompleteItem
            key={item.key}
            classNames={{
              base: 'text-sm text-gray-700 dark:text-gray-300 hover:bg-transparent dark:hover:bg-transparent focus:bg-gray-100 dark:focus:bg-[#404040] focus:outline-none rounded-sm px-3 py-2 cursor-pointer data-[selected=true]:bg-blue-50 dark:data-[selected=true]:bg-blue-900/20 data-[selected=true]:text-blue-600 dark:data-[selected=true]:text-blue-400 data-[focus=true]:bg-gray-100 dark:data-[focus=true]:bg-[#404040]',
            }}
          >
            {item.label}
          </AutocompleteItem>
        )}
      </Autocomplete>
    </div>
  )
}

export default CountryFilter
