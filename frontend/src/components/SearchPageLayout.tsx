import React, { useState } from 'react'
import LoadingSpinner from 'components/LoadingSpinner'
import Pagination from 'components/Pagination'
import SearchBar from 'components/Search'

interface SearchPageLayoutProps {
  isLoaded: boolean
  totalPages: number
  currentPage: number
  searchQuery: string
  // eslint-disable-next-line no-unused-vars
  onSearch: (query: string) => void
  // eslint-disable-next-line no-unused-vars
  onPageChange: (page: number) => void
  searchPlaceholder: string
  empty: string
  indexName: string
  loadingImageUrl?: string
  children?: React.ReactNode
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
  children,
}: SearchPageLayoutProps) => {
  const [isSearchBarReady, setIsSearchBarReady] = useState(false)

  const handleSearchBarReady = () => {
    setIsSearchBarReady(true)
  }

  return (
    <div className="mt-16 flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text">
      {!isLoaded && !isSearchBarReady && (
        <div className="bg-background/50 fixed inset-0 flex items-center justify-center">
          <LoadingSpinner imageUrl={loadingImageUrl} />
        </div>
      )}
      <div className="w-full max-w-lg">
        <SearchBar
          indexName={indexName}
          onSearch={onSearch}
          placeholder={searchPlaceholder}
          initialValue={searchQuery}
          onReady={handleSearchBarReady}
        />
      </div>
      {isLoaded && isSearchBarReady && (
        <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
          {totalPages === 0 && <div className="text bg:text-white m-4 text-xl">{empty}</div>}
          {children}
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={onPageChange}
              isLoaded={isLoaded}
            />
          )}
        </div>
      )}
    </div>
  )
}

export default SearchPageLayout
