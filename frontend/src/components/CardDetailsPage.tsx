import { useSession } from 'next-auth/react'
import type { ExtendedSession } from 'types/auth'
import type { DetailsCardProps } from 'types/card'
import { useRouter } from 'next/navigation'
import HeaderSection from './HeaderSection'
import SummarySection from './SummarySection'
import DetailsSection from './DetailsSection'
import MetricsSection from './MetricsSection'
import ListsSection from './ListsSection'
import ContributorsSection from './ContributorsSection'
import ActivitySection from './ActivitySection'
import RepositoriesSection from './RepositoriesSection'
import ModulesSection from './ModulesSection'
import HealthSection from './HealthSection'
import SponsorsSection from './SponsorsSection'

const DetailsCard = ({
  description,
  details,
  accessLevel,
  status,
  setStatus,
  canUpdateStatus,
  tags,
  domains,
  modules,
  mentors,
  admins,
  entityKey,
  geolocationData = null,
  healthMetricsData,
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

  return (
    <div className="min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <HeaderSection
          title={title}
          type={type}
          accessLevel={accessLevel}
          status={status}
          setStatus={setStatus}
          canUpdateStatus={canUpdateStatus}
          admins={admins}
          description={description}
          userLogin={(data as ExtendedSession)?.user?.login}
          router={router}
          isActive={isActive}
          healthMetricsData={healthMetricsData}
        />
        <SummarySection summary={summary} userSummary={userSummary} />
        <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
          <DetailsSection
            details={details}
            socialLinks={socialLinks}
            type={type}
            geolocationData={geolocationData}
          />
          <MetricsSection stats={stats} type={type} />
        </div>
        <ListsSection
          languages={languages}
          topics={topics}
          tags={tags}
          domains={domains}
          type={type}
        />
        <ContributorsSection
          topContributors={topContributors}
          admins={admins}
          mentors={mentors}
          type={type}
        />
        <ActivitySection
          type={type}
          recentIssues={recentIssues}
          pullRequests={pullRequests}
          recentMilestones={recentMilestones}
          recentReleases={recentReleases}
          showAvatar={showAvatar}
        />
        <RepositoriesSection repositories={repositories} type={type} />
        <ModulesSection modules={modules} accessLevel={accessLevel} admins={admins} type={type} />
        <HealthSection healthMetricsData={healthMetricsData} type={type} />
        <SponsorsSection entityKey={entityKey} projectName={projectName} title={title} type={type} />
      </div>
    </div>
  )
}

export default DetailsCard;