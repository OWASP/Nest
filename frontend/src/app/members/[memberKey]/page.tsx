'use client'
import { useQuery } from '@apollo/client/react'
import Image from 'next/image'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import React, { useEffect, useMemo } from 'react'
import { FaCodeMerge, FaFolderOpen, FaPersonWalkingArrowRight, FaUserPlus } from 'react-icons/fa6'
import { handleAppError, ErrorDisplay } from 'app/global-error'

import { GetUserDataDocument } from 'types/__generated__/userQueries.generated'
import { Badge } from 'types/badge'
import { formatDate } from 'utils/dateFormatter'
import Badges from 'components/Badges'
import DetailsCard from 'components/CardDetailsPage'
import ContributionHeatmap from 'components/ContributionHeatmap'
import MemberDetailsPageSkeleton from 'components/skeletons/MemberDetailsPageSkeleton'

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

  const formattedBio = user?.bio?.split(' ').map((word, index) => {
    const mentionMatch = word.match(/^@([\w-]+(?:\.[\w-]+)*)([^\w@])?$/)
    if (mentionMatch && mentionMatch.length > 1) {
      const username = mentionMatch[1]
      const punctuation = mentionMatch[2] || ''
      return (
        <React.Fragment key={`mention-${username}-${index}`}>
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
    return <span key={`word-${word}-${index}`}>{word} </span>
  })

  if (isLoading) {
    return (
      <div data-testid="user-loading-skeleton">
        <MemberDetailsPageSkeleton />
      </div>
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

  const userDetails = [
    { label: 'Joined', value: user?.createdAt ? formatDate(user.createdAt) : 'Not available' },
    { label: 'Email', value: user?.email || 'N/A' },
    { label: 'Company', value: user?.company || 'N/A' },
    { label: 'Location', value: user?.location || 'N/A' },
  ]

  const userStats = [
    { icon: FaPersonWalkingArrowRight, value: user?.followersCount || 0, unit: 'Follower' },
    { icon: FaUserPlus, value: user?.followingCount || 0, unit: 'Following' },
    {
      icon: FaFolderOpen,
      pluralizedName: 'Repositories',
      unit: 'Repository',
      value: user?.publicRepositoriesCount ?? 0,
    },
    { icon: FaCodeMerge, value: user?.contributionsCount || 0, unit: 'Contribution' },
  ]

  const UserSummary = () => (
    <div className="mt-4 flex flex-col items-center lg:flex-row">
      <Image
        width={200}
        height={200}
        className="mr-4 h-[200px] w-[200px] rounded-full border-2 border-white bg-white object-cover shadow-md dark:border-gray-800 dark:bg-gray-600/60"
        src={user?.avatarUrl || '/placeholder.svg'}
        alt={user?.name || user?.login || 'User Avatar'}
      />
      <div className="w-full overflow-x-auto text-center lg:text-left">
        <div className="pl-0 lg:pl-4">
          <div className="flex items-center justify-center gap-3 text-center text-sm text-gray-500 lg:justify-start lg:text-left dark:text-gray-400">
            <Link
              href={user?.url || '#'}
              className="text-xl font-bold text-blue-400 hover:underline"
            >
              @{user?.login}
            </Link>
            {user?.badges && user.badges.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {user.badges.slice().map((badge: Badge) => (
                  <React.Fragment key={badge.id}>
                    <Badges
                      name={badge.name}
                      cssClass={badge.cssClass || 'medal'}
                      showTooltip={true}
                    />
                  </React.Fragment>
                ))}
              </div>
            )}
          </div>
          <p className="text-gray-600 dark:text-gray-400">{formattedBio}</p>
        </div>
        {hasContributionData && dateRange.startDate && dateRange.endDate && (
          <div className="w-full lg:block">
            <div className="overflow-x-auto rounded-lg bg-white dark:bg-gray-800">
              <ContributionHeatmap
                contributionData={contributionData}
                startDate={dateRange.startDate}
                endDate={dateRange.endDate}
                variant="medium"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )

  return (
    <DetailsCard
      details={userDetails}
      pullRequests={pullRequests}
      recentIssues={issues}
      recentMilestones={milestones}
      recentReleases={releases}
      repositories={topRepositories}
      showAvatar={false}
      stats={userStats}
      title={user?.name || user?.login}
      type="user"
      userSummary={<UserSummary />}
    />
  )
}

export default UserDetailsPage
