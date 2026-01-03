'use client'

import { useQuery } from '@apollo/client/react'
import Image from 'next/image'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useTheme } from 'next-themes'
import React, { useEffect, useRef, useState } from 'react'
import {
  FaCodeMerge,
  FaFolderOpen,
  FaPersonWalkingArrowRight,
  FaUserPlus,
} from 'react-icons/fa6'
import { handleAppError, ErrorDisplay } from 'app/global-error'

import { GetUserDataDocument } from 'types/__generated__/userQueries.generated'
import { Badge } from 'types/badge'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { RepositoryCardProps } from 'types/project'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
import type { User } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import {
  drawContributions,
  fetchHeatmapData,
  HeatmapData,
} from 'utils/helpers/githubHeatmap'
import Badges from 'components/Badges'
import DetailsCard from 'components/CardDetailsPage'
import MemberDetailsPageSkeleton from 'components/skeletons/MemberDetailsPageSkeleton'

const UserDetailsPage: React.FC = () => {
  const { memberKey } = useParams<{ memberKey: string }>()

  const { data, error, loading } = useQuery(GetUserDataDocument, {
    variables: { key: memberKey },
  })

  const [heatmapData, setHeatmapData] = useState<HeatmapData>({} as HeatmapData)
  const [username, setUsername] = useState('')
  const [isPrivateContributor, setIsPrivateContributor] = useState(false)

  useEffect(() => {
    if (error) {
      handleAppError(error)
    }
  }, [error])

  useEffect(() => {
    const fetchData = async () => {
      const result = await fetchHeatmapData(memberKey as string)
      if (!result) {
        setIsPrivateContributor(true)
        return
      }
      if (result?.contributions) {
        setUsername(memberKey as string)
        setHeatmapData(result as HeatmapData)
      }
    }
    fetchData()
  }, [memberKey])

  if (loading) {
    return (
      <div data-testid="user-loading-skeleton">
        <MemberDetailsPageSkeleton />
      </div>
    )
  }

  if (!data?.user) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="User not found"
        message="Sorry, the user you're looking for doesn't exist"
      />
    )
  }

  const {
    user,
    recentIssues,
    recentMilestones,
    recentPullRequests,
    recentReleases,
    topContributedRepositories,
  } = data

  const formattedBio = user.bio?.split(' ').map((word, index) => {
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

  const userDetails = [
    { label: 'Joined', value: user.createdAt ? formatDate(user.createdAt) : 'Not available' },
    { label: 'Email', value: user.email || 'N/A' },
    { label: 'Company', value: user.company || 'N/A' },
    { label: 'Location', value: user.location || 'N/A' },
  ]

  const userStats = [
    { icon: FaPersonWalkingArrowRight, value: user.followersCount, unit: 'Follower' },
    { icon: FaUserPlus, value: user.followingCount, unit: 'Following' },
    {
      icon: FaFolderOpen,
      pluralizedName: 'Repositories',
      unit: 'Repository',
      value: user.publicRepositoriesCount,
    },
    { icon: FaCodeMerge, value: user.contributionsCount, unit: 'Contribution' },
  ]

  const Heatmap = () => {
    const canvasRef = useRef<HTMLCanvasElement | null>(null)
    const [imgSrc, setImgSrc] = useState('')
    const { resolvedTheme } = useTheme()
    const isDarkMode = (resolvedTheme ?? 'light') === 'dark'

    useEffect(() => {
      if (canvasRef.current && heatmapData?.years?.length) {
        drawContributions(canvasRef.current, {
          data: heatmapData,
          username,
          themeName: isDarkMode ? 'dark' : 'light',
        })
        setImgSrc(canvasRef.current.toDataURL())
      } else {
        setImgSrc('')
      }
    }, [isDarkMode, heatmapData, username])

    return (
      <div className="overflow-hidden rounded-lg bg-white dark:bg-gray-800">
        <div className="relative">
          <canvas ref={canvasRef} style={{ display: 'none' }} aria-hidden="true" />
          {imgSrc ? (
            <div className="h-32">
              <Image
                width={100}
                height={100}
                src={imgSrc}
                className="h-full w-full object-cover object-[54%_60%]"
                alt="Contribution Heatmap"
              />
            </div>
          ) : (
            <div className="relative h-32">
              <Image
                height={100}
                width={100}
                src={
                  isDarkMode
                    ? '/img/heatmap-background-dark.png'
                    : '/img/heatmap-background-light.png'
                }
                className="h-full w-full object-cover object-[54%_60%]"
                alt="Heatmap Background"
              />
              <div className="heatmap-loader" />
            </div>
          )}
        </div>
      </div>
    )
  }

  const UserSummary = () => (
    <div className="mt-4 flex flex-col items-center lg:flex-row">
      <Image
        width={200}
        height={200}
        className="mr-4 h-[200px] w-[200px] rounded-full border-2 border-white bg-white object-cover shadow-md dark:border-gray-800 dark:bg-gray-600/60"
        src={user.avatarUrl || '/placeholder.svg'}
        alt={user.name || user.login || 'User Avatar'}
      />
      <div className="w-full text-center lg:text-left">
        <div className="pl-0 lg:pl-4">
          <div className="flex items-center justify-center gap-3 text-sm text-gray-500 lg:justify-start dark:text-gray-400">
            <Link href={user.url || '#'} className="text-xl font-bold text-blue-400 hover:underline">
              @{user.login}
            </Link>
            {user.badges?.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {user.badges.map((badge: Badge) => (
                  <Badges
                    key={badge.id}
                    name={badge.name}
                    cssClass={badge.cssClass || 'medal'}
                    showTooltip
                  />
                ))}
              </div>
            )}
          </div>
          <p className="text-gray-600 dark:text-gray-400">{formattedBio}</p>
        </div>
        {!isPrivateContributor && (
          <div className="hidden w-full lg:block">
            <Heatmap />
          </div>
        )}
      </div>
    </div>
  )

  return (
    <DetailsCard
      details={userDetails}
      pullRequests={recentPullRequests}
      recentIssues={recentIssues}
      recentMilestones={recentMilestones}
      recentReleases={recentReleases}
      repositories={topContributedRepositories as RepositoryCardProps[]}
      showAvatar={false}
      stats={userStats}
      title={user.name || user.login}
      type="user"
      userSummary={<UserSummary />}
    />
  )
}

export default UserDetailsPage
