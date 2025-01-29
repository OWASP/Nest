import {
  faUsers,
  faCodeFork,
  faStar,
  faBook,
  faCode,
  faCalendar,
  faFileCode,
  faTag,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { formatDate } from 'utils/dateFormatter'
import { getSocialIcon } from 'utils/urlIconMappings'
import InfoBlock from 'components/InfoBlock'
import ItemCardList from 'components/ItemCardList'
import SecondaryCard from 'components/SecondaryCard'
import TopContributors from 'components/ToggleContributors'
import ToggleableList from 'components/ToogleList'

const GenericDetails = ({
  title,
  is_active = false,
  summary,
  data,
  details,
  type,
  topContributors,
  languages,
  topics,
  recentIssues,
  recentReleases,
}) => {
  return (
    <div className="mt-16 min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 mt-4 text-4xl font-bold">{title}</h1>

        {!is_active && (
          <span className="ml-2 rounded bg-red-200 px-2 py-1 text-sm text-red-800">Inactive</span>
        )}
        <SecondaryCard title="Summary">
          <p>{summary}</p>
        </SecondaryCard>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <SecondaryCard
            title={`${type === 'project' ? 'Project' : 'Chapter'} Details`}
            className={`${type === 'project' ? 'md:col-span-2' : 'col-span-3'} gap-2`}
          >
            {details &&
              details.map((detail, index) => (
                <div key={index}>
                  <strong>{detail.label}:</strong> {detail.value}
                </div>
              ))}
            {type === 'chapter' && <SocialLinks urls={data.related_urls} />}
          </SecondaryCard>

          {type === 'project' && (
            <SecondaryCard title="Statistics">
              <>
                <InfoBlock
                  className="pb-1"
                  icon={faUsers}
                  value={`${data.contributors_count} Contributors`}
                />
                <InfoBlock className="pb-1" icon={faCodeFork} value={`${data.forks_count} Forks`} />
                <InfoBlock className="pb-1" icon={faStar} value={`${data.stars_count} Stars`} />
                <InfoBlock className="pb-1" icon={faBook} value={`${data.issues_count} Issues`} />
                <InfoBlock
                  className="pb-1"
                  icon={faCode}
                  value={`${data.repositories_count} Repositories`}
                />
              </>
            </SecondaryCard>
          )}
        </div>

        {type === 'project' && (
          <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
            <ToggleableList items={languages} label="Languages" />
            <ToggleableList items={topics} label="Topics" />
          </div>
        )}

        <TopContributors contributors={topContributors} maxInitialDisplay={6} />

        {type === 'project' && (
          <>
            <ItemCardList
              title="Recent Issues"
              data={recentIssues}
              renderDetails={(item) => (
                <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                  <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                  <span>{formatDate(item.createdAt)}</span>
                  <FontAwesomeIcon icon={faFileCode} className="ml-4 mr-2 h-4 w-4" />
                  <span>{item.commentsCount} comments</span>
                </div>
              )}
            />
            <ItemCardList
              title="Recent Releases"
              data={recentReleases}
              renderDetails={(item) => (
                <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                  <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                  <span>{formatDate(item.publishedAt)}</span>
                  <FontAwesomeIcon icon={faTag} className="ml-4 mr-2 h-4 w-4" />
                  <span>{item.tagName}</span>
                </div>
              )}
            />
          </>
        )}
      </div>
    </div>
  )
}

export default GenericDetails

const SocialLinks = ({ urls }) => (
  <div>
    <strong>Social Links</strong>
    <div className="mt-2 flex flex-wrap gap-3">
      {urls.map((url, index) => (
        <a
          key={index}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-600 transition-colors hover:text-gray-800 dark:text-blue-600 dark:hover:text-gray-200"
        >
          <FontAwesomeIcon icon={getSocialIcon(url)} className="h-5 w-5" />
        </a>
      ))}
    </div>
  </div>
)
