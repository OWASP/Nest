import {
  faUsers,
  faCodeFork,
  faStar,
  faCode,
  faCalendar,
  faFileCode,
  faTag,
  faBook,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { DetailsCardProps } from 'types/card'
import { formatDate } from 'utils/dateFormatter'
import { getSocialIcon } from 'utils/urlIconMappings'
import ChapterMap from 'components/ChapterMap'
import InfoBlock from 'components/InfoBlock'
import ItemCardList from 'components/ItemCardList'
import SecondaryCard from 'components/SecondaryCard'
import TopContributors from 'components/ToggleContributors'
import ToggleableList from 'components/ToogleList'

const DetailsCard = ({
  title,
  is_active = true,
  summary,
  description,
  projectStats,
  details,
  socialLinks,
  type,
  topContributors,
  languages,
  topics,
  recentIssues,
  recentReleases,
  geolocationData = null,
}: DetailsCardProps) => {
  return (
    <div className="mt-16 min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 mt-4 text-4xl font-bold">{title}</h1>
        <p className="mb-6 text-xl">{description}</p>
        {!is_active && (
          <span className="ml-2 rounded bg-red-200 px-2 py-1 text-sm text-red-800">Inactive</span>
        )}
        <SecondaryCard title="Summary">
          <p>{summary}</p>
        </SecondaryCard>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
          <SecondaryCard
            title={`${type[0].toUpperCase() + type.slice(1)} Details`}
            className={`${type === 'project' ? 'md:col-span-5' : 'md:col-span-3'} gap-2`}
          >
            {details &&
              details.map((detail, index) => (
                <div key={index}>
                  <strong>{detail.label}:</strong> {detail.value}
                </div>
              ))}
            {socialLinks && type === 'chapter' && <SocialLinks urls={socialLinks || []} />}
          </SecondaryCard>
          {type === 'project' && (
            <SecondaryCard title="Statistics" className="md:col-span-2">
              <InfoBlock
                className="pb-1"
                icon={faUsers}
                value={`${projectStats.Contributors || 'No'} Contributors`}
              />
              <InfoBlock
                className="pb-1"
                icon={faCodeFork}
                value={`${projectStats.Forks || 'No'} Forks`}
              />
              <InfoBlock
                className="pb-1"
                icon={faStar}
                value={`${projectStats.Stars || 'No'} Stars`}
              />
              <InfoBlock
                className="pb-1"
                icon={faCode}
                value={`${projectStats.Repositories || 'No'} Repositories`}
              />
              <InfoBlock
                className="pb-1"
                icon={faBook}
                value={`${projectStats.Issues || 'No'} Issues`}
              />
            </SecondaryCard>
          )}
          {type === 'chapter' && geolocationData && (
            <SecondaryCard title="Chapter Location" className="md:col-span-4">
              <ChapterMap
                geoLocData={geolocationData ? [geolocationData] : []}
                style={{ height: '200px', width: '100%', zIndex: '0' }}
              />
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

export default DetailsCard

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
