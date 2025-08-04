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
import type { DetailsCardProps } from 'types/card'
import { capitalize } from 'utils/capitalize'
import { IS_PROJECT_HEALTH_ENABLED } from 'utils/credentials'
import { getSocialIcon } from 'utils/urlIconMappings'
import AnchorTitle from 'components/AnchorTitle'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import HealthMetrics from 'components/HealthMetrics'
import InfoBlock from 'components/InfoBlock'
import LeadersList from 'components/LeadersList'
import MetricsScoreCircle from 'components/MetricsScoreCircle'
import Milestones from 'components/Milestones'
import RecentIssues from 'components/RecentIssues'
import RecentPullRequests from 'components/RecentPullRequests'
import RecentReleases from 'components/RecentReleases'
import RepositoriesCard from 'components/RepositoriesCard'
import SecondaryCard from 'components/SecondaryCard'
import SponsorCard from 'components/SponsorCard'
import ToggleableList from 'components/ToggleableList'
import TopContributorsList from 'components/TopContributorsList'

const DetailsCard = ({
  description,
  details,
  entityKey,
  geolocationData = null,
  healthMetricsData,
  heatmap,
  isActive = true,
  languages,
  projectName,
  pullRequests,
  recentIssues,
  recentMilestones,
  recentReleases,
  repositories = [],
  showAvatar = true,
  socialLinks,
  stats,
  summary,
  title,
  topContributors,
  topics,
  type,
  userSummary,
}: DetailsCardProps) => {
  return (
    <div className="min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <div className="mt-4 flex flex-row items-center">
          <div className="flex w-full items-center justify-between">
            <h1 className="text-4xl font-bold">{title}</h1>
            {IS_PROJECT_HEALTH_ENABLED && type === 'project' && healthMetricsData.length > 0 && (
              <Link href="#issues-trend">
                <MetricsScoreCircle score={healthMetricsData[0].score} />
              </Link>
            )}
          </div>
          {!isActive && (
            <span className="ml-4 justify-center rounded bg-red-200 px-2 py-1 text-sm text-red-800">
              Inactive
            </span>
          )}
        </div>
        <p className="mb-6 text-xl">{description}</p>
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
                geoLocData={geolocationData}
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
          <TopContributorsList
            contributors={topContributors}
            icon={faUsers}
            maxInitialDisplay={12}
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
            <SecondaryCard icon={faFolderOpen} title={<AnchorTitle title="Repositories" />}>
              <RepositoriesCard maxInitialDisplay={4} repositories={repositories} />
            </SecondaryCard>
          )}
        {IS_PROJECT_HEALTH_ENABLED && type === 'project' && healthMetricsData.length > 0 && (
          <HealthMetrics data={healthMetricsData} />
        )}
        {entityKey && ['chapter', 'project', 'repository'].includes(type) && (
          <SponsorCard
            target={entityKey}
            title={projectName || title}
            type={type === 'chapter' ? 'chapter' : 'project'}
          />
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
