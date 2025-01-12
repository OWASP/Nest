import { autocomplete } from '@algolia/autocomplete-js'
import { createQuerySuggestionsPlugin } from '@algolia/autocomplete-plugin-query-suggestions'
import '@algolia/autocomplete-theme-classic'
import { debounce } from 'lodash'
import React from 'react'
import { useEffect, useRef } from 'react'
import { ENVIRONMENT } from 'utils/credentials'
import { client } from 'utils/helpers/algoliaClient'
import 'styles/Autosuggestion.css'

interface SearchProps {
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
    }, 750)

    useEffect(() => {
      return () => {
        debouncedOnChange.cancel()
      }
    }, [debouncedOnChange])

    useEffect(() => {
      if (containerRef.current) {
        const querySuggestionsPlugin = createQuerySuggestionsPlugin({
          searchClient: client,
          indexName: `${ENVIRONMENT}_${indexName}_suggestions`,
          getSearchParams: () => ({
            hitsPerPage: 7,
          }),
        })

        searchRef.current = autocomplete({
          container: containerRef.current,
          placeholder,
          autoFocus: true,
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
