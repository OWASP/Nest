'use client'
import { useQuery } from '@apollo/client/react'
import {
  faCodeMerge,
  faFolderOpen,
  faPersonWalkingArrowRight,
  faUserPlus,
} from '@fortawesome/free-solid-svg-icons'
import Image from 'next/image'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useTheme } from 'next-themes'
import React, { useState, useEffect, useRef } from 'react'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GetUserDataDocument } from 'types/__generated__/userQueries.generated'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { RepositoryCardProps } from 'types/project'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
import type { User } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import { drawContributions, fetchHeatmapData, HeatmapData } from 'utils/helpers/githubHeatmap'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const UserDetailsPage: React.FC = () => {
  const { memberKey } = useParams<{ memberKey: string }>()
  const [user, setUser] = useState<User | null>()
  const [issues, setIssues] = useState<Issue[]>([])
  const [topRepositories, setTopRepositories] = useState<RepositoryCardProps[]>([])
  const [milestones, setMilestones] = useState<Milestone[]>([])
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([])
  const [releases, setReleases] = useState<Release[]>([])
  const [data, setData] = useState<HeatmapData>({} as HeatmapData)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [username, setUsername] = useState('')
  const [isPrivateContributor, setIsPrivateContributor] = useState(false)

  const { data: graphQLData, error: graphQLRequestError } = useQuery(GetUserDataDocument, {
    variables: { key: memberKey },
  })

  useEffect(() => {
    if (graphQLData) {
      setUser(graphQLData.user)
      setIssues(graphQLData.recentIssues)
      setMilestones(graphQLData.recentMilestones)
      setPullRequests(graphQLData.recentPullRequests)
      setReleases(graphQLData.recentReleases)
      setTopRepositories(graphQLData.topContributedRepositories)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [graphQLData, graphQLRequestError, memberKey])

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
    // Regex to match GitHub usernames, but if last character is not a word character or @, it's a punctuation
    const mentionMatch = word.match(/^@([\w-]+(?:\.[\w-]+)*)([^\w@])?$/)
    if (mentionMatch && mentionMatch.length > 1) {
      const username = mentionMatch[1]
      const punctuation = mentionMatch[2] || ''
      return (
        <React.Fragment key={index}>
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
    return <span key={index}>{word} </span>
  })

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!isLoading && user == null) {
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
    { icon: faPersonWalkingArrowRight, value: user?.followersCount || 0, unit: 'Follower' },
    { icon: faUserPlus, value: user?.followingCount || 0, unit: 'Following' },
    {
      icon: faFolderOpen,
      pluralizedName: 'Repositories',
      unit: 'Repository',
      value: user?.publicRepositoriesCount ?? 0,
    },
    { icon: faCodeMerge, value: user?.contributionsCount || 0, unit: 'Contribution' },
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
    <div className="flex flex-col items-start lg:flex-row">
      <div className="mb-4 flex-shrink-0 self-center lg:mr-6 lg:mb-0 lg:self-start">
        <Image
          width={200}
          height={200}
          className="h-[200px] w-[200px] rounded-full border-2 border-white bg-white object-cover shadow-md dark:border-gray-800 dark:bg-gray-600/60"
          src={user?.avatarUrl || '/placeholder.svg'}
          alt={user?.name || user?.login || 'User Avatar'}
        />
      </div>
      <div className="flex w-full flex-1 flex-col">
        <div className="mb-0 text-center lg:mb-4 lg:ml-[26px] lg:text-left">
          <Link href={user?.url || '#'} className="text-xl font-bold text-blue-400 hover:underline">
            @{user?.login}
          </Link>
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
