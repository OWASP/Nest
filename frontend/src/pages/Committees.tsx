import Card from '../components/Card'
import SearchBar from '../components/Search'
import { useSearchQuery } from '../hooks/useSearchquery'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { CommitteeDataType } from '../lib/types'
import { getFilteredIcons, handleSocialUrls } from '../lib/utils'
import { API_URL } from '../utils/credentials'

export default function Committees() {
  const {
    data: committeeData,
    setData: setCommitteeData,
    defaultData: defaultCommittees,
    initialQuery,
  } = useSearchQuery<CommitteeDataType>({
    apiUrl: `${API_URL}/owasp/search/committee`,
    entityKey: 'committees',
    initialTitle: 'OWASP Committees',
  })

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text">
      <div className="flex w-full flex-col items-center justify-normal gap-4">
        <SearchBar
          placeholder="Search for OWASP committees..."
          searchEndpoint={`${API_URL}/owasp/search/committee`}
          onSearchResult={setCommitteeData}
          defaultResults={defaultCommittees}
          initialQuery={initialQuery}
        />
        {committeeData?.committees?.map((committee, index) => {
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
    </div>
  )
}
