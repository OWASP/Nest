import { useEffect, useState } from 'react'

import Card from '../components/Card'
import LoadingSpinner from '../components/LoadingSpinner'
import { Modal } from '../components/Modal/Modal'
import Pagination from '../components/Pagination'
import SearchBar from '../components/Search'
import { loadData } from '../lib/api'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { IssuesDataType } from '../lib/types'
import { getFilteredIcons } from '../lib/utils'
import { logger } from '../utils/logger'

export default function ContributePage() {
  const [contributeData, setContributeData] = useState<IssuesDataType | null>(null)
  const [modalOpenIndex, setModalOpenIndex] = useState<number | null>(null)
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [isLoaded, setIsLoaded] = useState<boolean>(false)

  useEffect(() => {
    document.title = 'OWASP Issues'
    setIsLoaded(false)
    const fetchData = async () => {
      try {
        const data = await loadData<IssuesDataType>('owasp/search/issue', searchQuery, currentPage)
        setContributeData(data)
      } catch (error) {
        logger.error(error)
      }
      setIsLoaded(true)
    }
    fetchData()
  }, [currentPage, searchQuery])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setCurrentPage(1)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({
      top: 0,
      behavior: 'auto',
    })
  }

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text">
      <SearchBar onSearch={handleSearch} placeholder="Search for OWASP projects..." />
      {!isLoaded ? (
        <div className="bg-background/50 fixed inset-0 flex items-center justify-center">
          <LoadingSpinner imageUrl="../public/img/owasp_icon_white_sm.png" />
        </div>
      ) : contributeData && contributeData?.total_pages === 0 ? (
        <div>No issues found</div>
      ) : (
        <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
          {contributeData &&
            contributeData.issues.map((issue, index) => {
              const params: string[] = ['idx_created_at', 'idx_comments_count']
              const filteredIcons = getFilteredIcons(issue, params)

              const SubmitButton = {
                label: 'Read More',
                icon: <FontAwesomeIconWrapper icon="fa-solid fa-wand-magic-sparkles" />,
                onclick: () => setModalOpenIndex(index),
              }

              return (
                <>
                  <Card
                    key={issue.objectID || `issue-${index}`}
                    title={issue.idx_title}
                    url={issue.idx_url}
                    projectName={issue.idx_project_name}
                    projectLink={issue.idx_project_url}
                    summary={issue.idx_summary}
                    languages={issue.idx_repository_languages}
                    icons={filteredIcons}
                    button={SubmitButton}
                  />
                  <Modal
                    isOpen={modalOpenIndex === index}
                    onClose={() => setModalOpenIndex(null)}
                    title={issue.idx_title}
                    summary={issue.idx_summary}
                    hint={issue.idx_hint}
                  ></Modal>
                </>
              )
            })}
        </div>
      )}

      <Pagination
        currentPage={currentPage}
        totalPages={contributeData?.total_pages || 0}
        onPageChange={handlePageChange}
        isLoaded={isLoaded}
      />
    </div>
  )
}
