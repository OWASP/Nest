import axios from 'axios'
import { useState, useEffect, useCallback } from 'react'
import { Dispatch, SetStateAction } from 'react'

import logger from '../utils/logger'

/* eslint-disable-next-line */
interface UseSearchQueryOptions<_T> {
  apiUrl: string
  entityKey: string
  initialTitle?: string
}

export function useSearchQuery<T>({ apiUrl, entityKey, initialTitle }: UseSearchQueryOptions<T>) {
  const [data, setData] = useState<T | null>(null)
  const [defaultData, setDefaultData] = useState<T | null>(null)
  const [initialQuery, setInitialQuery] = useState<string>('')

  const fetchDefaultData = useCallback(async () => {
    try {
      const response = await axios.get(`${apiUrl}`)
      const fetchedData = response.data
      setData(fetchedData)
      setDefaultData(fetchedData)
    } catch (error) {
      logger.error(`Error fetching default ${entityKey}:`, error)
    }
  }, [apiUrl, entityKey])

  const fetchDefData = useCallback(async () => {
    try {
      const response = await axios.get(`${apiUrl}`)
      const fetchedData = response.data
      setDefaultData(fetchedData)
    } catch (error) {
      logger.error(`Error fetching default ${entityKey}:`, error)
    }
  }, [apiUrl, entityKey])

  const fetchSearchData = useCallback(
    async (query: string) => {
      try {
        const response = await axios.get(`${apiUrl}`, {
          params: { q: query },
        })
        const fetchedData = response.data.data || response.data
        setData(fetchedData)
        setDefaultData(fetchedData)
      } catch (error) {
        logger.error(`Error searching ${entityKey}:`, error)
      }
    },
    [apiUrl, entityKey]
  )

  useEffect(() => {
    const fetchData = async () => {
      try {
        const queryParams = new URLSearchParams(window.location.search)
        const urlQuery = queryParams.get('q')

        if (urlQuery) {
          setInitialQuery(urlQuery)
          fetchSearchData(urlQuery)
          fetchDefData()
        } else {
          await fetchDefaultData()
        }

        if (initialTitle) {
          document.title = initialTitle
        }
      } catch (error) {
        logger.error('Error fetching data:', error)
      }
    }

    fetchData()
  }, [initialTitle, fetchSearchData, fetchDefaultData, fetchDefData])

  const modifiedSetData: Dispatch<SetStateAction<T | null>> = useCallback(
    (value: SetStateAction<T | null>) => {
      if (typeof value === 'function') {
        setData(() => {
          /* eslint-disable-next-line */
          const newData = (value as (prevState: T | null) => T | null)(null)
          return newData || defaultData
        })
      } else {
        setData(value || defaultData)
      }
    },
    [defaultData]
  )

  return {
    data,
    setData: modifiedSetData,
    defaultData,
    initialQuery,
    setInitialQuery,
  }
}
