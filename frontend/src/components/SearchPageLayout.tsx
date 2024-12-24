import LoadingSpinner from 'components/LoadingSpinner'
import Pagination from 'components/Pagination'
import SearchBar from 'components/Search'
import React from 'react'

interface SearchPageLayoutProps {
  isLoaded: boolean
  totalPages: number
  currentPage: number
  searchQuery: string
  /* eslint-disable-next-line */
  onSearch: (query: string) => void
  /* eslint-disable-next-line */
  onPageChange: (page: number) => void
  searchPlaceholder: string
  empty: string
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
  loadingImageUrl = '../public/img/owasp_icon_white_sm.png',
  children,
}: SearchPageLayoutProps) => {
  return (
    <div className="mt-16 flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text">
      {!isLoaded ? (
        <div className="bg-background/50 fixed inset-0 flex items-center justify-center">
          <LoadingSpinner imageUrl={loadingImageUrl} />
        </div>
      ) : (
        <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
          <SearchBar
            onSearch={onSearch}
            placeholder={searchPlaceholder}
            initialValue={searchQuery}
          />
          {totalPages === 0 && <div className="text bg:text-white m-4 text-xl">{empty}</div>}
          {children}
        </div>
      )}

      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={onPageChange}
          isLoaded={isLoaded}
        />
      )}
    </div>
  )
}

export default SearchPageLayout
