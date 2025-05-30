import {
  faCircleInfo,
  faSquarePollVertical,
  faChartPie,
  faFolderOpen,
  faCode,
  faTags,
  faUsers,
  faRectangleList,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Link from 'next/link'
import { DetailsCardProps } from 'types/card'
import { capitalize } from 'utils/capitalize'
import { getSocialIcon } from 'utils/urlIconMappings'
import AnchorTitle from 'components/AnchorTitle'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import InfoBlock from 'components/InfoBlock'
import LeadersList from 'components/LeadersList'
import Milestones from 'components/Milestones'
import RecentIssues from 'components/RecentIssues'
import RecentPullRequests from 'components/RecentPullRequests'
import RecentReleases from 'components/RecentReleases'
import RepositoriesCard from 'components/RepositoriesCard'
import SecondaryCard from 'components/SecondaryCard'
import ToggleableList from 'components/ToggleableList'
import TopContributors from 'components/TopContributors'

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
  key,
  topContributors,
  languages,
  pullRequests,
  topics,
  recentIssues,
  recentReleases,
  recentMilestones,
  showAvatar = true,
  userSummary,
  geolocationData = null,
  repositories = [],
}: DetailsCardProps) => {
  const getDonationUrl = () => {
    if (!key) return 'https://owasp.org/donate/'

    let repoPrefix = ''
    if (type === 'project') {
      repoPrefix = 'www-project-'
    } else if (type === 'chapter') {
      repoPrefix = 'www-chapter-'
    } else if (type === 'repository') {
      repoPrefix = ''
    }

    const encodedTitle = encodeURIComponent(`OWASP ${title || ''}`)
    return `https://owasp.org/donate/?reponame=${repoPrefix}${key}&title=${encodedTitle}`
  }

  const shouldShowSponsor = ['project', 'chapter', 'repository'].includes(type)

  return (
    <div className="min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 mt-4 text-4xl font-bold">{title}</h1>
        <p className="mb-6 text-xl">{description}</p>
        {!is_active && (
          <span className="ml-2 rounded bg-red-200 px-2 py-1 text-sm text-red-800">Inactive</span>
        )}
        {summary && (
          <SecondaryCard icon={faCircleInfo} title={<AnchorTitle title="Summary" />}>
            <p>{summary}</p>
          </SecondaryCard>
        )}

        {userSummary && (
          <SecondaryCard icon={faCircleInfo} title={<AnchorTitle title="Summary" />}>
            {userSummary}
          </SecondaryCard>
        )}

        {heatmap && (
          <SecondaryCard
            icon={faSquarePollVertical}
            title={<AnchorTitle title="Contribution Heatmap" />}
          >
            {heatmap}
          </SecondaryCard>
        )}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
          <SecondaryCard
            icon={faRectangleList}
            title={<AnchorTitle title={`${capitalize(type)} Details`} />}
            className={`${type !== 'chapter' ? 'md:col-span-5' : 'md:col-span-3'} gap-2`}
          >
            {details?.map((detail) =>
              detail?.label === 'Leaders' ? (
                <div key={detail.label} className="flex flex-row gap-1 pb-1">
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
            type === 'user' ||
            type === 'organization') && (
            <SecondaryCard
              icon={faChartPie}
              title={<AnchorTitle title="Statistics" />}
              className="md:col-span-2"
            >
              {stats.map((stat, index) => (
                <div key={index}>
                  <InfoBlock
                    className="pb-1"
                    icon={stat.icon}
                    pluralizedName={stat.pluralizedName}
                    unit={stat.unit}
                    value={stat.value}
                  />
                </div>
              ))}
            </SecondaryCard>
          )}
          {type === 'chapter' && geolocationData && (
            <div className="mb-8 h-[250px] md:col-span-4 md:h-auto">
              <ChapterMapWrapper
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
                icon={faCode}
                label={<AnchorTitle title="Languages" />}
              />
            )}
            {topics.length !== 0 && (
              <ToggleableList items={topics} icon={faTags} label={<AnchorTitle title="Topics" />} />
            )}
          </div>
        )}
        {topContributors && (
          <TopContributors
            icon={faUsers}
            contributors={topContributors}
            maxInitialDisplay={9}
            type="contributor"
          />
        )}
        {(type === 'project' ||
          type === 'repository' ||
          type === 'user' ||
          type === 'organization') && (
          <div className="grid-cols-2 gap-4 lg:grid">
            <RecentIssues data={recentIssues} showAvatar={showAvatar} />
            {type === 'user' ||
            type === 'organization' ||
            type === 'repository' ||
            type === 'project' ? (
              <Milestones data={recentMilestones} showAvatar={showAvatar} />
            ) : (
              <RecentReleases
                data={recentReleases}
                showAvatar={showAvatar}
                showSingleColumn={true}
              />
            )}
          </div>
        )}
        {(type === 'project' ||
          type === 'repository' ||
          type === 'organization' ||
          type === 'user') && (
          <div className="grid-cols-2 gap-4 lg:grid">
            <RecentPullRequests data={pullRequests} showAvatar={showAvatar} />
            <RecentReleases data={recentReleases} showAvatar={showAvatar} showSingleColumn={true} />
          </div>
        )}
        {(type === 'project' || type === 'user' || type === 'organization') &&
          repositories.length > 0 && (
            <SecondaryCard
              icon={faFolderOpen}
              title={<AnchorTitle title="Repositories" />}
              className="mt-6"
            >
              <RepositoriesCard repositories={repositories} />
            </SecondaryCard>
          )}

        {/* Sponsor Section */}
        {shouldShowSponsor && (
          <div className="mb-20 mt-8">
            <SecondaryCard className="text-center">
              <h3 className="mb-4 text-2xl font-semibold">Support Our Work</h3>
              <p className="mb-6 text-gray-600 dark:text-gray-400">
                Your contribution helps maintain and improve {title}. Support the OWASP community!
              </p>
              <Link
                href={getDonationUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block rounded bg-blue-500 px-6 py-3 font-bold text-white hover:bg-blue-600"
              >
                Sponsor {type === 'chapter' ? 'Chapter' : type === 'project' ? 'Project' : 'Repository'}
              </Link>
            </SecondaryCard>
          </div>
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
            className="text-blue-400 transition-colors hover:text-gray-800 dark:hover:text-gray-200"
          >
            <FontAwesomeIcon icon={getSocialIcon(url)} className="h-5 w-5" />
          </a>
        ))}
      </div>
    </div>
  )
}
