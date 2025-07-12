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
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import type { DetailsCardProps } from 'types/card'
import { ExtendedSession } from 'types/program'
import { capitalize } from 'utils/capitalize'
import { IS_PROJECT_HEALTH_ENABLED } from 'utils/credentials'
import { getSocialIcon } from 'utils/urlIconMappings'
import ActionButton from 'components/ActionButton'
import AnchorTitle from 'components/AnchorTitle'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import HealthMetrics from 'components/HealthMetrics'
import InfoBlock from 'components/InfoBlock'
import LeadersList from 'components/LeadersList'
import Milestones from 'components/Milestones'
import ModuleCard from 'components/ModuleCard'
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
  isDraft,
  setPublish,
  tags,
  domains,
  modules,
  mentors,
  admins,
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
  const { data } = useSession()
  const router = useRouter()
  let scoreStyle = 'bg-green-400 text-green-900'
  if (type === 'project' && healthMetricsData.length > 0) {
    const score = healthMetricsData[0].score
    if (score < 50) {
      scoreStyle = 'bg-red-400 text-red-900'
    } else if (score < 75) {
      scoreStyle = 'bg-yellow-400 text-yellow-900'
    }
  }
  return (
    <div className="min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <div className="mt-4 flex flex-row items-center">
          <div className="flex w-full items-center justify-between">
            <h1 className="text-4xl font-bold">{title}</h1>
            {type === 'program' &&
              admins?.some(
                (admin) => admin.login === ((data as ExtendedSession)?.user?.login as string)
              ) && (
                <div className="flex gap-2">
                  <ActionButton
                    onClick={() => {
                      router.push(`${window.location.pathname}/edit`)
                    }}
                    children="Edit Program"
                  />

                  <ActionButton
                    children=" Add Module"
                    onClick={() => {
                      router.push(`${window.location.pathname}/createModule`)
                    }}
                  />
                  {isDraft && (
                    <ActionButton children="Publish" onClick={() => setPublish && setPublish()} />
                  )}
                </div>
              )}

            {type === 'module' &&
              admins?.some(
                (admin) => admin.login === ((data as ExtendedSession)?.user?.login as string)
              ) && (
                <button
                  className="flex items-center justify-center gap-2 text-nowrap rounded-md border border-[#0D6EFD] bg-transparent px-2 py-2 text-[#0D6EFD] text-blue-600 transition-all hover:bg-[#0D6EFD] hover:text-white dark:border-sky-600 dark:text-sky-600 dark:hover:bg-sky-100"
                  onClick={() => {
                    router.push(`${window.location.pathname}/edit`)
                  }}
                >
                  Edit Module
                </button>
              )}
            {IS_PROJECT_HEALTH_ENABLED && type === 'project' && healthMetricsData.length > 0 && (
              <Link href="#issues-trend">
                <div
                  className={`group relative flex h-20 w-20 flex-col items-center justify-center rounded-full border-2 shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-xl ${scoreStyle}`}
                >
                  <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                  <div className="relative z-10 flex flex-col items-center text-center">
                    <span className="text-xs font-semibold uppercase tracking-wide opacity-90">
                      Health
                    </span>
                    <span className="text-xl font-black leading-none">
                      {healthMetricsData[0].score}
                    </span>
                    <span className="text-xs font-semibold uppercase tracking-wide opacity-90">
                      Score
                    </span>
                  </div>
                  {healthMetricsData[0].score < 30 && (
                    <div className="animate-pulse absolute inset-0 rounded-full bg-red-400/20"></div>
                  )}
                </div>
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
            className={
              type === 'program' || type === 'module'
                ? 'gap-2 md:col-span-7'
                : type !== 'chapter'
                  ? 'gap-2 md:col-span-5'
                  : 'gap-2 md:col-span-3'
            }
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
        {(type === 'program' || type === 'module') && (
          <div
            className={`mb-8 grid grid-cols-1 gap-6 ${tags?.length === 0 || domains?.length === 0 ? 'md:col-span-1' : 'md:grid-cols-2'}`}
          >
            {tags.length !== 0 && (
              <ToggleableList items={tags} icon={faTags} label={<AnchorTitle title="Tags" />} />
            )}
            {domains.length !== 0 && (
              <ToggleableList
                items={domains}
                icon={faChartPie}
                label={<AnchorTitle title="Domains" />}
              />
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
        {admins && admins.length > 0 && type === 'program' && (
          <TopContributorsList
            icon={faUsers}
            contributors={admins}
            maxInitialDisplay={6}
            label="Admins"
          />
        )}
        {mentors && mentors.length > 0 && (
          <TopContributorsList
            icon={faUsers}
            contributors={mentors}
            maxInitialDisplay={6}
            label="Mentors"
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
              <RepositoriesCard repositories={repositories} />
            </SecondaryCard>
          )}
        {type === 'program' && modules.length > 0 && (
          <SecondaryCard icon={faFolderOpen} title={<AnchorTitle title="Modules" />}>
            <ModuleCard modules={modules} />
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

export const SocialLinks = ({ urls }) => {
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
