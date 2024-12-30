import { autocomplete } from '@algolia/autocomplete-js'
import { createQuerySuggestionsPlugin } from '@algolia/autocomplete-plugin-query-suggestions'
import '@algolia/autocomplete-theme-classic'
import { debounce } from 'lodash'
import React from 'react'
import { useEffect, useRef } from 'react'
import { client } from '../lib/algoliaClient'
import './Autosuggestion.css'
import { NEST_ENV } from 'utils/credentials'

interface SearchProps {
  // eslint-disable-next-line no-unused-vars
  onChange: (query: string) => void
  placeholder: string
  initialValue?: string
  indexName: string
  onReady: () => void
}

const Autocomplete = React.memo(
  ({ onChange, placeholder, initialValue = '', indexName, onReady }: SearchProps) => {
    const containerRef = useRef<HTMLDivElement | null>(null)
    const searchRef = useRef<ReturnType<typeof autocomplete> | null>(null)

    const debouncedOnChange = debounce((query: string) => {
      onChange(query)
    }, 1000)

    useEffect(() => {
      return () => {
        debouncedOnChange.cancel()
      }
    }, [debouncedOnChange])

    useEffect(() => {
      if (containerRef.current) {
        const querySuggestionsPlugin = createQuerySuggestionsPlugin({
          searchClient: client,
          indexName: `${NEST_ENV}_${indexName}_suggestions`,
          getSearchParams: () => ({
            hitsPerPage: 7,
          }),
        })

        searchRef.current = autocomplete({
          container: containerRef.current,
          placeholder,
          autoFocus: true,
          openOnFocus: true,
          insights: true,
          plugins: [querySuggestionsPlugin],
          initialState: { query: initialValue },
          onStateChange: ({ state }) => {
            const { query } = state
            debouncedOnChange(query as string)
          },
        })
        onReady()
        return () => {
          if (searchRef.current) {
            searchRef.current.destroy()
          }
        }
      }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [indexName])

    return (
      <div className="w-full max-w-lg p-4">
        <div ref={containerRef}></div>
      </div>
    )
  }
)

export default Autocomplete
