import { Tooltip } from '@heroui/tooltip'
import upperFirst from 'lodash/upperFirst'
import Image from 'next/image'
import Link from 'next/link'
import { useSession } from 'next-auth/react'
import { useState } from 'react'
import {
  FaCircleInfo,
  FaChartPie,
  FaFolderOpen,
  FaCode,
  FaTags,
  FaRectangleList,
  FaCalendar,
  FaCircleCheck,
  FaCircleExclamation,
  FaSignsPost,
} from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import type { ExtendedSession } from 'types/auth'
import type { DetailsCardProps } from 'types/card'
import { formatDate } from 'utils/dateFormatter'
import { IS_PROJECT_HEALTH_ENABLED } from 'utils/env.client'
import { scrollToAnchor } from 'utils/scrollToAnchor'
import { getMemberUrl, getMenteeUrl } from 'utils/urlFormatter'
import { getSocialIcon } from 'utils/urlIconMappings'
import AnchorTitle from 'components/AnchorTitle'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import ContributionHeatmap from 'components/ContributionHeatmap'
import ContributionStats from 'components/ContributionStats'
import ContributorsList from 'components/ContributorsList'
import EntityActions from 'components/EntityActions'
import HealthMetrics from 'components/HealthMetrics'
import InfoBlock from 'components/InfoBlock'
import Leaders from 'components/Leaders'
import LeadersList from 'components/LeadersList'
import Markdown from 'components/MarkdownWrapper'
import MetricsScoreCircle from 'components/MetricsScoreCircle'
import Milestones from 'components/Milestones'
import ModuleCard from 'components/ModuleCard'
import RecentIssues from 'components/RecentIssues'
import RecentPullRequests from 'components/RecentPullRequests'
import RecentReleases from 'components/RecentReleases'
import RepositoryCard from 'components/RepositoryCard'
import SecondaryCard from 'components/SecondaryCard'
import ShowMoreButton from 'components/ShowMoreButton'
import SponsorCard from 'components/SponsorCard'
import StatusBadge from 'components/StatusBadge'
import ToggleableList from 'components/ToggleableList'

import { TruncatedText } from 'components/TruncatedText'

export type CardType =
  | 'chapter'
  | 'committee'
  | 'module'
  | 'organization'
  | 'program'
  | 'project'
  | 'repository'
  | 'user'

const showStatistics = (type: CardType): boolean =>
  ['committee', 'organization', 'project', 'repository', 'user'].includes(type)

const showIssuesAndMilestones = (type: CardType): boolean =>
  ['organization', 'project', 'repository', 'user'].includes(type)

const showPullRequestsAndReleases = (type: CardType): boolean =>
  ['organization', 'project', 'repository', 'user'].includes(type)

const MILESTONE_LIMIT = 4

