'use client'
import { useQuery } from '@apollo/client'
import {
  faCodeMerge,
  faFolderOpen,
  faPersonWalkingArrowRight,
  faUserPlus,
} from '@fortawesome/free-solid-svg-icons'
import Image from 'next/image'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import React, { useState, useEffect, useRef, useMemo } from 'react'
import { GET_USER_DATA } from 'server/queries/userQueries'
import type {
  ProjectIssuesType,
  ProjectMilestonesType,
  ProjectReleaseType,
  RepositoryCardProps,
} from 'types/project'
import type { ItemCardPullRequests, PullRequestsType, UserDetailsProps } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import { drawContributions, fetchHeatmapData, HeatmapData } from 'utils/helpers/githubHeatmap'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import { handleAppError, ErrorDisplay } from 'app/global-error'

const UserDetailsPage: React.FC = () => {
  const { memberKey } = useParams()
  const [user, setUser] = useState<UserDetailsProps | null>()
  const [issues, setIssues] = useState<ProjectIssuesType[]>([])
  const [topRepositories, setTopRepositories] = useState<RepositoryCardProps[]>([])
  const [milestones, setMilestones] = useState<ProjectMilestonesType[]>([])
  const [pullRequests, setPullRequests] = useState<PullRequestsType[]>([])
  const [releases, setReleases] = useState<ProjectReleaseType[]>([])
  const [data, setData] = useState<HeatmapData>({} as HeatmapData)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [username, setUsername] = useState('')
  const [imageLink, setImageLink] = useState('')
  const [privateContributor, setPrivateContributor] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const theme = 'blue'

  const { data: graphQLData, error: graphQLRequestError } = useQuery(GET_USER_DATA, {
    variables: { key: memberKey },
  })

  useEffect(() => {
    if (graphQLData) {
      setUser(graphQLData?.user)
      setIssues(graphQLData?.recentIssues)
      setMilestones(graphQLData?.recentMilestones)
      setPullRequests(graphQLData?.recentPullRequests)
      setReleases(graphQLData?.recentReleases)
      setTopRepositories(graphQLData?.topContributedRepositories)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [graphQLData, graphQLRequestError, memberKey])

  useEffect(() => {
    const fetchData = async () => {
      if (!memberKey) {
        return
      }
      const result = await fetchHeatmapData(memberKey as string)
      if (typeof result !== 'string' && result.contributions) {
        setUsername(memberKey as string)
        setData(result as HeatmapData)
      } else {
        setPrivateContributor(true)
      }
    }
    fetchData()
  }, [memberKey, user])

  useEffect(() => {
    if (canvasRef.current && data && data.years && data.years.length > 0) {
      drawContributions(canvasRef.current, { data, username, theme })
      const imageURL = canvasRef.current.toDataURL()
      setImageLink(imageURL)
    }
  }, [username, data])

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

  const formattedIssues: ProjectIssuesType[] = useMemo(() => {
    return (
      issues?.map((issue) => ({
        author: {
          avatarUrl: user?.avatarUrl || '',
          key: user?.login || '',
          login: user?.login || '',
          name: user?.name || user?.login || '',
        },
        createdAt: issue.createdAt,
        organizationName: issue.organizationName,
        repositoryName: issue.repositoryName,
        title: issue.title,
        url: issue.url,
      })) || []
    )
  }, [user, issues])

  const formattedPullRequest: ItemCardPullRequests[] = useMemo(() => {
    return (
      pullRequests?.map((pullRequest) => ({
        author: {
          avatarUrl: user?.avatarUrl || '',
          key: user?.login || '',
          login: user?.login || '',
          name: user?.name || user?.login || '',
        },
        createdAt: pullRequest.createdAt,
        organizationName: pullRequest.organizationName,
        repositoryName: pullRequest.repositoryName,
        title: pullRequest.title,
        url: pullRequest.url,
      })) || []
    )
  }, [pullRequests, user])

  const formattedReleases: ProjectReleaseType[] = useMemo(() => {
    return (
      releases?.map((release) => ({
        author: {
          avatarUrl: user?.avatarUrl || '',
          key: user?.login || '',
          login: user?.login || '',
          name: user?.name || user?.login || '',
        },
        isPreRelease: release.isPreRelease,
        name: release.name,
        organizationName: release.organizationName,
        publishedAt: release.publishedAt,
        repositoryName: release.repositoryName,
        tagName: release.tagName,
        url: release.url,
      })) || []
    )
  }, [releases, user])

  const formattedMilestones: ProjectMilestonesType[] = useMemo(() => {
    return (
      milestones?.map((milestone) => ({
        author: {
          avatarUrl: user?.avatarUrl || '',
          key: user?.login || '',
          login: user?.login || '',
          name: user?.name || user?.login || '',
        },
        createdAt: milestone.createdAt,
        openIssuesCount: milestone.openIssuesCount,
        closedIssuesCount: milestone.closedIssuesCount,
        organizationName: milestone.organizationName,
        repositoryName: milestone.repositoryName,
        title: milestone.title,
        url: milestone.url,
      })) || []
    )
  }, [milestones, user])

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

  const Heatmap = () => (
    <div className="flex flex-col gap-4">
      <div className="overflow-hidden rounded-lg bg-white shadow-xl dark:bg-gray-800">
        <div className="relative">
          <canvas ref={canvasRef} style={{ display: 'none' }} aria-hidden="true"></canvas>
          {imageLink ? (
            <div className="h-40 bg-[#10151c]">
              <Image
                width={100}
                height={100}
                src={imageLink || '/placeholder.svg'}
                className="h-full w-full object-cover object-[54%_60%]"
                alt="Contribution Heatmap"
              />
            </div>
          ) : (
            <div className="relative h-40 items-center justify-center bg-[#10151c]">
              <Image
                height={100}
                width={100}
                src="/img/heatmapBackground.png"
                className="heatmap-background-loader h-full w-full border-none object-cover object-[54%_60%]"
                alt="Heatmap Background"
              />
              <div className="heatmap-loader"></div>
            </div>
          )}
        </div>
      </div>
    </div>
  )

  const UserSummary = () => (
    <div className="mt-4 flex items-center">
      <Image
        width={64}
        height={64}
        className="mr-4 h-16 w-16 rounded-full border-2 border-white bg-white object-cover shadow-md dark:border-gray-800 dark:bg-gray-600/60"
        src={user?.avatarUrl || '/placeholder.svg'}
        alt={user?.name || user?.login || 'User Avatar'}
      />
      <div>
        <Link href={user?.url || '#'} className="text-xl font-bold text-blue-400 hover:underline">
          @{user?.login}
        </Link>
        <p className="text-gray-600 dark:text-gray-400">{formattedBio}</p>
      </div>
    </div>
  )

  return (
    <DetailsCard
      showAvatar={false}
      title={user?.name || user?.login || 'User'}
      heatmap={privateContributor ? undefined : <Heatmap />}
      details={userDetails}
      recentMilestones={formattedMilestones}
      pullRequests={formattedPullRequest}
      stats={userStats}
      type="user"
      recentIssues={formattedIssues}
      recentReleases={formattedReleases}
      repositories={topRepositories}
      userSummary={<UserSummary />}
    />
  )
}

export default UserDetailsPage
