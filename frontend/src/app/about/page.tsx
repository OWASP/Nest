'use client'
import { useQuery } from '@apollo/client'
import {
  faCircleCheck,
  faClock,
  faUserGear,
  faMapSigns,
  faUsers,
  faTools,
  faArrowUpRightFromSquare,
  faBullseye,
  faUserGroup,
  faRocket,
  faHandsHelping,
  faTimeline,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GET_PROJECT_METADATA, GET_TOP_CONTRIBUTORS } from 'server/queries/projectQueries'
import { GET_LEADER_DATA } from 'server/queries/userQueries'
import type { Contributor } from 'types/contributor'
import type { Project } from 'types/project'
import type { User } from 'types/user'
import {
  technologies,
  leaders,
  missionContent,
  keyFeatures,
  getInvolvedContent,
  projectHistory,
} from 'utils/aboutData'
import AnchorTitle from 'components/AnchorTitle'
import AnimatedCounter from 'components/AnimatedCounter'
import LoadingSpinner from 'components/LoadingSpinner'
import Markdown from 'components/MarkdownWrapper'
import SecondaryCard from 'components/SecondaryCard'
import TopContributorsList from 'components/TopContributorsList'
import UserCard from 'components/UserCard'

const projectKey = 'nest'

const About = () => {
  const { data: projectMetadataResponse, error: projectMetadataRequestError } = useQuery(
    GET_PROJECT_METADATA,
    {
      variables: { key: projectKey },
    }
  )

  const { data: topContributorsResponse, error: topContributorsRequestError } = useQuery(
    GET_TOP_CONTRIBUTORS,
    {
      variables: { excludedUsernames: Object.keys(leaders), key: projectKey },
    }
  )

  const [projectMetadata, setProjectMetadata] = useState<Project | null>(null)
  const [topContributors, setTopContributors] = useState<Contributor[]>([])

  useEffect(() => {
    if (projectMetadataResponse?.project) {
      setProjectMetadata(projectMetadataResponse.project)
    }

    if (projectMetadataRequestError) {
      handleAppError(projectMetadataRequestError)
    }
  }, [projectMetadataResponse, projectMetadataRequestError])

  useEffect(() => {
    if (topContributorsResponse?.topContributors) {
      setTopContributors(topContributorsResponse.topContributors)
    }

    if (topContributorsRequestError) {
      handleAppError(topContributorsRequestError)
    }
  }, [topContributorsResponse, topContributorsRequestError])

  const isLoading =
    !projectMetadataResponse ||
    !topContributorsResponse ||
    (projectMetadataRequestError && !projectMetadata) ||
    (topContributorsRequestError && !topContributors)

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!projectMetadata || !topContributors) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Data not found"
        message="Sorry, the page you're looking for doesn't exist"
      />
    )
  }

  return (
    <div className="min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 mt-4 text-4xl font-bold">About</h1>

        <div className="mb-8 grid gap-6 md:grid-cols-2">
          <SecondaryCard icon={faBullseye} title={<AnchorTitle title="Mission" />}>
            <p className="text-gray-600 dark:text-gray-300">{missionContent.mission}</p>
          </SecondaryCard>

          <SecondaryCard icon={faUserGroup} title={<AnchorTitle title="Who It's For" />}>
            <p className="text-gray-600 dark:text-gray-300">{missionContent.whoItsFor}</p>
          </SecondaryCard>
        </div>

        <SecondaryCard icon={faRocket} title={<AnchorTitle title="Key Features" />}>
          <div className="grid gap-4 sm:grid-cols-2">
            {keyFeatures.map((feature) => (
              <div
                key={`${feature.title}-${feature.description.slice(0, 10)}`}
                className="rounded-lg bg-gray-100 p-4 dark:bg-gray-700"
              >
                <h3 className="mb-2 font-semibold text-blue-400">{feature.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-300">{feature.description}</p>
              </div>
            ))}
          </div>
        </SecondaryCard>

        {/* Leaders */}
        <SecondaryCard icon={faArrowUpRightFromSquare} title={<AnchorTitle title="Leaders" />}>
          <div className="flex w-full flex-col items-center justify-around overflow-hidden md:flex-row">
            {Object.keys(leaders).map((username) => (
              <div key={username}>
                <LeaderData username={username} />
              </div>
            ))}
          </div>
        </SecondaryCard>

        {/* Top Contributors */}
        {topContributors && (
          <TopContributorsList
            icon={faUsers}
            contributors={topContributors}
            maxInitialDisplay={9}
            type="contributor"
          />
        )}

        {/* Technologies & Tools */}
        <SecondaryCard icon={faTools} title={<AnchorTitle title="Technologies & Tools" />}>
          <div className="w-full">
            <div className="grid w-full grid-cols-1 justify-center sm:grid-cols-2 lg:grid-cols-4 lg:pl-8">
              {technologies.map((tech) => (
                <div key={tech.section} className="mb-2">
                  <h3 className="mb-3 font-semibold text-blue-400">{tech.section}</h3>
                  <ul className="space-y-3">
                    {Object.entries(tech.tools).map(([name, details]) => (
                      <li key={name} className="flex flex-row items-center gap-2">
                        <Image
                          alt={`${name} icon`}
                          className="inline-block align-middle grayscale"
                          height={24}
                          src={details.icon}
                          width={24}
                        />
                        <Link
                          href={details.url}
                          className="text-gray-600 hover:underline dark:text-gray-300"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </SecondaryCard>

        {/* Roadmap */}
        {projectMetadata.recentMilestones.length > 0 && (
          <SecondaryCard icon={faMapSigns} title={<AnchorTitle title="Roadmap" />}>
            <div className="grid gap-4">
              {[...projectMetadata.recentMilestones]
                .filter((milestone) => milestone.state !== 'closed')
                .sort((a, b) => (a.title > b.title ? 1 : -1))
                .map((milestone, index) => (
                  <div
                    key={milestone.url || milestone.title || index}
                    className="flex items-center gap-4 overflow-hidden rounded-lg bg-gray-200 p-6 dark:bg-gray-700"
                  >
                    <div className="flex-1">
                      <Link
                        href={milestone.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block"
                      >
                        <h3 className="mb-2 text-xl font-semibold text-blue-400">
                          {milestone.title}
                          <Tooltip
                            closeDelay={100}
                            content={
                              milestone.progress === 100
                                ? 'Completed'
                                : milestone.progress > 0
                                  ? 'In Progress'
                                  : 'Not Started'
                            }
                            id={`tooltip-state-${index}`}
                            delay={100}
                            placement="top"
                            showArrow
                          >
                            <span className="ml-4 inline-block text-gray-400">
                              <FontAwesomeIcon
                                icon={
                                  milestone.progress === 100
                                    ? faCircleCheck
                                    : milestone.progress > 0
                                      ? faUserGear
                                      : faClock
                                }
                              />
                            </span>
                          </Tooltip>
                        </h3>
                      </Link>
                      <p className="text-gray-600 dark:text-gray-300">{milestone.body}</p>
                    </div>
                  </div>
                ))}
            </div>
          </SecondaryCard>
        )}

        {/* Get Involved */}
        <SecondaryCard icon={faHandshake} title={<AnchorTitle title="Get Involved" />}>
          <div className="space-y-4">
            <p className="text-gray-600 dark:text-gray-300">{getInvolvedContent.description}</p>
            <ul className="space-y-2">
              {getInvolvedContent.ways.map((way) => (
                <li key={way.slice(0, 32)} className="flex items-start gap-2">
                  <span className="mt-1 text-blue-400">•</span>
                  <span className="text-gray-600 dark:text-gray-300">{way}</span>
                </li>
              ))}
            </ul>
            <div className="mt-4 rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
              <Markdown content={getInvolvedContent.callToAction} />
            </div>
          </div>
        </SecondaryCard>

        <SecondaryCard icon={faHistory} title={<AnchorTitle title="Project History" />}>
          <div className="relative" data-testid="project-history-section">
            <div className="absolute bottom-0 left-4 top-8 w-0.5 bg-gradient-to-b from-blue-400 to-gray-300 dark:to-gray-600"></div>

            <div className="space-y-8">
              {projectHistory.map((milestone) => (
                <div key={`${milestone.year}-${milestone.title}`} className="relative flex gap-6">
                  <div className="relative z-10 flex flex-col items-center">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-400 text-xs font-bold text-white shadow-lg ring-4 ring-white dark:ring-gray-800">
                      {milestone.year.slice(-2)}
                    </div>
                  </div>
                  <div className="flex-1 pb-2">
                    <div className="rounded-lg bg-gray-50 p-4 dark:bg-gray-700/50">
                      <h3 className="mb-2 font-semibold text-blue-400">{milestone.title}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-300">
                        {milestone.description}
                      </p>
                      <span className="mt-2 inline-block text-xs font-medium text-gray-500 dark:text-gray-400">
                        {milestone.year}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </SecondaryCard>

        <div className="grid gap-6 md:grid-cols-4">
          {[
            { label: 'Forks', value: projectMetadata.forksCount },
            { label: 'Stars', value: projectMetadata.starsCount },
            { label: 'Contributors', value: projectMetadata.contributorsCount },
            { label: 'Open Issues', value: projectMetadata.issuesCount },
          ].map((stat, index) => (
            <div key={index}>
              <SecondaryCard className="text-center">
                <div className="mb-2 text-3xl font-bold text-blue-400">
                  <AnimatedCounter end={Math.floor(stat.value / 10) * 10} duration={2} />+
                </div>
                <div className="text-gray-600 dark:text-gray-300">{stat.label}</div>
              </SecondaryCard>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

const LeaderData = ({ username }: { username: string }) => {
  const { data, loading, error } = useQuery(GET_LEADER_DATA, {
    variables: { key: username },
  })
  const router = useRouter()

  if (loading) return <p>Loading {username}...</p>
  if (error) return <p>Error loading {username}'s data</p>

  const user = data?.user

  if (!user) {
    return <p>No data available for {username}</p>
  }

  const handleButtonClick = (user: User) => {
    router.push(`/members/${user.login}`)
  }

  return (
    <UserCard
      avatar={user.avatarUrl}
      button={{
        icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
        label: 'View Profile',
        onclick: () => handleButtonClick(user),
      }}
      className="h-64 w-40 bg-inherit"
      company={user.company}
      description={leaders[user.login]}
      location={user.location}
      name={user.name || username}
    />
  )
}

export default About
