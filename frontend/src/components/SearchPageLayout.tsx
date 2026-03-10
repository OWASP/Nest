import { Skeleton } from '@heroui/skeleton'
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
  useEffect(() => {
    if (isLoaded && isFirstLoad) {
      setIsFirstLoad(false)
    }
  }, [isLoaded, isFirstLoad])
  const getSearchBarClassName = () => {
    if (inlineSort && filterChildren) return 'rounded-none'
    if (inlineSort) return 'rounded-r-none'
    return ''
  }

  return (
    <div className="text-text flex min-h-screen w-full flex-col items-center justify-normal p-5">
      <div className={`flex w-full items-center justify-center ${inlineSort ? 'gap-0' : 'gap-2'}`}>
        {filterChildren &&
          (isFirstLoad ? (
            <Skeleton
              className={`h-12 w-60 ${inlineSort ? 'rounded-l-lg rounded-r-none' : 'rounded-lg'}`}
              aria-hidden="true"
            />
          ) : (
            <div className={inlineSort ? '[&>div]:rounded-r-none' : ''}>{filterChildren}</div>
          ))}
        <SearchBar
          isLoaded={!isFirstLoad}
          onSearch={onSearch}
          placeholder={searchPlaceholder}
          initialValue={searchQuery}
          className={
            inlineSort && filterChildren ? 'rounded-none' : inlineSort ? 'rounded-r-none' : ''
          }
        />
        {inlineSort &&
          sortChildren &&
          (isFirstLoad ? (
            <div className="flex items-center">
              <Skeleton className="h-12 w-48 rounded-none" aria-hidden="true" />
            </div>
          ) : (
            <div className="[&>div>div:first-child]:rounded-l-none" data-testid="sort-inline">
              {sortChildren}
            </div>
          ))}
      </div>
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