const DetailsCard = ({
  description,
  details,
  accessLevel,
  contributionData,
  contributionStats,
  endDate,
  startDate,
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
  const { data: session } = useSession() as { data: ExtendedSession | null }
  const [showAllMilestones, setShowAllMilestones] = useState(false)

  // compute styles based on type prop
  const typeStylesMap = {
    chapter: 'gap-2 md:col-span-3',
    module: 'gap-2 md:col-span-7',
    program: 'gap-2 md:col-span-7',
  }

  const hasContributions =
    (contributionStats && contributionStats.total > 0) ||
    (contributionData && Object.keys(contributionData).length > 0)

  const secondaryCardStyles = typeStylesMap[type] ?? 'gap-2 md:col-span-5'

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
                admins?.some((admin) => admin.login === session?.user?.login) && (
                  <EntityActions type="module" programKey={programKey} moduleKey={entityKey} />
                )}
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
          <SecondaryCard icon={FaCircleInfo} title={<AnchorTitle title="Summary" />}>
            <Markdown content={summary} />
          </SecondaryCard>
        )}

        {userSummary && <SecondaryCard>{userSummary}</SecondaryCard>}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
          <SecondaryCard
            icon={FaRectangleList}
            title={<AnchorTitle title={`${upperFirst(type)} Details`} />}
            className={secondaryCardStyles}
          >
            {details?.map((detail) =>
              detail?.label === 'Leaders' ? (
                <div key={detail.label} className="flex flex-row gap-1 pb-1">
                  <strong>{detail.label}:</strong>{' '}
                  <LeadersList
                    entityKey={`${entityKey}-${detail.label}`}
                    leaders={detail?.value == null ? 'Unknown' : String(detail.value)}
                  />
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
          {showStatistics(type) && (
            <SecondaryCard
              icon={FaChartPie}
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
                showLocationSharing={true}
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
                entityKey={`${entityKey}-languages`}
                items={languages}
                icon={FaCode}
                label={<AnchorTitle title="Languages" />}
              />
            )}
            {topics.length !== 0 && (
              <ToggleableList
                entityKey={`${entityKey}-topics`}
                items={topics}
                icon={FaTags}
                label={<AnchorTitle title="Topics" />}
              />
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
                    entityKey={`${entityKey}-tags`}
                    items={tags}
                    icon={FaTags}
                    label={<AnchorTitle title="Tags" />}
                    isDisabled={true}
                  />
                )}
                {domains?.length > 0 && (
                  <ToggleableList
                    entityKey={`${entityKey}-domains`}
                    items={domains}
                    icon={FaChartPie}
                    label={<AnchorTitle title="Domains" />}
                    isDisabled={true}
                  />
                )}
              </div>
            )}
            {labels?.length > 0 && (
              <div className="mb-8">
                <ToggleableList
                  entityKey={`${entityKey}-labels`}
                  items={labels}
                  icon={FaTags}
                  label={<AnchorTitle title="Labels" />}
                  isDisabled={true}
                />
              </div>
            )}
          </>
        )}
        {entityLeaders && entityLeaders.length > 0 && <Leaders users={entityLeaders} />}
        {(type === 'project' || type === 'chapter') && hasContributions && (
          <div className="mb-8">
            <div className="rounded-lg bg-gray-100 px-4 pt-6 shadow-md sm:px-6 lg:px-10 dark:bg-gray-800">
              {contributionStats && (
                <ContributionStats
                  title={`${type === 'project' ? 'Project' : 'Chapter'} Contribution Activity`}
                  stats={contributionStats}
                />
              )}
              {contributionData &&
                Object.keys(contributionData).length > 0 &&
                startDate &&
                endDate && (
                  <div className="flex w-full items-center justify-center">
                    <div className="w-full">
                      <ContributionHeatmap
                        contributionData={contributionData}
                        startDate={startDate}
                        endDate={endDate}
                        unit="contribution"
                      />
                    </div>
                  </div>
                )}
            </div>
          </div>
        )}
        {topContributors && (
          <ContributorsList
            contributors={topContributors}
            icon={HiUserGroup}
            maxInitialDisplay={12}
            label="Top Contributors"
            getUrl={getMemberUrl}
          />
        )}
        {admins && admins.length > 0 && type === 'program' && (
          <ContributorsList
            icon={HiUserGroup}
            contributors={admins}
            maxInitialDisplay={6}
            label="Admins"
            getUrl={getMemberUrl}
          />
        )}
        {mentors && mentors.length > 0 && (
          <ContributorsList
            icon={HiUserGroup}
            contributors={mentors}
            maxInitialDisplay={6}
            label="Mentors"
            getUrl={getMemberUrl}
          />
        )}
        {mentees && mentees.length > 0 && (
          <ContributorsList
            icon={HiUserGroup}
            contributors={mentees}
            maxInitialDisplay={6}
            label="Mentees"
            getUrl={(login) => getMenteeUrl(programKey || '', entityKey || '', login)}
          />
        )}
        {showIssuesAndMilestones(type) && (
          <div className="grid-cols-2 gap-4 lg:grid">
            <RecentIssues data={recentIssues} showAvatar={showAvatar} />
            <Milestones data={recentMilestones} showAvatar={showAvatar} />
          </div>
        )}
        {showPullRequestsAndReleases(type) && (
          <div className="grid-cols-2 gap-4 lg:grid">
            <RecentPullRequests data={pullRequests} showAvatar={showAvatar} />
            <RecentReleases data={recentReleases} showAvatar={showAvatar} showSingleColumn={true} />
          </div>
        )}
        {(type === 'project' || type === 'user' || type === 'organization') &&
          repositories.length > 0 && (
            <SecondaryCard icon={FaFolderOpen} title={<AnchorTitle title="Repositories" />}>
              <RepositoryCard maxInitialDisplay={4} repositories={repositories} />
            </SecondaryCard>
          )}
        {type === 'program' && modules.length > 0 && (
          <SecondaryCard
            icon={FaFolderOpen}
            title={<AnchorTitle title={modules.length === 1 ? 'Module' : 'Modules'} />}
          >
            <ModuleCard modules={modules} accessLevel={accessLevel} admins={admins} />
          </SecondaryCard>
        )}
        {type === 'program' && recentMilestones && recentMilestones.length > 0 && (
          <SecondaryCard icon={FaSignsPost} title={<AnchorTitle title="Recent Milestones" />}>
            <div className="grid gap-4 gap-y-0 sm:grid-cols-1 md:grid-cols-2">
              {recentMilestones
                .slice(0, showAllMilestones ? recentMilestones.length : MILESTONE_LIMIT)
                .map((milestone, index) => (
                  <div
                    key={milestone.url || `${milestone.title}-${index}`}
                    className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
                  >
                    <div className="flex w-full flex-col justify-between">
                      <div className="flex w-full items-center">
                        {showAvatar && milestone?.author?.login && milestone?.author?.avatarUrl && (
                          <Tooltip
                            closeDelay={100}
                            content={milestone?.author?.name || milestone?.author?.login}
                            id={`avatar-tooltip-${index}`}
                            delay={100}
                            placement="bottom"
                            showArrow
                          >
                            <Link
                              className="shrink-0 text-blue-400 hover:underline"
                              href={`/members/${milestone?.author?.login}`}
                            >
                              <Image
                                height={24}
                                width={24}
                                src={milestone?.author?.avatarUrl}
                                alt={
                                  milestone.author &&
                                    (milestone.author.name || milestone.author.login)
                                    ? `${milestone.author.name || milestone.author.login}'s avatar`
                                    : "Author's avatar"
                                }
                                className="mr-2 rounded-full"
                              />
                            </Link>
                          </Tooltip>
                        )}
                        <h3 className="min-w-0 flex-1 overflow-hidden font-semibold text-ellipsis whitespace-nowrap">
                          {milestone?.url ? (
                            <Link
                              className="text-blue-400 hover:underline"
                              href={milestone?.url}
                              target="_blank"
                            >
                              <TruncatedText text={milestone.title} />
                            </Link>
                          ) : (
                            <TruncatedText text={milestone.title} />
                          )}
                        </h3>
                      </div>
                      <div className="ml-0.5 w-full">
                        <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
                          <div className="mr-4 flex items-center">
                            <FaCalendar className="mr-2 h-4 w-4" />
                            <span>{formatDate(milestone.createdAt)}</span>
                          </div>
                          <div className="mr-4 flex items-center">
                            <FaCircleCheck className="mr-2 h-4 w-4" />
                            <span>{milestone.closedIssuesCount} closed</span>
                          </div>
                          <div className="mr-4 flex items-center">
                            <FaCircleExclamation className="mr-2 h-4 w-4" />
                            <span>{milestone.openIssuesCount} open</span>
                          </div>
                          {milestone?.repositoryName && milestone?.organizationName && (
                            <div className="flex flex-1 items-center overflow-hidden">
                              <FaFolderOpen className="mr-2 h-5 w-4 shrink-0" />
                              <Link
                                href={`/organizations/${milestone.organizationName}/repositories/${milestone.repositoryName}`}
                                className="cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap text-gray-600 hover:underline dark:text-gray-400"
                              >
                                <TruncatedText text={milestone.repositoryName} />
                              </Link>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
            {recentMilestones.length > MILESTONE_LIMIT && (
              <ShowMoreButton onToggle={() => setShowAllMilestones(!showAllMilestones)} />
            )}
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
        {urls.map((url) => {
          const SocialIcon = getSocialIcon(url)
          return (
            <a
              key={url}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 transition-colors hover:text-gray-800 dark:hover:text-gray-200"
            >
              <SocialIcon className="h-5 w-5" />
            </a>
          )
        })}
      </div>
    </div>
  )
}
