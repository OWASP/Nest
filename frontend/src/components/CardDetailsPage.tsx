import {
  faCircleInfo,
  faChartPie,
  faFolderOpen,
  faCode,
  faTags,
  faUsers,
  faRectangleList,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import upperFirst from 'lodash/upperFirst'
import { useSession } from 'next-auth/react'
import type { ExtendedSession } from 'types/auth'
import type { DetailsCardProps } from 'types/card'
import { IS_PROJECT_HEALTH_ENABLED } from 'utils/env.client'
import { scrollToAnchor } from 'utils/scrollToAnchor'
import { getSocialIcon } from 'utils/urlIconMappings'
import AnchorTitle from 'components/AnchorTitle'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import EntityActions from 'components/EntityActions'
import HealthMetrics from 'components/HealthMetrics'
import InfoBlock from 'components/InfoBlock'
import Leaders from 'components/Leaders'
import LeadersList from 'components/LeadersList'
import MenteeContributorsList from 'components/MenteeContributorsList'
import MetricsScoreCircle from 'components/MetricsScoreCircle'
import Milestones from 'components/Milestones'
import ModuleCard from 'components/ModuleCard'
import RecentIssues from 'components/RecentIssues'
import RecentPullRequests from 'components/RecentPullRequests'
import RecentReleases from 'components/RecentReleases'
import RepositoryCard from 'components/RepositoryCard'
import SecondaryCard from 'components/SecondaryCard'
import SponsorCard from 'components/SponsorCard'
import StatusBadge from 'components/StatusBadge'
import ToggleableList from 'components/ToggleableList'
import TopContributorsList from 'components/TopContributorsList'

const DetailsCard = ({
  description,
  details,
  accessLevel,
  status,
  setStatus,
  canUpdateStatus,
  tags,
  domains,
  entityLeaders,
  labels,
  modules,
  mentors,
  mentees,
  admins,
  entityKey,
  geolocationData = null,
  healthMetricsData,
  isActive = true,
  isArchived = false,
  languages,
  programKey,
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

  // compute styles based on type prop
  const secondaryCardStyles = (() => {
    if (type === 'program' || type === 'module') {
      return 'gap-2 md:col-span-7'
    } else if (type === 'chapter') {
      return 'gap-2 md:col-span-3'
    }
    return 'gap-2 md:col-span-5'
  })()

  return (
    <div className="min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <div className="mt-4 flex flex-row items-center">
          <div className="flex w-full items-center justify-between">
            <h1 className="text-4xl font-bold">{title}</h1>
            <div className="flex items-center gap-3">
              {type === 'program' && accessLevel === 'admin' && canUpdateStatus && (
                <EntityActions
                  type="program"
                  programKey={programKey}
                  status={status}
                  setStatus={setStatus}
                />
              )}
              {type === 'module' &&
                accessLevel === 'admin' &&
                admins?.some(
                  (admin) => admin.login === ((data as ExtendedSession)?.user?.login as string)
                ) && <EntityActions type="module" programKey={programKey} moduleKey={entityKey} />}
              {!isActive && <StatusBadge status="inactive" size="md" />}
              {isArchived && type === 'repository' && <StatusBadge status="archived" size="md" />}
              {IS_PROJECT_HEALTH_ENABLED && type === 'project' && healthMetricsData.length > 0 && (
                <MetricsScoreCircle
                  score={healthMetricsData[0].score}
                  clickable={true}
                  onClick={() => scrollToAnchor('issues-trend')}
                />
              )}
            </div>
          </div>
        </div>
        <p className="mb-6 text-xl">{description}</p>
        {summary && (
          <SecondaryCard icon={faCircleInfo} title={<AnchorTitle title="Summary" />}>
            <p>{summary}</p>
          </SecondaryCard>
        )}

        {userSummary && <SecondaryCard>{userSummary}</SecondaryCard>}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
          <SecondaryCard
            icon={faRectangleList}
            title={<AnchorTitle title={`${upperFirst(type)} Details`} />}
            className={secondaryCardStyles}
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
              {stats.map((stat) => (
                <div key={`${stat.unit}-${stat.value}`}>
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
          <>
            {((tags?.length || 0) > 0 || (domains?.length || 0) > 0) && (
              <div
                className={`mb-8 grid grid-cols-1 gap-6 ${(tags?.length || 0) === 0 || (domains?.length || 0) === 0 ? 'md:col-span-1' : 'md:grid-cols-2'}`}
              >
                {tags?.length > 0 && (
                  <ToggleableList
                    items={tags}
                    icon={faTags}
                    label={<AnchorTitle title="Tags" />}
                    isDisabled={true}
                  />
                )}
                {domains?.length > 0 && (
                  <ToggleableList
                    items={domains}
                    icon={faChartPie}
                    label={<AnchorTitle title="Domains" />}
                    isDisabled={true}
                  />
                )}
              </div>
            )}
            {labels?.length > 0 && (
              <div className="mb-8">
                <ToggleableList
                  items={labels}
                  icon={faTags}
                  label={<AnchorTitle title="Labels" />}
                  isDisabled={true}
                />
              </div>
            )}
          </>
        )}
        {entityLeaders && entityLeaders.length > 0 && <Leaders users={entityLeaders} />}
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
        {mentees && mentees.length > 0 && (
          <MenteeContributorsList
            icon={faUsers}
            contributors={mentees}
            maxInitialDisplay={6}
            label="Mentees"
            programKey={programKey || ''}
            moduleKey={entityKey || ''}
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
              <RepositoryCard maxInitialDisplay={4} repositories={repositories} />
            </SecondaryCard>
          )}
        {type === 'program' && modules.length > 0 && (
          <SecondaryCard
            icon={faFolderOpen}
            title={<AnchorTitle title={modules.length === 1 ? 'Module' : 'Modules'} />}
          >
            <ModuleCard modules={modules} accessLevel={accessLevel} admins={admins} />
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
        {urls.map((url) => (
          <a
            key={url}
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
