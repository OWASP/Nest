'use client'
import { useQuery } from '@apollo/client'
import {
  faCodeBranch,
  faUserPlus,
  faUser,
  faFileCode,
  faBookmark,
} from '@fortawesome/free-solid-svg-icons'
import { addToast } from '@heroui/toast'
import Image from 'next/image'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import React, { useState, useEffect, useRef, useMemo } from 'react'
import { GET_USER_DATA } from 'server/queries/userQueries'
import type { ProjectIssuesType, ProjectReleaseType, RepositoryCardProps } from 'types/project'
import type { ItemCardPullRequests, PullRequestsType, UserDetailsProps } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import { drawContributions, fetchHeatmapData, HeatmapData } from 'utils/helpers/githubHeatmap'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const UserDetailsPage: React.FC = () => {
  const { userKey } = useParams()
  const [user, setUser] = useState<UserDetailsProps | null>()
  const [topRepositories, setTopRepositories] = useState<RepositoryCardProps[]>([])
  const [pullRequests, setPullRequests] = useState<PullRequestsType[]>([])
  const [data, setData] = useState<HeatmapData>({} as HeatmapData)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [username, setUsername] = useState('')
  const [imageLink, setImageLink] = useState('')
  const [privateContributor, setPrivateContributor] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const theme = 'blue'

  const { data: graphQLData, error: graphQLRequestError } = useQuery(GET_USER_DATA, {
    variables: { key: userKey },
  })

  useEffect(() => {
    if (graphQLData) {
      setUser(graphQLData?.user)
      setPullRequests(graphQLData?.recentPullRequests)
      setTopRepositories(graphQLData?.topContributedRepositories)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      addToast({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
      setIsLoading(false)
    }
  }, [graphQLData, graphQLRequestError, userKey])

  useEffect(() => {
    const fetchData = async () => {
      if (!userKey) {
        return
      }
      const result = await fetchHeatmapData(userKey as string)
      if (typeof result !== 'string' && result.contributions) {
        setUsername(userKey as string)
        setData(result as HeatmapData)
      } else {
        setPrivateContributor(true)
      }
    }
    fetchData()
  }, [userKey, user])

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
      user?.issues?.map((issue) => ({
        commentsCount: issue.commentsCount,
        createdAt: issue.createdAt,
        title: issue.title,
        author: {
          login: user?.login || '',
          avatarUrl: user?.avatarUrl || '',
          key: user?.login || '',
          name: user?.name || user?.login || '',
        },
        url: issue.url,
      })) || []
    )
  }, [user])

  const formattedPullRequest: ItemCardPullRequests[] = useMemo(() => {
    return (
      pullRequests?.map((pullRequest) => ({
        createdAt: pullRequest.createdAt,
        title: pullRequest.title,
        author: {
          login: user?.login || '',
          avatarUrl: user?.avatarUrl || '',
          key: user?.login || '',
          name: user?.name || user?.login || '',
        },
        url: pullRequest.url,
      })) || []
    )
  }, [pullRequests, user])

  const formattedReleases: ProjectReleaseType[] = useMemo(() => {
    return (
      user?.releases?.map((release) => ({
        isPreRelease: release.isPreRelease,
        name: release.name,
        publishedAt: release.publishedAt,
        tagName: release.tagName,
        author: {
          login: user?.login || '',
          avatarUrl: user?.avatarUrl || '',
          key: user?.login || '',
          name: user?.name || user?.login || '',
        },
        url: release.url,
      })) || []
    )
  }, [user])

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
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
    {
      label: 'GitHub Profile',
      value: (
        <Link href={user?.url || '#'} className="text-blue-400 hover:underline">
          @{user?.login}
        </Link>
      ),
    },
    { label: 'Joined', value: user?.createdAt ? formatDate(user.createdAt) : 'Not available' },
    { label: 'Email', value: user?.email || 'Not provided' },
    { label: 'Company', value: user?.company || 'Not provided' },
    { label: 'Location', value: user?.location || 'Not provided' },
  ]

  const userStats = [
    { icon: faUser, value: user?.followersCount || 0, unit: 'Follower' },
    { icon: faUserPlus, value: user?.followingCount || 0, unit: 'Following' },
    {
      icon: faCodeBranch,
      pluralizedName: 'Repositories',
      unit: 'Repository',
      value: user?.publicRepositoriesCount ?? 0,
    },
    { icon: faFileCode, value: user?.issuesCount || 0, unit: 'Issue' },
    { icon: faBookmark, value: user?.releasesCount || 0, unit: 'Release' },
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