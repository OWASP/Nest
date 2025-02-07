import { Button } from '@chakra-ui/react'
import { faEllipsisH } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'

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
    const pageNumbers: (number | string)[] = []
    const maxVisiblePages = 7

    if (totalPages <= maxVisiblePages) {
      return Array.from({ length: totalPages }, (_, i) => i + 1)
    }

    for (let i = 1; i <= 3; i++) {
      pageNumbers.push(i)
    }

    if (currentPage > 4) {
      pageNumbers.push('...')
    }

    for (
      let i = Math.max(4, currentPage - 1);
      i <= Math.min(totalPages - 1, currentPage + 1);
      i++
    ) {
      if (!pageNumbers.includes(i)) {
        pageNumbers.push(i)
      }
    }

    if (currentPage < totalPages - 3) {
      pageNumbers.push('...')
    }

    if (totalPages > 3 && !pageNumbers.includes(totalPages)) {
      pageNumbers.push(totalPages)
    }

    return pageNumbers
  }

  const pageNumbers = getPageNumbers()
  if (!isLoaded || totalPages <= 1) return null

  return (
    <div className="mt-8 flex flex-col items-center justify-center space-y-3">
      <div className="flex flex-wrap items-center justify-center gap-2">
        <Button
          className="flex h-10 min-w-[2.5rem] items-center justify-center rounded-md border border-gray-200 bg-white px-3 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
          onClick={() => onPageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
        >
          Prev
        </Button>
        {pageNumbers.map((number, index) => (
          <React.Fragment key={index}>
            {number === '...' ? (
              <span className="flex h-10 w-10 items-center justify-center text-gray-600 dark:text-gray-400">
                <FontAwesomeIcon icon={faEllipsisH} className="h-5 w-5"></FontAwesomeIcon>
              </span>
            ) : (
              <Button
                className={`flex h-10 min-w-[2.5rem] items-center justify-center rounded-md px-3 text-sm font-medium ${
                  currentPage === number
                    ? 'bg-[#83a6cc] text-white dark:bg-white dark:text-black'
                    : 'border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
                onClick={() => onPageChange(number as number)}
              >
                {number}
              </Button>
            )}
          </React.Fragment>
        ))}
        <Button
          className="flex h-10 min-w-[2.5rem] items-center justify-center rounded-md border border-gray-200 bg-white px-3 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
          onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage === totalPages}
        >
          Next
        </Button>
      </div>
    </div>
  )
}

export default Pagination
