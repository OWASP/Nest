import type { DetailsCardProps } from 'types/card'
import { IS_PROJECT_HEALTH_ENABLED } from 'utils/env.client'
import CardDetailsContributions from 'components/CardDetailsPage/CardDetailsContributions'
import CardDetailsContributors from 'components/CardDetailsPage/CardDetailsContributors'
import CardDetailsHeader from 'components/CardDetailsPage/CardDetailsHeader'
import CardDetailsIssuesMilestones from 'components/CardDetailsPage/CardDetailsIssuesMilestones'
import CardDetailsMetadata from 'components/CardDetailsPage/CardDetailsMetadata'
import CardDetailsRepositoriesModules from 'components/CardDetailsPage/CardDetailsRepositoriesModules'
import CardDetailsSummary from 'components/CardDetailsPage/CardDetailsSummary'
import CardDetailsTags from 'components/CardDetailsPage/CardDetailsTags'
import HealthMetrics from 'components/HealthMetrics'
import Leaders from 'components/Leaders'
import SponsorCard from 'components/SponsorCard'

export type CardType =
  | 'chapter'
  | 'committee'
  | 'module'
  | 'organization'
  | 'program'
  | 'project'
  | 'repository'
  | 'user'

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
  geolocationData = [],
  healthMetricsData,
  isActive = true,
  isArchived = false,
  languages,
  onLoadMorePullRequests,
  onResetPullRequests,
  isFetchingMore,
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
  const hasContributions = !!(
    (contributionStats && contributionStats.total > 0) ||
    (contributionData && Object.keys(contributionData).length > 0)
  )

  return (
    <div className="min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <CardDetailsHeader
          title={title}
          description={description}
          type={type}
          status={status}
          setStatus={setStatus}
          canUpdateStatus={canUpdateStatus}
          programKey={programKey}
          entityKey={entityKey}
          accessLevel={accessLevel}
          admins={admins}
          mentors={mentors}
          isActive={isActive}
          isArchived={isArchived}
          healthMetricsData={healthMetricsData}
        />

        <CardDetailsSummary summary={summary} userSummary={userSummary} />

        <CardDetailsMetadata
          type={type}
          details={details}
          entityKey={entityKey}
          stats={stats}
          geolocationData={geolocationData}
          socialLinks={socialLinks}
        />

        <CardDetailsTags
          type={type}
          entityKey={entityKey}
          languages={languages}
          topics={topics}
          tags={tags}
          domains={domains}
          labels={labels}
        />

        {entityLeaders && entityLeaders.length > 0 && (
          <div className="mb-8">
            <Leaders users={entityLeaders} />
          </div>
        )}

        <CardDetailsContributions
          type={type}
          hasContributions={hasContributions}
          contributionStats={contributionStats}
          contributionData={contributionData}
          startDate={startDate}
          endDate={endDate}
        />

        <CardDetailsContributors
          type={type}
          entityKey={entityKey}
          programKey={programKey}
          topContributors={topContributors}
          admins={admins}
          mentors={mentors}
          mentees={mentees}
        />

        <CardDetailsIssuesMilestones
          type={type}
          recentIssues={recentIssues}
          recentMilestones={recentMilestones}
          pullRequests={pullRequests}
          recentReleases={recentReleases}
          showAvatar={showAvatar}
          onLoadMorePullRequests={onLoadMorePullRequests}
          onResetPullRequests={onResetPullRequests}
          isFetchingMore={isFetchingMore}
        />

        <CardDetailsRepositoriesModules
          type={type}
          programKey={programKey}
          accessLevel={accessLevel}
          repositories={repositories}
          modules={modules}
          admins={admins}
        />
        {IS_PROJECT_HEALTH_ENABLED &&
          type === 'project' &&
          healthMetricsData &&
          healthMetricsData.length > 0 && <HealthMetrics data={healthMetricsData} />}

        {entityKey &&
          ['chapter', 'project', 'repository'].includes(type) &&
          (projectName || title) &&
          (() => {
            return (
              <SponsorCard
                target={entityKey}
                title={(projectName || title) as string}
                type={type === 'chapter' ? 'chapter' : 'project'}
              />
            )
          })()}
      </div>
    </div>
  )
}

export default DetailsCard
