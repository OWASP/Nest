import React, { useEffect, useState } from 'react'
import Pagination from 'components/Pagination'
import SearchBar from 'components/Search'
import SkeletonBase from 'components/SkeletonsBase'
interface SearchPageLayoutProps {
  isLoaded: boolean
  totalPages: number
  currentPage: number
  searchQuery: string

  onSearch: (query: string) => void

  onPageChange: (page: number) => void
  searchPlaceholder: string
  empty?: string
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
  loadingImageUrl = '/img/spinner_light.png',
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
    <div className="text-text flex min-h-screen w-full flex-col items-center justify-normal p-5">
      <div className="flex w-full items-center justify-center">
        <SearchBar
          isLoaded={!isFirstLoad}
          onSearch={onSearch}
          placeholder={searchPlaceholder}
          initialValue={searchQuery}
        />
      </div>
      {isLoaded ? (
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
      ) : (
        <SkeletonBase indexName={indexName} loadingImageUrl={loadingImageUrl} />
      )}
    </div>
  )
}

export default SearchPageLayout
