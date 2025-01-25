import React, { useState } from 'react'
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
  const [isSearchBarReady, setIsSearchBarReady] = useState(false)

  const handleSearchBarReady = () => {
    setIsSearchBarReady(true)
  }

  return (
    <div className="mt-16 flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text">
      <div className="flex w-full items-center justify-center">
        <SearchBar
          indexName={indexName}
          onSearch={onSearch}
          placeholder={searchPlaceholder}
          initialValue={searchQuery}
          onReady={handleSearchBarReady}
        />
        <div>{sortChildren}</div>
      </div>
      {!isSearchBarReady || !isLoaded ? (
        <SkeletonBase indexName={indexName} loadingImageUrl={loadingImageUrl} />
      ) : (
        <>
          <div>
            {totalPages === 0 && <div className="text bg:text-white m-4 text-xl">{empty}</div>}
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
