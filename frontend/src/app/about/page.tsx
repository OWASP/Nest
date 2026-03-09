'use client'

import { useQuery } from '@apollo/client/react'
import { Tooltip } from '@heroui/tooltip'
import upperFirst from 'lodash/upperFirst'
import millify from 'millify'
import Image from 'next/image'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { FaMapSigns, FaTools } from 'react-icons/fa'
import { FaCircleCheck, FaClock, FaScroll, FaBullseye, FaUser, FaUsersGear } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { IconWrapper } from 'wrappers/IconWrapper'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetAboutPageDataDocument } from 'types/__generated__/aboutQueries.generated'
import type { Leader } from 'types/leader'
import {
  technologies,
  missionContent,
  keyFeatures,
  getInvolvedContent,
  projectTimeline,
  projectStory,
} from 'utils/aboutData'
import { getMemberUrl } from 'utils/urlFormatter'
import AnchorTitle from 'components/AnchorTitle'
import ContributorsList from 'components/ContributorsList'
import Leaders from 'components/Leaders'
import Markdown from 'components/MarkdownWrapper'
import SecondaryCard from 'components/SecondaryCard'
import ShowMoreButton from 'components/ShowMoreButton'
import AboutSkeleton from 'components/skeletons/AboutSkeleton'

const leaders = {
  arkid15r: 'CCSP, CISSP, CSSLP',
  kasya: 'CC',
  mamicidal: 'CISSP',
}

const MILESTONE_LIMIT = 3

const projectKey = 'nest'

const getMilestoneStatus = (progress: number): string => {
  if (progress === 100) {
    return 'Completed'
  }
  if (progress > 0) {
    return 'In Progress'
  }
  return 'Not Started'
}

const getMilestoneIcon = (progress: number) => {
  if (progress === 100) {
    return FaCircleCheck
  }
  if (progress > 0) {
    return FaUsersGear
  }
  return FaClock
}

