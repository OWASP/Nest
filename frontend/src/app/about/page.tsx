'use client'
import { useQuery } from '@apollo/client/react'
import {
  faCircleCheck,
  faClock,
  faUserGear,
  faMapSigns,
  faScroll,
  faUsers,
  faTools,
  faPersonWalkingArrowRight,
  faBullseye,
  faUser,
  faUsersGear,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import upperFirst from 'lodash/upperFirst'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import {
  GetProjectMetadataDocument,
  GetTopContributorsDocument,
} from 'types/__generated__/projectQueries.generated'
import { GetLeaderDataDocument } from 'types/__generated__/userQueries.generated'
import type { Contributor } from 'types/contributor'
import type { Project } from 'types/project'
import type { User } from 'types/user'
import {
  technologies,
  missionContent,
  keyFeatures,
  getInvolvedContent,
  projectTimeline,
  projectStory,
} from 'utils/aboutData'
import AnchorTitle from 'components/AnchorTitle'
import AnimatedCounter from 'components/AnimatedCounter'
import LoadingSpinner from 'components/LoadingSpinner'
import Markdown from 'components/MarkdownWrapper'
import SecondaryCard from 'components/SecondaryCard'
import TopContributorsList from 'components/TopContributorsList'
import UserCard from 'components/UserCard'

const leaders = {
  arkid15r: 'CCSP, CISSP, CSSLP',
  kasya: 'CC',
  mamicidal: 'CISSP',
}
const projectKey = 'nest'

const About = () => {
  const { data: projectMetadataResponse, error: projectMetadataRequestError } = useQuery(
    GetProjectMetadataDocument,
    {
      variables: { key: projectKey },
    }
  )

  const { data: topContributorsResponse, error: topContributorsRequestError } = useQuery(
    GetTopContributorsDocument,
    {
      variables: {
        excludedUsernames: Object.keys(leaders),
        hasFullName: true,
        key: projectKey,
        limit: 24,
      },
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
        <h1 className="mt-4 mb-6 text-4xl font-bold">About</h1>
        <div className="grid gap-0 md:grid-cols-2 md:gap-6">
          <SecondaryCard icon={faBullseye} title={<AnchorTitle title="Our Mission" />}>
            <p className="text-gray-600 dark:text-gray-300">{missionContent.mission}</p>
          </SecondaryCard>

          <SecondaryCard icon={faUser} title={<AnchorTitle title="Who It's For" />}>
            <p className="text-gray-600 dark:text-gray-300">{missionContent.whoItsFor}</p>
          </SecondaryCard>
        </div>

        <SecondaryCard icon={faCircleCheck} title={<AnchorTitle title="Key Features" />}>
          <div className="grid gap-4 md:grid-cols-2">
            {keyFeatures.map((feature) => (
              <div key={feature.title} className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                <h3 className="mb-2 text-lg font-semibold text-blue-400">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
              </div>
            ))}
          </div>
        </SecondaryCard>

        <SecondaryCard icon={faPersonWalkingArrowRight} title={<AnchorTitle title="Leaders" />}>
          <div className="flex w-full flex-col items-center justify-around overflow-hidden md:flex-row">
            {Object.keys(leaders).map((username) => (
              <div key={username}>
                <LeaderData username={username} />
              </div>
            ))}
          </div>
        </SecondaryCard>

        {topContributors && (
          <TopContributorsList
            contributors={topContributors}
            icon={faUsers}
            maxInitialDisplay={12}
          />
        )}

        <SecondaryCard icon={faTools} title={<AnchorTitle title="Technologies & Tools" />}>
          <div className="w-full">
            <div className="grid w-full grid-cols-1 justify-center sm:grid-cols-2 lg:grid-cols-4 lg:pl-8">
              {technologies.map((tech) => (
                <div key={tech.section} className="mb-2">
                  <h3 className="mb-3 font-semibold text-blue-400">{tech.section}</h3>
                  <ul className="flex flex-col gap-3">
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
                          {upperFirst(name)}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </SecondaryCard>

        <SecondaryCard icon={faUsersGear} title={<AnchorTitle title="Get Involved" />}>
          <p className="mb-2 text-gray-600 dark:text-gray-300">{getInvolvedContent.description}</p>
          <ul className="mb-6 list-inside list-disc space-y-2 pl-4">
            {getInvolvedContent.ways.map((way) => (
              <li key={way} className="pb-1 text-gray-600 dark:text-gray-300">
                {way}
              </li>
            ))}
          </ul>
          <Markdown content={getInvolvedContent.callToAction} />
        </SecondaryCard>

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
                      <div className="relative">
                        <Link
                          href={milestone.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block"
                        >
                          <h3 className="mb-2 pr-8 text-xl font-semibold text-blue-400">
                            {milestone.title}
                          </h3>
                        </Link>
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
                          <span className="absolute top-0 right-0 text-xl text-gray-400">
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
                      </div>
                      <p className="text-gray-600 dark:text-gray-300">{milestone.body}</p>
                    </div>
                  </div>
                ))}
            </div>
          </SecondaryCard>
        )}
        <SecondaryCard icon={faScroll} title={<AnchorTitle title="Our Story" />}>
          {projectStory.map((text, index) => (
            <div key={`story-${index}`} className="mb-4">
              <div>
                <Markdown content={text} />
              </div>
            </div>
          ))}
        </SecondaryCard>
        <SecondaryCard icon={faClock} title={<AnchorTitle title="Project Timeline" />}>
          <div className="space-y-6">
            {[...projectTimeline].reverse().map((milestone, index) => (
              <div key={`${milestone.year}-${milestone.title}`} className="relative pl-10">
                {index !== projectTimeline.length - 1 && (
                  <div className="absolute top-5 left-[5px] h-full w-0.5 bg-gray-400"></div>
                )}
                <div
                  aria-hidden="true"
                  className="absolute top-[10px] left-0 h-3 w-3 rounded-full bg-gray-400"
                ></div>
                <div>
                  <h3 className="text-lg font-semibold text-blue-400">{milestone.title}</h3>
                  <h4 className="mb-1 font-medium text-gray-400">{milestone.year}</h4>
                  <p className="text-gray-600 dark:text-gray-300">{milestone.description}</p>
                </div>
              </div>
            ))}
          </div>
        </SecondaryCard>

        <div className="grid gap-0 md:grid-cols-4 md:gap-6">
          {[
            { label: 'Forks', value: projectMetadata.forksCount },
            { label: 'Stars', value: projectMetadata.starsCount },
            { label: 'Contributors', value: projectMetadata.contributorsCount },
            { label: 'Open Issues', value: projectMetadata.issuesCount },
          ].map((stat) => (
            <div key={stat.label}>
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
  const { data, loading, error } = useQuery(GetLeaderDataDocument, {
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
      description={leaders[user.login]}
      name={user.name || username}
    />
  )
}

export default About
