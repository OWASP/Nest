'use client'
import { useQuery } from '@apollo/client/react'
import Image from 'next/image'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useTheme } from 'next-themes'
import React, { useState, useEffect, useRef } from 'react'
import { FaCodeMerge, FaFolderOpen, FaPersonWalkingArrowRight, FaUserPlus } from 'react-icons/fa6'
import { handleAppError, ErrorDisplay } from 'app/global-error'

import { GetUserDataDocument } from 'types/__generated__/userQueries.generated'
import { Badge } from 'types/badge'
import { formatDate } from 'utils/dateFormatter'
import { drawContributions, fetchHeatmapData, HeatmapData } from 'utils/helpers/githubHeatmap'
import Badges from 'components/Badges'
import DetailsCard from 'components/CardDetailsPage'
import MemberDetailsPageSkeleton from 'components/skeletons/MemberDetailsPageSkeleton'

const UserDetailsPage: React.FC = () => {
  const { memberKey } = useParams<{ memberKey: string }>()
  const [data, setData] = useState<HeatmapData>({} as HeatmapData)
  const [username, setUsername] = useState('')
  const [isPrivateContributor, setIsPrivateContributor] = useState(false)

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

  useEffect(() => {
    const fetchData = async () => {
      const result = await fetchHeatmapData(memberKey as string)
      if (!result) {
        setIsPrivateContributor(true)
        return
      }
      if (result?.contributions) {
        setUsername(memberKey as string)
        setData(result as HeatmapData)
      }
    }
    fetchData()
  }, [memberKey, user])

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

  const Heatmap = () => {
    const canvasRef = useRef<HTMLCanvasElement | null>(null)
    const [imgSrc, setImgSrc] = useState('')
    const { resolvedTheme } = useTheme()
    const isDarkMode = (resolvedTheme ?? 'light') === 'dark'

    useEffect(() => {
      if (canvasRef.current && data?.years?.length) {
        drawContributions(canvasRef.current, {
          data,
          username,
          themeName: isDarkMode ? 'dark' : 'light',
        })
        const imageURL = canvasRef.current.toDataURL()
        setImgSrc(imageURL)
      } else {
        setImgSrc('')
      }
    }, [isDarkMode])

    return (
      <div className="overflow-hidden rounded-lg bg-white dark:bg-gray-800">
        <div className="relative">
          <canvas ref={canvasRef} style={{ display: 'none' }} aria-hidden="true"></canvas>
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
            <div className="relative h-32 items-center justify-center">
              <Image
                height={100}
                width={100}
                src={
                  isDarkMode
                    ? '/img/heatmap-background-dark.png'
                    : '/img/heatmap-background-light.png'
                }
                className="heatmap-background-loader h-full w-full border-none object-cover object-[54%_60%]"
                alt="Heatmap Background"
              />
              <div className="heatmap-loader"></div>
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
        src={user?.avatarUrl || '/placeholder.svg'}
        alt={user?.name || user?.login || 'User Avatar'}
      />
      <div className="w-full text-center lg:text-left">
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
