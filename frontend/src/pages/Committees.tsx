import { useEffect, useState } from 'react'

import Card from '../components/Card'
import LoadingSpinner from '../components/LoadingSpinner'
import Pagination from '../components/Pagination'
import SearchBar from '../components/Search'
import { loadData } from '../lib/api'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { CommitteeDataType, CommitteeType } from '../lib/types'
import { getFilteredIcons, handleSocialUrls } from '../lib/utils'

const CommitteesPage = () => {
  const [Committees, setCommittees] = useState<CommitteeType[]>([])
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [totalPages, setTotalPages] = useState<number>(1)
  const [isLoaded, setIsLoaded] = useState<boolean>(false)
  useEffect(() => {
    document.title = 'OWASP Committees'
    const fetchApiData = async () => {
      setIsLoaded(false)
      try {
        const data = await loadData<CommitteeDataType>(
          'owasp/search/committee',
          searchQuery,
          currentPage
        )
        setCommittees(data.committees)
        setTotalPages(data.total_pages)
      } catch (error) {
        console.error(error)
      }
      setIsLoaded(true)
    }
    fetchApiData()
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
      <SearchBar onSearch={handleSearch} placeholder="Search for OWASP committees..." />
      {!isLoaded ? (
        <div className="bg-background/50 fixed inset-0 flex items-center justify-center">
          <LoadingSpinner imageUrl="../public/img/owasp_icon_white_sm.png" />
        </div>
      ) : (
        <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
          {totalPages === 0 && (
            <div className="text bg:text-white m-4 text-xl"> No committees found </div>
          )}
          {Committees &&
            Committees?.map((committee, index) => {
              const params: string[] = ['idx_updated_at']
              const filteredIcons = getFilteredIcons(committee, params)
              const formattedUrls = handleSocialUrls(committee.idx_related_urls)

              const SubmitButton = {
                label: 'Learn More',
                icon: <FontAwesomeIconWrapper icon="fa-solid fa-people-group" />,
                url: committee.idx_url,
              }

              return (
                <Card
                  key={committee.objectID || `committee-${index}`}
                  title={committee.idx_name}
                  url={committee.idx_url}
                  summary={committee.idx_summary}
                  icons={filteredIcons}
                  leaders={committee.idx_leaders}
                  topContributors={committee.idx_top_contributors}
                  button={SubmitButton}
                  social={formattedUrls}
                  tooltipLabel={`Learn more about ${committee.idx_name}`}
                />
              )
            })}
        </div>
      )}
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        isLoaded={isLoaded}
        onPageChange={handlePageChange}
      />
    </div>
  )
}
export default CommitteesPage
