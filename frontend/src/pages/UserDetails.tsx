import { useQuery } from '@apollo/client'
import { Link } from '@chakra-ui/react'
import {
  faCodeBranch,
  faUserPlus,
  faUser,
  faFileCode,
  faBookmark,
} from '@fortawesome/free-solid-svg-icons'
import { GET_USER_DATA } from 'api/queries/userQueries'
import React, { useState, useEffect, useRef, useMemo } from 'react'
import { useParams } from 'react-router-dom'
import type { ProjectIssuesType, ProjectReleaseType, RepositoryCardProps } from 'types/project'
import type { ItemCardPullRequests, PullRequestsType, UserDetailsProps } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import { fetchHeatmapData, drawContributions, type HeatmapData } from 'utils/helpers/githubHeatmap'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import MetadataManager from 'components/MetadataManager'
import { toaster } from 'components/ui/toaster'

const UserDetailsPage: React.FC = () => {
  const { userKey } = useParams()
  const [user, setUser] = useState<UserDetailsProps | null>()
  const [issues, setIssues] = useState<ProjectIssuesType[]>([])
  const [topRepositories, setTopRepositories] = useState<RepositoryCardProps[]>([])
  const [pullRequests, setPullRequests] = useState<PullRequestsType[]>([])
  const [releases, setReleases] = useState<ProjectReleaseType[]>([])
  const [data, setData] = useState<HeatmapData | null>(null)
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
      setIssues(graphQLData?.recentIssues)
      setPullRequests(graphQLData?.recentPullRequests)
      setReleases(graphQLData?.recentReleases)
      setTopRepositories(graphQLData?.topContributedRepositories)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      toaster.create({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        type: 'error',
      })
      setIsLoading(false)
    }
  }, [graphQLData, graphQLRequestError, userKey])

  useEffect(() => {
    const fetchData = async () => {
      const result = await fetchHeatmapData(userKey)
      if (result && result.contributions) {
        setUsername(userKey)
        setData(result)
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
    let mentionMatch = word.match(/^@([\w-]+(?:\.[\w-]+)*)([^\w@])?$/)
    if (mentionMatch && mentionMatch.length > 1) {
      let username = mentionMatch[1]
      let punctuation = mentionMatch[2] || ''
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
  }, [issues, user])

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
      releases?.map((release) => ({
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
        repositoryName: release.repositoryName,
        url: release.url,
      })) || []
    )
  }, [releases, user])

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
    {
      label: 'GitHub Profile',
      value: (
        <Link href={user.url || '#'} className="text-blue-400 hover:underline">
          @{user.login}
        </Link>
      ),
    },
    { label: 'Joined', value: formatDate(user.createdAt) },
    { label: 'Email', value: user.email || 'Not provided' },
    { label: 'Company', value: user.company || 'Not provided' },
    { label: 'Location', value: user.location || 'Not provided' },
  ]

  const userStats = [
    { icon: faUser, value: user.followersCount, unit: 'Follower' },
    { icon: faUserPlus, value: user.followingCount, unit: 'Following' },
    {
      icon: faCodeBranch,
      pluralizedName: 'Repositories',
      unit: 'Repository',
      value: user.publicRepositoriesCount,
    },
    { icon: faFileCode, value: user.issuesCount, unit: 'Issue' },
    { icon: faBookmark, value: user.releasesCount, unit: 'Release' },
  ]

  const Heatmap = () => (
    <div className="flex flex-col gap-4">
      <div className="overflow-hidden rounded-lg bg-white shadow-xl dark:bg-gray-800">
        <div className="relative">
          <canvas ref={canvasRef} style={{ display: 'none' }} aria-hidden="true"></canvas>
          {imageLink ? (
            <div className="h-40 bg-[#10151c]">
              <img
                src={imageLink || '/placeholder.svg'}
                className="h-full w-full object-cover object-[54%_60%]"
                alt="Contribution Heatmap"
              />
            </div>
          ) : (
            <div className="relative h-40 items-center justify-center bg-[#10151c]">
              <img
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
      <img
        className="mr-4 h-16 w-16 rounded-full border-2 border-white bg-white object-cover shadow-md dark:border-gray-800 dark:bg-gray-600/60"
        src={user.avatarUrl || '/placeholder.svg'}
        alt={user.name || user.login || 'User Avatar'}
      />
      <div>
        <Link href={user.url || '#'} className="text-xl font-bold text-blue-400 hover:underline">
          @{user.login}
        </Link>
        <p className="text-gray-600 dark:text-gray-400">{formattedBio}</p>
      </div>
    </div>
  )

  return (
    <MetadataManager
      pageTitle={user?.name || user?.login}
      description={user?.bio}
      url={user.url || '#'}
    >
      <DetailsCard
        showAvatar={false}
        title={user.name || user.login || 'User'}
        heatmap={privateContributor ? null : <Heatmap />}
        details={userDetails}
        pullRequests={formattedPullRequest}
        stats={userStats}
        type="user"
        recentIssues={formattedIssues}
        recentReleases={formattedReleases}
        repositories={topRepositories}
        userSummary={<UserSummary />}
      />
    </MetadataManager>
  )
}

export default UserDetailsPage
