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
  const [topRepositories, setTopRepositories] = useState<RepositoryCardProps[]>(null)
  const [pullRequests, setPullRequests] = useState<PullRequestsType[]>([])
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
      setPullRequests(graphQLData?.pullRequests)
      setTopRepositories(graphQLData?.topRepositories)
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

  const formattedIssues: ProjectIssuesType[] = useMemo(() => {
    return (
      user?.issues?.map((issue) => ({
        commentsCount: issue.commentsCount,
        createdAt: issue.createdAt,
        number: issue.number,
        title: issue.title,
        author: {
          login: user.login,
          avatarUrl: user.avatarUrl,
          key: user.login,
          name: user.name || user.login,
        },
        repository: {
          key: issue.repository.key,
          owner_key: issue.repository.ownerKey,
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
          login: user.login,
          avatarUrl: user.avatarUrl,
          key: user.login,
          name: user.name || user.login,
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
          login: user.login,
          avatarUrl: user.avatarUrl,
          key: user.login,
          name: user.name || user.login,
        },
        repository: {
          key: release.repository.key,
          owner_key: release.repository.ownerKey,
        },
        url: release.url,
      })) || []
    )
  }, [user])

  if (isLoading)
    return (
      <div
        className="flex min-h-[60vh] items-center justify-center"
        aria-live="polite"
        aria-busy="true"
      >
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )

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
        <Link href={user.url} className="hover:underline dark:text-sky-600">
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
    {
      icon: faUser,
      value: `${user.followersCount.toLocaleString()} Followers`,
    },
    {
      icon: faUserPlus,
      value: `${user.followingCount.toLocaleString()} Following`,
    },
    {
      icon: faCodeBranch,
      value: `${user.publicRepositoriesCount.toLocaleString()} Repositories`,
    },
    {
      icon: faFileCode,
      value: `${user.issuesCount} Issues`,
    },
    {
      icon: faBookmark,
      value: `${user.releasesCount} Releases`,
    },
  ]

  const Heatmap = () => (
    <div className="flex flex-col gap-4">
      <div className="overflow-hidden rounded-lg bg-white shadow-xl dark:bg-gray-800">
        <div className="relative">
          <canvas ref={canvasRef} style={{ display: 'none' }} aria-hidden="true"></canvas>
          {privateContributor ? (
            <div className="h-40 rounded-lg bg-owasp-blue"></div>
          ) : imageLink ? (
            <div className="bg-#10151c h-40">
              <img
                src={imageLink || '/placeholder.svg'}
                className="h-full w-full object-cover object-[54%_60%]"
                alt="Contribution Heatmap"
              />
            </div>
          ) : (
            <div className="bg-#10151c relative h-40 items-center justify-center">
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
        alt={user.name || user.login}
      />
      <div>
        <Link href={user.url} className="text-xl font-bold hover:underline dark:text-sky-600">
          @{user.login}
        </Link>
        <p className="text-gray-600 dark:text-gray-400">{user.bio}</p>
      </div>
    </div>
  )

  return (
    <MetadataManager pageTitle={user?.name || user?.login} description={user?.bio} url={user.url}>
      <DetailsCard
        title={user.name || user.login}
        heatmap={<Heatmap />}
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
