import { faCalendar, faFileCode, faTag } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { DetailsCardProps } from 'types/card'
import { capitalize } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import { pluralize } from 'utils/pluralize'
import { getSocialIcon } from 'utils/urlIconMappings'
import AnchorTitle from 'components/AnchorTitle'
import ChapterMap from 'components/ChapterMap'
import InfoBlock from 'components/InfoBlock'
import ItemCardList from 'components/ItemCardList'
import RepositoriesCard from 'components/RepositoriesCard'
import SecondaryCard from 'components/SecondaryCard'
import ToggleableList from 'components/ToggleableList'
import TopContributors from 'components/TopContributors'
import LeadersList from './LeadersList'

const DetailsCard = ({
  title,
  is_active = true,
  summary,
  description,
  heatmap,
  stats,
  details,
  socialLinks,
  type,
  topContributors,
  languages,
  pullRequests,
  topics,
  recentIssues,
  recentReleases,
  showAvatar = true,
  userSummary,
  geolocationData = null,
  repositories = [],
}: DetailsCardProps) => {
  return (
    <div className="mt-16 min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 mt-4 text-4xl font-bold">{title && capitalize(title)}</h1>
        <p className="mb-6 text-xl">{description}</p>
        {!is_active && (
          <span className="ml-2 rounded bg-red-200 px-2 py-1 text-sm text-red-800">Inactive</span>
        )}
        {summary && (
          <SecondaryCard title={<AnchorTitle href="#summary" title="Summary" />}>
            <p>{summary}</p>
          </SecondaryCard>
        )}

        {userSummary && (
          <SecondaryCard title={<AnchorTitle href="#summary" title="Summary" />}>
            {userSummary}
          </SecondaryCard>
        )}

        {heatmap && (
          <SecondaryCard
            title={<AnchorTitle href="#contribution-heatmap" title="Contribution Heatmap" />}
          >
            {heatmap}
          </SecondaryCard>
        )}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
          <SecondaryCard
            title={<AnchorTitle href={`#${type}-details`} title={`${capitalize(type)} Details`} />}
            className={`${type !== 'chapter' ? 'md:col-span-5' : 'md:col-span-3'} gap-2`}
          >
            {details?.map((detail) =>
              detail?.label === 'Leaders' ? (
                <div key={detail.label} className="pb-1">
                  <strong>{detail.label}:</strong>{' '}
                  <LeadersList leaders={detail?.value != null ? String(detail.value) : 'Unknown'} />
                </div>
              ) : (
                <div key={detail.label} className="pb-1">
                  <strong>{detail.label}:</strong> {detail?.value || 'Unknown'}
                </div>
              )
            )}
            {socialLinks && (type === 'chapter' || type === 'committee') && (
              <SocialLinks urls={socialLinks || []} />
            )}
          </SecondaryCard>
          {(type === 'project' ||
            type === 'repository' ||
            type === 'committee' ||
            type === 'user') && (
            <SecondaryCard
              title={<AnchorTitle href="#statistics" title="Statistics" />}
              className="md:col-span-2"
            >
              {stats.map((stat, index) => (
                <InfoBlock key={index} className="pb-1" icon={stat.icon} value={stat.value} />
              ))}
            </SecondaryCard>
          )}
          {type === 'chapter' && geolocationData && (
            <div className="mb-8 h-[250px] md:col-span-4 md:h-auto">
              <ChapterMap
                geoLocData={geolocationData ? [geolocationData] : []}
                showLocal={true}
                style={{
                  borderRadius: '0.5rem',
                  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                  height: '100%',
                  width: '100%',
                  zIndex: '0',
                }}
              />
            </div>
          )}
        </div>
        {(type === 'project' || type === 'repository') && (
          <div
            className={`mb-8 grid grid-cols-1 gap-6 ${topics.length === 0 || languages.length === 0 ? 'md:col-span-1' : 'md:grid-cols-2'}`}
          >
            {languages.length !== 0 && (
              <ToggleableList
                items={languages}
                label={<AnchorTitle href="#languages" title="Languages" />}
              />
            )}
            {topics.length !== 0 && (
              <ToggleableList
                items={topics}
                label={<AnchorTitle href="#topics" title="Topics" />}
              />
            )}
          </div>
        )}
        {topContributors && (
          <TopContributors
            contributors={topContributors}
            maxInitialDisplay={6}
            type="contributor"
          />
        )}
        {(type === 'project' || type === 'repository' || type === 'user') && (
          <div className="grid-cols-2 gap-4 lg:grid">
            <ItemCardList
              title={<AnchorTitle href="#recent-issues" title="Recent Issues" />}
              data={recentIssues}
              showAvatar={showAvatar}
              renderDetails={(item) => (
                <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                  <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                  <span>{formatDate(item.createdAt)}</span>
                  {item?.commentsCount ? (
                    <>
                      <FontAwesomeIcon icon={faFileCode} className="ml-4 mr-2 h-4 w-4" />
                      <span>
                        {item.commentsCount} {pluralize(item.commentsCount, 'comment')}
                      </span>
                    </>
                  ) : null}
                </div>
              )}
            />
            {type === 'user' ? (
              <ItemCardList
                title={<AnchorTitle href="#recent-pull-requests" title="Recent Pull Requests" />}
                data={pullRequests}
                showAvatar={showAvatar}
                renderDetails={(item) => (
                  <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                    <span>{formatDate(item.createdAt)}</span>
                    {item?.commentsCount ? (
                      <>
                        <FontAwesomeIcon icon={faFileCode} className="ml-4 mr-2 h-4 w-4" />
                        <span>
                          {item.commentsCount} {pluralize(item.commentsCount, 'comment')}
                        </span>
                      </>
                    ) : null}
                  </div>
                )}
              />
            ) : (
              <ItemCardList
                title={<AnchorTitle href="#recent-releases" title="Recent Releases" />}
                data={recentReleases}
                showAvatar={showAvatar}
                renderDetails={(item) => (
                  <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                    <span>{formatDate(item.publishedAt)}</span>
                    <FontAwesomeIcon icon={faTag} className="ml-4 mr-2 h-4 w-4" />
                    <span>{item.tagName}</span>
                  </div>
                )}
              />
            )}
          </div>
        )}
        {type === 'user' && (
          <SecondaryCard title={<AnchorTitle href="#recent-releases" title="Recent Releases" />}>
            {recentReleases && recentReleases.length > 0 ? (
              <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                {recentReleases.map((item, index) => (
                  <div
                    key={index}
                    className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
                  >
                    <div className="flex w-full flex-col justify-between">
                      <div className="flex w-full items-center">
                        {showAvatar && (
                          <a
                            className="flex-shrink-0 text-blue-400 hover:underline dark:text-blue-200"
                            href={`/community/users/${item?.author?.login}`}
                          >
                            <img
                              src={item?.author?.avatarUrl}
                              alt={item?.author?.name}
                              className="mr-2 h-6 w-6 rounded-full"
                            />
                          </a>
                        )}
                        <h3 className="flex-1 overflow-hidden text-ellipsis whitespace-nowrap font-semibold">
                          <a
                            className="text-blue-500 hover:underline dark:text-blue-400"
                            href={item?.url}
                            target="_blank"
                          >
                            {item.name}
                          </a>
                        </h3>
                      </div>
                      <div className="ml-0.5 w-full">
                        <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                          <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                          <span>{formatDate(item.publishedAt)}</span>
                          <FontAwesomeIcon icon={faTag} className="ml-4 mr-2 h-4 w-4" />
                          <span>{item.tagName}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>Nothing to display.</p>
            )}
          </SecondaryCard>
        )}
        {(type === 'project' || type === 'user') && repositories.length > 0 && (
          <SecondaryCard
            title={<AnchorTitle href="#repositories" title="Repositories" />}
            className="mt-6"
          >
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
