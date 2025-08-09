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
import React, { useState, useEffect, useRef } from 'react'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GET_USER_DATA } from 'server/queries/userQueries'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { RepositoryCardProps } from 'types/project'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
import type { UserDetails } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import { drawContributions, fetchHeatmapData, HeatmapData } from 'utils/helpers/githubHeatmap'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import PageLayout from 'components/PageLayout'

const UserDetailsPage: React.FC = () => {
  const { memberKey } = useParams()
  const [user, setUser] = useState<UserDetails | null>()
  const [issues, setIssues] = useState<Issue[]>([])
  const [topRepositories, setTopRepositories] = useState<RepositoryCardProps[]>([])
  const [milestones, setMilestones] = useState<Milestone[]>([])
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([])
  const [releases, setReleases] = useState<Release[]>([])
  const [data, setData] = useState<HeatmapData>({} as HeatmapData)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [username, setUsername] = useState('')
  const [imageLink, setImageLink] = useState('')
  const [isPrivateContributor, setIsPrivateContributor] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const theme = 'blue'

  const { data: graphQLData, error: graphQLRequestError } = useQuery(GET_USER_DATA, {
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
      <div className="w-full">
        <Link href={user?.url || '#'} className="text-xl font-bold text-blue-400 hover:underline">
          @{user?.login}
        </Link>
        <p className="text-gray-600 dark:text-gray-400">{formattedBio}</p>
      </div>
    </div>
  )

  return (
    <PageLayout breadcrumbItems={{ title: user?.name || user?.login }}>
      <DetailsCard
        details={userDetails}
        heatmap={isPrivateContributor ? undefined : <Heatmap />}
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
    </PageLayout>
  )
}

export default UserDetailsPage
