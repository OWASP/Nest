import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import Link from 'next/link'
import { useState } from 'react'
import {
  FaCalendar,
  FaCircleCheck,
  FaCircleExclamation,
  FaFolderOpen,
  FaSignsPost,
  FaCodeBranch,
} from 'react-icons/fa6'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
import { formatDate } from 'utils/dateFormatter'
import AnchorTitle from 'components/AnchorTitle'
import type { CardType } from 'components/CardDetailsPage'
import MentorshipPullRequest from 'components/MentorshipPullRequest'
import Milestones from 'components/Milestones'
import RecentIssues from 'components/RecentIssues'
import RecentPullRequests from 'components/RecentPullRequests'
import RecentReleases from 'components/RecentReleases'
import SecondaryCard from 'components/SecondaryCard'
import ShowMoreButton from 'components/ShowMoreButton'
import { TruncatedText } from 'components/TruncatedText'

interface CardDetailsIssuesMilestonesProps {
  type: CardType
  recentIssues?: Issue[]
  recentMilestones?: Milestone[]
  pullRequests?: PullRequest[]
  recentReleases?: Release[]
  showAvatar?: boolean
}

const MILESTONE_LIMIT = 4

const showIssuesAndMilestones = (type: CardType): boolean =>
  ['organization', 'project', 'repository', 'user'].includes(type)

const showPullRequestsAndReleases = (type: CardType): boolean =>
  ['organization', 'project', 'repository', 'user'].includes(type)

const CardDetailsIssuesMilestones = ({
  type,
  recentIssues,
  recentMilestones,
  pullRequests,
  recentReleases,
  showAvatar = true,
}: CardDetailsIssuesMilestonesProps) => {
  const [showAllMilestones, setShowAllMilestones] = useState(false)
  const [showAllPRs, setShowAllPRs] = useState(false)

  return (
    <>
      {showIssuesAndMilestones(type) && (
        <div className="grid-cols-2 gap-4 lg:grid">
          {recentIssues && <RecentIssues data={recentIssues} showAvatar={showAvatar} />}
          {recentMilestones && <Milestones data={recentMilestones} showAvatar={showAvatar} />}
        </div>
      )}
      {showPullRequestsAndReleases(type) && (
        <div className="grid-cols-2 gap-4 lg:grid">
          {pullRequests && <RecentPullRequests data={pullRequests} showAvatar={showAvatar} />}
          {recentReleases && (
            <RecentReleases data={recentReleases} showAvatar={showAvatar} showSingleColumn={true} />
          )}
        </div>
      )}
      {type === 'module' && pullRequests && pullRequests.length > 0 && (
        <SecondaryCard icon={FaCodeBranch} title={<AnchorTitle title="Recent Pull Requests" />}>
          <div className="grid grid-cols-1 gap-3">
            {pullRequests.slice(0, showAllPRs ? undefined : 4).map((pr) => (
              <MentorshipPullRequest key={pr.id} pr={pr} />
            ))}
            {pullRequests.length > 4 && (
              <ShowMoreButton onToggle={() => setShowAllPRs(!showAllPRs)} />
            )}
          </div>
        </SecondaryCard>
      )}
      {type === 'program' && recentMilestones && recentMilestones.length > 0 && (
        <SecondaryCard icon={FaSignsPost} title={<AnchorTitle title="Recent Milestones" />}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-1 md:grid-cols-2">
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
                              alt={`${milestone.author?.name || milestone.author?.login}'s avatar`}
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
                            rel="noopener noreferrer"
                          >
                            <TruncatedText text={milestone.title} />
                          </Link>
                        ) : (
                          <TruncatedText text={milestone.title} />
                        )}
                      </h3>
                    </div>
                    <div className="ml-0.5 w-full">
                      <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <div className="flex items-center">
                          <FaCalendar className="mr-2 h-4 w-4" />
                          {milestone.createdAt && <span>{formatDate(milestone.createdAt)}</span>}
                        </div>
                        <div className="flex items-center">
                          <FaCircleCheck className="mr-2 h-4 w-4" />
                          <span>{milestone.closedIssuesCount ?? 0} closed</span>
                        </div>
                        <div className="flex items-center">
                          <FaCircleExclamation className="mr-2 h-4 w-4" />
                          <span>{milestone.openIssuesCount ?? 0} open</span>
                        </div>
                        {milestone?.repositoryName && milestone?.organizationName && (
                          <div className="flex min-w-0 flex-1 items-center overflow-hidden">
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
    </>
  )
}

export default CardDetailsIssuesMilestones
