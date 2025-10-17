import RecentIssues from 'components/RecentIssues'
import RecentPullRequests from 'components/RecentPullRequests'
import RecentReleases from 'components/RecentReleases'
import Milestones from 'components/Milestones'
import type { Issue } from 'types/issue'
import type { PullRequest } from 'types/pullRequest'
import type { Milestone } from 'types/milestone'
import type { Release } from 'types/release'

interface ActivitySectionProps {
  type: string
  recentIssues?: Issue[]
  pullRequests?: PullRequest[]
  recentMilestones?: Milestone[]
  recentReleases?: Release[]
  showAvatar?: boolean
}

const ActivitySection = ({
  type,
  recentIssues,
  pullRequests,
  recentMilestones,
  recentReleases,
  showAvatar,
}: ActivitySectionProps) => (
  <>
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
          <RecentReleases data={recentReleases} showAvatar={showAvatar} showSingleColumn={true} />
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
  </>
)

export default ActivitySection;
