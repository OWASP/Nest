import { faCalendar, faFileCode, faTag } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { DetailsCardProps } from 'types/card'
import { formatDate } from 'utils/dateFormatter'
import { getSocialIcon } from 'utils/urlIconMappings'
import ChapterMap from 'components/ChapterMap'
import HeatMap from 'components/HeatMap'
import InfoBlock from 'components/InfoBlock'
import ItemCardList from 'components/ItemCardList'
import RepositoriesCard from 'components/RepositoriesCard'
import SecondaryCard from 'components/SecondaryCard'
import ToggleableList from 'components/ToggleableList'
import TopContributors from 'components/ToggleContributors'

const DetailsCard = ({
  title,
  is_active = true,
  summary,
  avatarUrl,
  name = null,
  description,
  stats,
  details,
  socialLinks,
  type,
  topContributors,
  languages,
  topics,
  recentIssues,
  recentReleases,
  geolocationData = null,
  repositories = [],
}: DetailsCardProps) => {
  return (
    <div className="mt-16 min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 mt-4 text-4xl font-bold">
          {title && title[0].toUpperCase() + title.slice(1)}
        </h1>
        <p className="mb-6 text-xl">{description}</p>
        {!is_active && (
          <span className="ml-2 rounded bg-red-200 px-2 py-1 text-sm text-red-800">Inactive</span>
        )}
        {(type === 'project' || type === 'chapter') && (
          <SecondaryCard title="Summary">
            <p>{summary}</p>
          </SecondaryCard>
        )}


        <div className="grid grid-cols-7 gap-6 md:grid-cols-7">
          <div className="col-span-2">
            {type === 'user' && (
              <div className="mb-8 rounded-lg bg-gray-100 p-2 shadow-md dark:bg-gray-800 md:col-span-1">
                    <img
                    className="h-[300px] w-[300px] rounded-full border-4 border-white bg-white object-cover shadow-lg transition-colors dark:border-gray-800 dark:bg-gray-600/60"
                    src={avatarUrl}
                    alt={name}
                    />
                  </div>

            )}
          </div>

          <div className="col-span-5">
            {type === 'user' && (
              <SecondaryCard
                  title={`${type[0].toUpperCase() + type.slice(1)} Details`}
                  className={'md:col-span-5 gap-2'}
              >
                {details && details.map((detail, index) => (
                  <div key={index}>
                    <strong>{detail.label}:</strong> {detail.value ? detail.value : 'Unknown'}
                  </div>
                  ))}
              </SecondaryCard>
          )}
          </div>
        </div>



        <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
          {(type !== 'user') && (
            <SecondaryCard
            title={`${type[0].toUpperCase() + type.slice(1)} Details`}
            className={`${type !== 'chapter' ? 'md:col-span-5' : 'md:col-span-3'} gap-2`}
          >
            {details &&
              details.map((detail, index) => (
                <div key={index}>
                  <strong>{detail.label}:</strong> {detail.value ? detail.value : 'Unknown'}
                </div>
              ))}
            {socialLinks && (type === 'chapter' || type === 'committee') && (
              <SocialLinks urls={socialLinks || []} />
            )}
          </SecondaryCard>
          )}
          {(type === 'user') && (
            <HeatMap className={'md:col-span-5 gap-2'}
            >
            </HeatMap>
          )}



          {(type === 'project' || type === 'repository' || type === 'committee' || type === 'user') && (
            <SecondaryCard title="Statistics" className="md:col-span-2">
              {stats.map((stat, index) => (
                <InfoBlock key={index} className="pb-1" icon={stat.icon} value={stat.value} />
              ))}
            </SecondaryCard>
          )}
          {type === 'chapter' && geolocationData && (
            <div className="mb-8 h-[250px] md:col-span-4 md:h-auto">
              <ChapterMap
                geoLocData={geolocationData ? [geolocationData] : []}
                style={{ height: '100%', width: '100%', zIndex: '0' }}
              />
            </div>
          )}
        </div>

        {(type === 'project' || type === 'repository') && (
          <div
            className={`mb-8 grid grid-cols-1 gap-6 ${topics.length === 0 || languages.length === 0 ? 'md:col-span-1' : 'md:grid-cols-2'}`}
          >
            {languages.length !== 0 && <ToggleableList items={languages} label="Languages" />}
            {topics.length !== 0 && <ToggleableList items={topics} label="Topics" />}
          </div>
        )}

        <TopContributors contributors={topContributors} maxInitialDisplay={6} />

        {(type === 'project' || type === 'repository') && (
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
        {type === 'project' && repositories.length > 0 && (
          <SecondaryCard title="Repositories" className="mt-6">
            <RepositoriesCard repositories={repositories} />
          </SecondaryCard>
        )}
      </div>
    </div>
  )
}

export default DetailsCard

const SocialLinks = ({ urls }) => {
  if (!urls || urls.length === 0) return null
  return (
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
}
