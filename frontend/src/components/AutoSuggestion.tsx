import { autocomplete } from '@algolia/autocomplete-js'
import { createQuerySuggestionsPlugin } from '@algolia/autocomplete-plugin-query-suggestions'
import '@algolia/autocomplete-theme-classic'
import { debounce } from 'lodash'
import { useEffect, useRef } from 'react'
import { client } from '../lib/algoliaClient'

interface SearchProps {
  // eslint-disable-next-line no-unused-vars
  onChange: (query: string) => void
  placeholder: string
  initialValue?: string
}

const querySuggestionsPlugin = createQuerySuggestionsPlugin({
  searchClient: client,
  indexName: 'issue_suggestions',
  getSearchParams: () => ({
    hitsPerPage: 10,
  }),
})

const Autocomplete = ({ onChange, placeholder, initialValue = '' }: SearchProps) => {
  const containerRef = useRef(null)

  const debouncedOnChange = useRef(
    debounce((query: string) => {
      onChange(query)
    }, 1000)
  ).current
  useEffect(() => {
    return () => {
      debouncedOnChange.cancel()
    }
  }, [debouncedOnChange])
  useEffect(() => {
    if (containerRef.current) {
      const search = autocomplete({
        container: containerRef.current,
        placeholder,
        openOnFocus: true,
        plugins: [querySuggestionsPlugin],
        initialState: { query: initialValue },
        onStateChange: ({ state }) => {
          const { query } = state
          debouncedOnChange(query as string)
        },
      })

      return () => {
        search.destroy()
      }
    }
  }, [onChange, placeholder, initialValue, debouncedOnChange])

  return (
    <div className="w-full max-w-md p-4">
      <div ref={containerRef}></div>
    </div>
  )
}

export default Autocomplete
