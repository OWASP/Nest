import { useEffect, useState } from 'react'

import Card from '../components/Card'
import Pagination from '../components/Pagination'
import SearchBar from '../components/Search'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { CommitteeDataType } from '../lib/types'
import { getFilteredIcons, handleSocialUrls } from '../lib/utils'
import { API_URL } from '../utils/credentials'

export default function Committees() {
  const [committeeData, setCommitteeData] = useState<CommitteeDataType | null>(null)
  const [defaultCommittees, setDefaultCommittees] = useState<CommitteeDataType | null>(null)
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [totalPages, setTotalPages] = useState<number>(1)
  const [isLoaded, setLoading] = useState<boolean>(false)
  useEffect(() => {
    if (committeeData) return
    document.title = 'OWASP Committees'
    const fetchApiData = async () => {
      try {
        const response = await fetch(`${API_URL}/owasp/search/committee?page=${currentPage}`)
        const data = await response.json()
        setCommitteeData(data)
        setDefaultCommittees(data)
        setTotalPages(data.total_pages)
        setLoading(true)
      } catch (error) {
        console.error(error)
      }
    }
    fetchApiData()
  }, [currentPage])
  useEffect(() => {
    setTotalPages(committeeData?.total_pages || 1)
  }, [committeeData])
  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({
      top: 0,
      behavior: 'auto',
    })
  }

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text md:p-20">
      <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
        <SearchBar
          placeholder="Search for OWASP projects..."
          searchEndpoint={`${API_URL}/owasp/search/committee`}
          onSearchResult={setCommitteeData}
          defaultResults={defaultCommittees}
          currentPage={currentPage}
        />
        {committeeData &&
          committeeData?.committees?.map((committee, index) => {
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
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        isLoaded={isLoaded}
        onPageChange={handlePageChange}
      />
    </div>
  )
}