const About = () => {
  const { data, loading, error } = useQuery(GetAboutPageDataDocument, {
    variables: {
      projectKey,
      excludedUsernames: Object.keys(leaders),
      hasFullName: true,
      limit: 24,
      leader1: 'arkid15r',
      leader2: 'kasya',
      leader3: 'mamicidal',
    },
  })

  // Derive data directly from response to prevent race conditions.
  const projectMetadata = data?.project
  const topContributors = data?.topContributors

  const leadersData = [data?.leader1, data?.leader2, data?.leader3]
    .filter(Boolean)
    .map((user) => ({
      description: user?.login ? leaders[user.login as keyof typeof leaders] : '',
      memberName: user?.name || user?.login,
      member: user,
    }))
    .filter((leader) => leader.memberName) as Leader[]

  const [showAllRoadmap, setShowAllRoadmap] = useState(false)

  type ProjectTimelineItem = (typeof projectTimeline)[number]
  type TimelineGroup = { calYear: string; milestones: ProjectTimelineItem[] }

  const extractCalYear = (yearStr: string): string => yearStr.split(' ').pop() ?? yearStr

  const timelineGroups: TimelineGroup[] = (() => {
    const map = new Map<string, ProjectTimelineItem[]>()
    for (const milestone of projectTimeline) {
      const cy = extractCalYear(milestone.year)
      if (!map.has(cy)) map.set(cy, [])
      map.get(cy)!.push(milestone)
    }
    return [...map.entries()]
      .sort(([a], [b]) => Number(b) - Number(a))
      .map(([calYear, milestones]) => ({ calYear, milestones: [...milestones].reverse() }))
  })()

  const defaultExpandedYears = (() => {
    if (timelineGroups.length === 0) return new Set<string>()
    const mostRecent = timelineGroups[0]
    if (mostRecent.milestones.length < 3 && timelineGroups.length > 1) {
      return new Set([mostRecent.calYear, timelineGroups[1].calYear])
    }
    return new Set([mostRecent.calYear])
  })()

  const TIMELINE_DEFAULT_LIMIT = 5

  const [expandedYears, setExpandedYears] = useState<Set<string>>(defaultExpandedYears)
  const [expandedYearMilestones, setExpandedYearMilestones] = useState<Set<string>>(new Set())

  const toggleYear = (calYear: string): void => {
    setExpandedYears((prev: Set<string>) => {
      if (prev.has(calYear)) {
        const next = new Set(prev)
        next.delete(calYear)
        return next
      }
      return new Set([calYear])
    })
    setExpandedYearMilestones(new Set())
  }

  const toggleYearMilestones = (calYear: string): void => {
    setExpandedYears(new Set([calYear]))
    setExpandedYearMilestones((prev: Set<string>) => {
      const next = new Set<string>()
      if (!prev.has(calYear)) next.add(calYear)
      return next
    })
  }

  type VisibleMilestone = ProjectTimelineItem & {
    calYear: string
    isFirst: boolean
    isLast: boolean
    globalIndex: number
  }

  type VisibleGroup = {
    calYear: string
    items: VisibleMilestone[]
    hasMore: boolean
    totalCount: number
  }

  const visibleGroups: VisibleGroup[] = (() => {
    let globalIndex = 0
    let budget = TIMELINE_DEFAULT_LIMIT
    const slices = new Map<string, { shown: ProjectTimelineItem[]; hasMore: boolean }>()
    for (const group of timelineGroups) {
      if (!expandedYears.has(group.calYear)) continue
      if (expandedYearMilestones.has(group.calYear)) {
        slices.set(group.calYear, { shown: group.milestones, hasMore: false })
      } else if (budget > 0) {
        const shown = group.milestones.slice(0, budget)
        slices.set(group.calYear, { shown, hasMore: group.milestones.length > shown.length })
        budget -= shown.length
      } else {
        slices.set(group.calYear, { shown: [], hasMore: group.milestones.length > 0 })
      }
    }

    const flatVisible: (ProjectTimelineItem & { calYear: string })[] = []
    for (const group of timelineGroups) {
      if (!expandedYears.has(group.calYear)) continue
      const s = slices.get(group.calYear)
      if (!s) continue
      for (const m of s.shown) flatVisible.push({ ...m, calYear: group.calYear })
    }

    const totalVisible = flatVisible.length
    const result: VisibleGroup[] = []
    let i = 0

    for (const group of timelineGroups) {
      if (!expandedYears.has(group.calYear)) continue
      const s = slices.get(group.calYear)
      if (!s) continue
      const { shown, hasMore } = s
      const items: VisibleMilestone[] = shown.map((m, localIdx) => {
        const gi = globalIndex++
        const isAbsoluteLast = i + localIdx === totalVisible - 1
        return {
          ...m,
          calYear: group.calYear,
          globalIndex: gi,
          isFirst: i + localIdx === 0,
          isLast: isAbsoluteLast && !hasMore,
        }
      })
      i += shown.length
      result.push({ calYear: group.calYear, items, hasMore, totalCount: group.milestones.length })
    }

    return result
  })()

  useEffect(() => {
    if (error) {
      handleAppError(error)
    }
  }, [error])

  const isLoading = loading

  if (isLoading) {
    return <AboutSkeleton />
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
          <SecondaryCard icon={FaBullseye} title={<AnchorTitle title="Our Mission" />}>
            <p className="text-gray-600 dark:text-gray-300">{missionContent.mission}</p>
          </SecondaryCard>

          <SecondaryCard icon={FaUser} title={<AnchorTitle title="Who It's For" />}>
            <p className="text-gray-600 dark:text-gray-300">{missionContent.whoItsFor}</p>
          </SecondaryCard>
        </div>

        <SecondaryCard icon={FaCircleCheck} title={<AnchorTitle title="Key Features" />}>
          <div className="grid gap-4 md:grid-cols-2">
            {keyFeatures.map((feature) => (
              <div key={feature.title} className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                <h3 className="mb-2 text-lg font-semibold text-blue-400">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
              </div>
            ))}
          </div>
        </SecondaryCard>

        <Leaders users={leadersData} />

        {topContributors && (
          <ContributorsList
            contributors={topContributors}
            icon={HiUserGroup}
            title="Wall of Fame"
            maxInitialDisplay={12}
            getUrl={getMemberUrl}
          />
        )}

        <SecondaryCard icon={FaTools} title={<AnchorTitle title="Technologies & Tools" />}>
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

        <SecondaryCard icon={FaUsersGear} title={<AnchorTitle title="Get Involved" />}>
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
          <SecondaryCard icon={FaMapSigns} title={<AnchorTitle title="Roadmap" />}>
            {(() => {
              const filteredMilestones = [...projectMetadata.recentMilestones]
                .filter((milestone) => milestone.state !== 'closed')
                .sort((a, b) => (a.title > b.title ? 1 : -1))
              return (
                <>
                  <div className="grid gap-4">
                    {filteredMilestones
                      .slice(0, showAllRoadmap ? filteredMilestones.length : MILESTONE_LIMIT)
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
                                content={getMilestoneStatus(milestone.progress)}
                                id={`tooltip-state-${index}`}
                                delay={100}
                                placement="top"
                                showArrow
                              >
                                <span className="absolute top-0 right-0 text-xl text-gray-400">
                                  <IconWrapper icon={getMilestoneIcon(milestone.progress)} />
                                </span>
                              </Tooltip>
                            </div>
                            <p className="text-gray-600 dark:text-gray-300">{milestone.body}</p>
                          </div>
                        </div>
                      ))}
                  </div>
                  {filteredMilestones.length > MILESTONE_LIMIT && (
                    <ShowMoreButton onToggle={() => setShowAllRoadmap(!showAllRoadmap)} />
                  )}
                </>
              )
            })()}
          </SecondaryCard>
        )}
        <SecondaryCard icon={FaScroll} title={<AnchorTitle title="Our Story" />}>
          {projectStory.map((text) => (
            <div key={`story-${text.substring(0, 50).replaceAll(' ', '-')}`} className="mb-4">
              <div>
                <Markdown content={text} />
              </div>
            </div>
          ))}
        </SecondaryCard>
        <SecondaryCard icon={FaClock} title={<AnchorTitle title="Project Timeline" />}>
          <div className="space-y-0">
            {(() => {
              const visibleGroupMap = new Map(visibleGroups.map((g) => [g.calYear, g]))
              return timelineGroups.map((group) => {
                const isExpanded = expandedYears.has(group.calYear)
                const visibleGroup = visibleGroupMap.get(group.calYear)
                return (
                  <div key={group.calYear}>
                    <button
                      type="button"
                      onClick={() => toggleYear(group.calYear)}
                      aria-expanded={isExpanded}
                      aria-controls={`timeline-group-${group.calYear}`}
                      className="group flex w-full items-center gap-4 py-6 transition-opacity hover:opacity-75"
                    >
                      <span className="hidden h-px flex-1 bg-gray-200 dark:bg-gray-700 md:block" />
                      <span className="flex items-center gap-1.5 rounded-full bg-blue-400 pl-4 pr-3 py-1.5 text-sm font-bold text-white shadow-md">
                        {group.calYear}
                        <span className={`text-xs transition-transform duration-200 ${isExpanded ? 'rotate-90' : 'rotate-0'}`}>›</span>
                      </span>
                      <span className="hidden h-px flex-1 bg-gray-200 dark:bg-gray-700 md:block" />
                    </button>

                    {isExpanded && visibleGroup && (
                      <div className="mx-auto hidden h-6 w-0.5 bg-gray-200 dark:bg-gray-700 md:block" />
                    )}

                    {isExpanded && visibleGroup && (
                      <div id={`timeline-group-${group.calYear}`} className="space-y-0">
                        {visibleGroup.items.map((milestone) => {
                          const isLeft = milestone.globalIndex % 2 === 0
                          const isLast = milestone.isLast
                          return (
                            <div key={milestone.globalIndex} className="relative flex flex-col md:flex-row md:items-center">
                              <div className="absolute top-0 left-1/2 hidden h-1/2 w-0.5 -translate-x-1/2 bg-gray-200 dark:bg-gray-700 md:block" />
                              {!isLast && (
                                <div className="absolute top-1/2 left-1/2 hidden h-1/2 w-0.5 -translate-x-1/2 bg-gray-200 dark:bg-gray-700 md:block" />
                              )}

                              <div className={`w-full py-3 md:w-1/2 ${isLeft ? 'md:pr-10' : 'md:invisible md:py-3'}`}>
                                {isLeft && (
                                  <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800/80">
                                    <span className="mb-2 inline-block rounded-md bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-500 dark:bg-blue-400/10 dark:text-blue-400">
                                      {milestone.year}
                                    </span>
                                    <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">{milestone.title}</h3>
                                    <p className="mt-1 text-sm leading-relaxed text-gray-500 dark:text-gray-400">{milestone.description}</p>
                                  </div>
                                )}
                              </div>

                              <div className="absolute left-1/2 hidden -translate-x-1/2 md:flex md:items-center md:justify-center">
                                <div className="z-10 h-3 w-3 rounded-full bg-white ring-2 ring-blue-400 dark:ring-blue-400" />
                              </div>

                              <div className="mb-2 flex items-center gap-3 md:hidden">
                                <div className="h-3 w-3 shrink-0 rounded-full bg-white ring-2 ring-blue-400" />
                                <span className="text-xs font-medium text-gray-400">{milestone.year}</span>
                              </div>

                              <div className={`w-full md:w-1/2 ${isLeft ? 'md:invisible md:py-3' : 'md:pl-10'}`}>
                                {!isLeft && (
                                  <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800/80">
                                    <span className="mb-2 inline-block rounded-md bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-500 dark:bg-blue-400/10 dark:text-blue-400">
                                      {milestone.year}
                                    </span>
                                    <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">{milestone.title}</h3>
                                    <p className="mt-1 text-sm leading-relaxed text-gray-500 dark:text-gray-400">{milestone.description}</p>
                                  </div>
                                )}
                              </div>
                            </div>
                          )
                        })}

                        {visibleGroup.hasMore && (
                          <div className="relative flex flex-col md:flex-row md:items-center">
                            <div className="absolute top-0 left-1/2 hidden h-1/2 w-0.5 -translate-x-1/2 bg-gray-200 dark:bg-gray-700 md:block" />
                            <div className="absolute left-1/2 hidden -translate-x-1/2 md:flex md:items-center md:justify-center">
                              <button
                                type="button"
                                onClick={() => toggleYearMilestones(group.calYear)}
                                className="z-10 rounded-full border border-gray-300 bg-white px-4 py-1 text-xs font-semibold text-gray-500 shadow-sm transition-colors hover:border-blue-400 hover:bg-blue-50 hover:text-blue-500 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-400 dark:hover:border-blue-400 dark:hover:bg-blue-500 dark:hover:text-white"
                              >
                                + more
                              </button>
                            </div>
                            <button
                              type="button"
                              onClick={() => toggleYearMilestones(group.calYear)}
                              className="my-3 flex items-center gap-2 text-xs font-medium text-blue-400 hover:underline md:hidden"
                            >
                              <span className="flex h-3 w-3 shrink-0 items-center justify-center rounded-full ring-2 ring-blue-400" />
                              Show more in {group.calYear}
                            </button>
                            <div className="hidden w-full py-3 md:block" />
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })
            })()}
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
                  {millify(Math.floor(stat.value / 10 || 0) * 10)}+
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

export default About
