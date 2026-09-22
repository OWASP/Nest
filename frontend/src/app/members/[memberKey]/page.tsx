'use client'
import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import React, { useEffect, useMemo } from 'react'
import { handleAppError, ErrorDisplay } from 'app/global-error'

import { GetUserDataDocument } from 'types/__generated__/userQueries.generated'
import { User } from 'types/user'
import MemberDetailSidebar from 'components/cards/MemberDetailSidebar'
import PageWrapper from 'components/cards/PageWrapper'
import RepositoriesModules from 'components/cards/RepositoriesModules'
import ContributionHeatmap from 'components/ContributionHeatmap'
import Milestones from 'components/Milestones'
import RecentIssues from 'components/RecentIssues'
import RecentPullRequests from 'components/RecentPullRequests'
import RecentReleases from 'components/RecentReleases'

import MemberDetailsPageSkeleton from 'components/skeletons/MemberDetailsPageSkeleton'

interface UserSummaryProps {
  user: User
  formattedBio: React.ReactNode
}

export const UserSummary: React.FC<UserSummaryProps> = ({ user, formattedBio }) => (
  <MemberDetailSidebar user={user} formattedBio={formattedBio} />
)

const UserDetailsPage: React.FC = () => {
  const { memberKey } = useParams<{ memberKey: string }>()

  const {
    data: graphQLData,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetUserDataDocument, {
    variables: { key: memberKey },
  })

  const user = graphQLData?.user
  const issues = graphQLData?.recentIssues || []
  const topRepositories = graphQLData?.topContributedRepositories || []
  const milestones = graphQLData?.recentMilestones || []
  const pullRequests = graphQLData?.recentPullRequests || []
  const releases = graphQLData?.recentReleases || []

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError, memberKey])

  const contributionData: Record<string, number> = useMemo(() => {
    if (user?.contributionData && typeof user.contributionData === 'object') {
      return user.contributionData as Record<string, number>
    }
    return {}
  }, [user?.contributionData])

  const dateRange = useMemo(() => {
    const dates = Object.keys(contributionData).sort((a, b) => a.localeCompare(b))
    if (dates.length === 0) {
      return { startDate: '', endDate: '' }
    }
    return {
      startDate: dates[0],
      endDate: dates.at(-1) ?? '',
    }
  }, [contributionData])

  const hasContributionData = Object.keys(contributionData).length > 0

  const formattedBio = user?.bio?.split(' ').map((word) => {
    const mentionMatch = word.match(/^@([\w-]+(?:\.[\w-]+)*)([^\w@])?$/)
    if (mentionMatch && mentionMatch.length > 1) {
      const username = mentionMatch[1]
      const punctuation = mentionMatch[2] || ''
      return (
        <React.Fragment key={`mention-${user.login}-${username}`}>
          <Link
            href={`https://github.com/${username}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:underline"
          >
            @{username}
          </Link>
          {punctuation}
          <span> </span>
        </React.Fragment>
      )
    }
    return <span key={`${user.login}-${word}`}>{word} </span>
  })

  if (isLoading) {
    return (
      <output>
        <MemberDetailsPageSkeleton />
      </output>
    )
  }

  if (graphQLRequestError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading user"
        message="An error occurred while loading the user data"
      />
    )
  }

  if (!graphQLData || !user) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="User not found"
        message="Sorry, the user you're looking for doesn't exist"
      />
    )
  }

  return (
    <PageWrapper>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-start">
          <aside className="w-full shrink-0 xl:w-[18rem]">
            <UserSummary user={user} formattedBio={formattedBio} />
          </aside>

          <div className="flex min-w-0 flex-1 flex-col gap-6">
            {hasContributionData && dateRange.startDate && dateRange.endDate && (
              <div className="rounded-lg bg-gray-100 pt-0 pr-4 pb-1 pl-1 shadow-md dark:bg-gray-800">
                <div className="overflow-x-auto">
                  <ContributionHeatmap
                    contributionData={contributionData}
                    startDate={dateRange.startDate}
                    endDate={dateRange.endDate}
                    variant="medium"
                  />
                </div>
              </div>
            )}

            {topRepositories.length > 0 && (
              <div className="flex flex-col [&>div]:mb-0! [&>div]:grow">
                <RepositoriesModules repositories={topRepositories} />
              </div>
            )}

            <div className="grid grow grid-cols-1 gap-6 md:grid-cols-2">
              {issues.length > 0 && (
                <div className="flex flex-col [&>div]:mb-0! [&>div]:grow">
                  <RecentIssues data={issues} showAvatar={false} />
                </div>
              )}
              {pullRequests.length > 0 && (
                <div className="flex flex-col [&>div]:mb-0! [&>div]:grow">
                  <RecentPullRequests data={pullRequests} showAvatar={false} />
                </div>
              )}
              {milestones.length > 0 && (
                <div className="flex flex-col [&>div]:mb-0! [&>div]:grow">
                  <Milestones data={milestones} showAvatar={false} />
                </div>
              )}
              {releases.length > 0 && (
                <div className="flex flex-col [&>div]:mb-0! [&>div]:grow">
                  <RecentReleases data={releases} showAvatar={false} showSingleColumn={true} />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}

export default UserDetailsPage
