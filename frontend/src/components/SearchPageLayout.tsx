import React, { useEffect, useState } from 'react'
import Pagination from './Pagination'
import SearchBar from './Search'
import SkeletonBase from './SkeletonsBase'
interface SearchPageLayoutProps {
  isLoaded: boolean
  totalPages: number
  currentPage: number
  searchQuery: string

  onSearch: (query: string) => void

  onPageChange: (page: number) => void
  searchPlaceholder: string
  empty: string
  indexName: string
  loadingImageUrl?: string
  children?: React.ReactNode
  sortChildren?: React.ReactNode
}

const SearchPageLayout = ({
  isLoaded,
  totalPages,
  currentPage,
  searchQuery,
  onSearch,
  onPageChange,
  searchPlaceholder,
  empty,
  indexName,
  loadingImageUrl = '/img/owasp_icon_white_sm.png',
  sortChildren,
  children,
}: SearchPageLayoutProps) => {
  const [isFirstLoad, setIsFirstLoad] = useState<boolean>(true)
  useEffect(() => {
    if (isLoaded && isFirstLoad) {
      setIsFirstLoad(false)
    }
  }, [isLoaded, isFirstLoad])
  return (
    <div className="mt-16 flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text">
      <div className="flex w-full items-center justify-center">
        <SearchBar
          isLoaded={isFirstLoad}
          onSearch={onSearch}
          placeholder={searchPlaceholder}
          initialValue={searchQuery}
        />
      </div>
      {!isLoaded ? (
        <SkeletonBase indexName={indexName} loadingImageUrl={loadingImageUrl} />
      ) : (
        <>
          <div>
            {totalPages !== 0 && <div className="flex justify-end">{sortChildren}</div>}
            {totalPages === 0 && <div className="text m-4 text-xl dark:text-white">{empty}</div>}
            {children}
          </div>
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={onPageChange}
              isLoaded={isLoaded}
            />
          )}
        </>
      )}
    </div>
  )
}

export default SearchPageLayout
