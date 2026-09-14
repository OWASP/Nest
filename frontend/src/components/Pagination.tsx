import { Button } from '@heroui/button'
import React from 'react'
import { FaEllipsis } from 'react-icons/fa6'

interface PaginationProps {
  currentPage: number
  totalPages: number
  isLoaded: boolean

  onPageChange: (page: number) => void
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  isLoaded,
}) => {
  const getPageNumbers = (): (number | string)[] => {
    const maxVisiblePages = 7

    if (totalPages <= maxVisiblePages) {
      return Array.from({ length: totalPages }, (_, i) => i + 1)
    }

    const pagesToShow = new Set<number>([1, totalPages])
    for (const offset of [-1, 0, 1]) {
      const page = currentPage + offset
      if (Number.isSafeInteger(page) && page >= 1 && page <= totalPages) {
        pagesToShow.add(page)
      }
    }

    const sortedPages = [...pagesToShow].sort((a, b) => a - b)
    const pageNumbers: (number | string)[] = []

    for (let index = 0; index < sortedPages.length; index++) {
      const page = sortedPages[index]
      if (index > 0) {
        const gap = page - sortedPages[index - 1]
        if (gap > 1) {
          pageNumbers.push('...')
        }
      }
      pageNumbers.push(page)
    }

    return pageNumbers
  }

  if (!isLoaded || !Number.isFinite(totalPages) || totalPages <= 1) return null

  const pageNumbers = getPageNumbers()

  return (
    <div className="mt-8 flex flex-col items-center justify-center gap-3">
      <div className="flex flex-wrap items-center justify-center gap-2">
        <Button
          type="button"
          className="flex h-10 min-w-10 items-center justify-center rounded-md border-1 border-gray-200 bg-white px-3 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
          onPress={() => onPageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
          aria-label="Go to previous page"
        >
          Prev
        </Button>
        {pageNumbers.map((number, index) => (
          // eslint-disable-next-line react/no-array-index-key
          <React.Fragment key={`pagination-${index}-${number}`}>
            {number === '...' ? (
              <div className="flex h-10 w-10 items-center justify-center text-gray-600 dark:text-gray-400">
                <FaEllipsis className="h-5 w-5" aria-hidden="true" />
              </div>
            ) : (
              <Button
                type="button"
                aria-current={currentPage === number ? 'page' : undefined}
                aria-label={`Go to page ${number}`}
                className={`flex h-10 min-w-10 items-center justify-center rounded-md px-3 text-sm font-medium ${
                  currentPage === number
                    ? 'bg-[#83a6cc] text-white dark:bg-white dark:text-black'
                    : 'border-1 border-gray-200 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
                onPress={() => onPageChange(number as number)}
              >
                {number}
              </Button>
            )}
          </React.Fragment>
        ))}
        <Button
          type="button"
          className="flex h-10 min-w-10 items-center justify-center rounded-md border-1 border-gray-200 bg-white px-3 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
          onPress={() => onPageChange(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage === totalPages}
          aria-label="Go to next page"
        >
          Next
        </Button>
      </div>
    </div>
  )
}

export default Pagination
