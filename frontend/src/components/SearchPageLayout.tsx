import { Skeleton } from '@heroui/skeleton'
import React, { useLayoutEffect, useState } from 'react'
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
  filterChildren?: React.ReactNode
  sortChildren?: React.ReactNode
  inlineSort?: boolean
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
  filterChildren,
  sortChildren,
  inlineSort = false,
  children,
}: SearchPageLayoutProps) => {
  const [isFirstLoad, setIsFirstLoad] = useState<boolean>(true)
  useLayoutEffect(() => {
    if (isLoaded && isFirstLoad) {
      setIsFirstLoad(false)
    }
  }, [isLoaded, isFirstLoad])

  let searchBarClassName = ''
  if (inlineSort && filterChildren) {
    // Square corners only on md+ (unified bar); keep rounded-lg on small screens
    searchBarClassName = 'md:rounded-none'
  } else if (inlineSort) {
    searchBarClassName = 'md:rounded-r-none'
  }

  return (
    <div className="text-text flex min-h-screen w-full flex-col items-center justify-normal p-5">
      <div
        className={`flex w-full flex-col md:flex-row md:items-center md:justify-center ${
          inlineSort ? 'md:gap-0' : 'md:gap-2'
        }`}
      >
        {filterChildren &&
          (isFirstLoad ? (
            <Skeleton
              className={`hidden h-12 w-60 shrink-0 md:block ${inlineSort ? 'rounded-l-lg rounded-r-none' : 'rounded-lg'}`}
              aria-hidden="true"
            />
          ) : (
            <div
              className={`hidden shrink-0 md:block md:w-fit ${inlineSort ? '[&>div]:rounded-r-none md:[&>div]:border-r-0' : ''}`}
            >
              {filterChildren}
            </div>
          ))}
        <div className="flex w-full justify-center md:w-[28rem] md:shrink-0">
          <SearchBar
            isLoaded={!isFirstLoad}
            onSearch={onSearch}
            placeholder={searchPlaceholder}
            initialValue={searchQuery}
            className={searchBarClassName}
          />
        </div>
        {inlineSort &&
          sortChildren &&
          (isFirstLoad ? (
            <div className="hidden shrink-0 md:flex md:w-fit md:items-center">
              <Skeleton className="h-12 w-48 rounded-none" aria-hidden="true" />
            </div>
          ) : (
            <div className="hidden shrink-0 md:flex md:w-fit [&>div>div:first-child]:rounded-l-none">
              {sortChildren}
            </div>
          ))}
      </div>

      {/* Mobile layout — max-w-md matches SearchBar so stacked controls align with search */}
      {(filterChildren || (inlineSort && sortChildren)) && (
        <div
          className={`mx-auto mt-2 mb-4 flex w-full max-w-md items-stretch md:hidden ${
            inlineSort ? 'gap-0' : 'justify-between gap-4'
          }`}
        >
          {filterChildren &&
            (isFirstLoad ? (
              <Skeleton
                className={`h-12 min-w-0 flex-1 ${inlineSort ? 'rounded-l-lg rounded-r-none' : 'max-w-40 rounded-lg'}`}
                aria-hidden="true"
              />
            ) : (
              <div
                className={`min-w-0 ${inlineSort && sortChildren ? 'flex-1' : 'max-w-40'} ${inlineSort ? '[&>div]:rounded-r-none' : ''}`}
              >
                {filterChildren}
              </div>
            ))}
          {inlineSort &&
            sortChildren &&
            (isFirstLoad ? (
              <Skeleton className="h-12 min-w-0 flex-1 rounded-none" aria-hidden="true" />
            ) : (
              <div className="min-w-0 flex-1 [&>div>div:first-child]:rounded-l-none">
                {sortChildren}
              </div>
            ))}
        </div>
      )}
      {isLoaded ? (
        <>
          <div>
            {!inlineSort && totalPages !== 0 && (
              <div className="flex justify-end" data-testid="sort-below">
                {sortChildren}
              </div>
            )}
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
