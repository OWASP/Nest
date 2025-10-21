'use client'
import { useQuery, useApolloClient } from '@apollo/client/react'
import {
  faCode,
  faCodeBranch,
  faCodeMerge,
  faExclamationCircle,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import millify from 'millify'
import Image from 'next/image'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'

import { handleAppError, ErrorDisplay } from 'app/global-error'
import {
  GetBoardCandidatesDocument,
  GetMemberSnapshotDocument,
  GetChapterByKeyDocument,
  GetProjectByKeyDocument,
} from 'types/__generated__/boardQueries.generated'
import { formatDate } from 'utils/dateFormatter'
import ContributionHeatmap from 'components/ContributionHeatmap'
import LoadingSpinner from 'components/LoadingSpinner'

dayjs.extend(relativeTime)

type Candidate = {
  id: string
  memberName: string
  memberEmail: string
  description: string
  member?: {
    id: string
    login: string
    name: string
    avatarUrl: string
    bio?: string
    createdAt?: number
    firstOwaspContributionAt?: number
    isOwaspBoardMember?: boolean
    isFormerOwaspStaff?: boolean
    isGsocMentor?: boolean
  }
}

type MemberSnapshot = {
  id: string
  startAt: string
  endAt: string
  commitsCount: number
  pullRequestsCount: number
  issuesCount: number
  messagesCount: number
  totalContributions: number
  contributionHeatmapData: Record<string, number>
  communicationHeatmapData?: Record<string, number>
  chapterContributions?: Record<string, number>
  projectContributions?: Record<string, number>
  repositoryContributions?: Record<string, number>
  channelCommunications?: Record<string, number> // channel_name -> message_count
  githubUser: {
    login: string
  }
}

type Chapter = {
  id: string
  key: string
  name: string
  url: string
}

type Project = {
  id: string
  key: string
  name: string
  level: string
  type: string
  url: string
}

type CandidateWithSnapshot = Candidate & {
  snapshot?: MemberSnapshot
}

const BoardCandidatesPage = () => {
  const { year } = useParams<{ year: string }>()
  const [candidates, setCandidates] = useState<CandidateWithSnapshot[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [boardUrl, setBoardUrl] = useState<string>('')

  const { data: graphQLData, error: graphQLRequestError } = useQuery(GetBoardCandidatesDocument, {
    variables: { year: Number.parseInt(year) },
  })

  useEffect(() => {
    if (graphQLData?.boardOfDirectors) {
      setCandidates(graphQLData.boardOfDirectors.candidates || [])
      setBoardUrl(graphQLData.boardOfDirectors.owaspUrl || '')
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [graphQLData, graphQLRequestError])

  const CandidateCard = ({ candidate }: { candidate: CandidateWithSnapshot }) => {
    const client = useApolloClient()
    const [snapshot, setSnapshot] = useState<MemberSnapshot | null>(null)
    const [ledChapters, setLedChapters] = useState<Chapter[]>([])
    const [ledProjects, setLedProjects] = useState<Project[]>([])

    const { data: snapshotData } = useQuery(GetMemberSnapshotDocument, {
      variables: {
        userLogin: candidate.member?.login || '',
      },
      skip: !candidate.member?.login,
    })

    useEffect(() => {
      if (snapshotData?.memberSnapshot) {
        setSnapshot(snapshotData.memberSnapshot)
      }
    }, [snapshotData])

    // Fetch chapters based on chapterContributions keys
    useEffect(() => {
      const fetchChapters = async () => {
        if (!snapshot?.chapterContributions) return

        const chapterKeys = Object.keys(snapshot.chapterContributions)
        const chapters: Chapter[] = []

        for (const key of chapterKeys) {
          try {
            const { data } = await client.query({
              query: GetChapterByKeyDocument,
              variables: { key: key.replace('www-chapter-', '') },
            })

            if (data?.chapter) {
              chapters.push(data.chapter)
            }
          } catch {
            // Silently skip chapters that fail to fetch
          }
        }

        setLedChapters(chapters.sort((a, b) => a.name.localeCompare(b.name)))
      }

      fetchChapters()
    }, [client, snapshot?.chapterContributions])

    // Fetch projects based on projectContributions keys
    useEffect(() => {
      const fetchProjects = async () => {
        if (!snapshot?.projectContributions) return

        const projectKeys = Object.keys(snapshot.projectContributions)
        const projects: Project[] = []

        for (const key of projectKeys) {
          try {
            const { data } = await client.query({
              query: GetProjectByKeyDocument,
              variables: { key: key.replace('www-project-', '') },
            })

            if (data?.project) {
              projects.push(data.project)
            }
          } catch {
            // Silently skip projects that fail to fetch
          }
        }

        setLedProjects(projects.sort((a, b) => a.name.localeCompare(b.name)))
      }

      fetchProjects()
    }, [client, snapshot?.projectContributions])

    const handleCardClick = () => {
      // Convert name to slug format.
      const nameSlug = candidate.memberName.toLowerCase().replace(/\s+/g, '_')
      const candidateUrl = `https://owasp.org/www-board-candidates/${year}/${nameSlug}.html`
      window.open(candidateUrl, '_blank', 'noopener,noreferrer')
    }

    return (
      <Button
        onPress={handleCardClick}
        className="group flex h-auto min-h-[280px] w-full flex-col items-start rounded-lg bg-white p-6 text-left shadow-lg transition-transform duration-300 hover:scale-105 hover:shadow-xl dark:bg-gray-800 dark:shadow-gray-900/30"
      >
        <div className="flex w-full items-start gap-4">
          {candidate.member?.avatarUrl && (
            <div className="relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-full ring-2 ring-gray-100 group-hover:ring-blue-400 dark:ring-gray-700">
              <Image
                fill
                src={`${candidate.member.avatarUrl}&s=160`}
                alt={candidate.memberName}
                className="object-cover"
              />
            </div>
          )}
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
              {candidate.memberName}
            </h3>
            {candidate.member?.login && (
              <Link
                href={`https://github.com/${candidate.member.login}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-400 hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                @{candidate.member.login}
              </Link>
            )}
            {candidate.member?.createdAt && (
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                GitHub account created{' '}
                <span className="underline">
                  {dayjs(
                    typeof candidate.member.createdAt === 'number'
                      ? candidate.member.createdAt * 1000
                      : candidate.member.createdAt
                  ).fromNow()}
                </span>{' '}
                - {formatDate(candidate.member.createdAt)}
              </p>
            )}
            {candidate.member?.firstOwaspContributionAt && (
              <p className="text-sm text-gray-600 dark:text-gray-400">
                First OWASP contribution made nearly{' '}
                <span className="underline">
                  {dayjs(candidate.member.firstOwaspContributionAt * 1000).fromNow()}
                </span>{' '}
                - {formatDate(candidate.member.firstOwaspContributionAt)}
              </p>
            )}
          </div>
        </div>

        <div className="mt-4">
          <p className="text-sm break-words whitespace-pre-wrap text-gray-700 dark:text-gray-300">
            {candidate.member?.bio || (
              <span className="text-gray-500 dark:text-gray-400">No profile description</span>
            )}
          </p>
        </div>

        {candidate.description && (
          <p className="mt-4 line-clamp-3 text-sm text-gray-700 dark:text-gray-300">
            {candidate.description}
          </p>
        )}

        {snapshot && (
          <div className="mt-4 w-full border-t border-gray-200 pt-4 dark:border-gray-700">
            <h4 className="mb-2 text-sm text-gray-700 dark:text-gray-300">
              <span className="font-semibold">OWASP Ecosystem Contributions</span>
            </h4>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="flex items-center gap-2">
                <FontAwesomeIcon
                  icon={faCode}
                  className="h-4 w-4 text-gray-600 dark:text-gray-400"
                />
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Commits</p>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {millify(snapshot.commitsCount, { precision: 1 })}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <FontAwesomeIcon
                  icon={faCodeBranch}
                  className="h-4 w-4 text-gray-600 dark:text-gray-400"
                />
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">PRs</p>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {millify(snapshot.pullRequestsCount, { precision: 1 })}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <FontAwesomeIcon
                  icon={faExclamationCircle}
                  className="h-4 w-4 text-gray-600 dark:text-gray-400"
                />
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Issues</p>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {millify(snapshot.issuesCount, { precision: 1 })}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <FontAwesomeIcon
                  icon={faCodeMerge}
                  className="h-4 w-4 text-gray-600 dark:text-gray-400"
                />
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total</p>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {millify(snapshot.totalContributions, { precision: 1 })}
                  </p>
                </div>
              </div>
            </div>
            {snapshot.contributionHeatmapData &&
              Object.keys(snapshot.contributionHeatmapData).length > 0 && (
                <div className="mt-3">
                  <ContributionHeatmap
                    contributionData={snapshot.contributionHeatmapData}
                    startDate={snapshot.startAt}
                    endDate={snapshot.endAt}
                  />
                </div>
              )}
            <div className="mt-4 w-full">
              <h4 className="mb-2 text-sm text-gray-700 dark:text-gray-300">
                <span className="font-semibold">Leadership</span>
                {(ledChapters.length > 0 || ledProjects.length > 0) && (
                  <span className="font-normal">
                    {' '}
                    (
                    {ledChapters.length > 0 && (
                      <>
                        {ledChapters.length} chapter{ledChapters.length !== 1 ? 's' : ''}
                      </>
                    )}
                    {ledChapters.length > 0 && ledProjects.length > 0 && ', '}
                    {ledProjects.length > 0 && (
                      <>
                        {ledProjects.length} project{ledProjects.length !== 1 ? 's' : ''}
                      </>
                    )}
                    )
                  </span>
                )}
              </h4>
              {ledChapters.length === 0 && ledProjects.length === 0 ? (
                <div className="inline-flex items-center gap-1.5 rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-gray-600/10 ring-inset dark:bg-gray-800/50 dark:text-gray-400 dark:ring-gray-400/30">
                  No chapters or projects are lead by this candidate
                </div>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {ledChapters.map((chapter) => {
                    // Strip prefix if present to get bare key
                    const bareKey = chapter.key.startsWith('www-chapter-')
                      ? chapter.key.replace('www-chapter-', '')
                      : chapter.key
                    // Check both key formats for compatibility
                    const directKey = snapshot?.chapterContributions?.[bareKey]
                    const withPrefix = snapshot?.chapterContributions?.[`www-chapter-${bareKey}`]
                    const contributionCount = directKey || withPrefix || 0

                    return (
                      <Link
                        key={chapter.id}
                        href={`/chapters/${chapter.key.replace('www-chapter-', '')}`}
                        className="inline-flex items-center gap-1.5 rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-700/10 ring-inset hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-400 dark:ring-blue-400/30 dark:hover:bg-blue-900/30"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <span>{chapter.name}</span>
                        <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-semibold text-blue-800 dark:bg-blue-800/40 dark:text-blue-300">
                          {contributionCount === 0
                            ? 'no contributions'
                            : `${contributionCount} contributions`}
                        </span>
                      </Link>
                    )
                  })}
                  {ledProjects.map((project) => {
                    // Strip prefix if present to get bare key
                    const bareKey = project.key.startsWith('www-project-')
                      ? project.key.replace('www-project-', '')
                      : project.key
                    // Check both key formats for compatibility
                    const directKey = snapshot?.projectContributions?.[bareKey]
                    const withPrefix = snapshot?.projectContributions?.[`www-project-${bareKey}`]
                    const contributionCount = directKey || withPrefix || 0
                    return (
                      <Link
                        key={project.id}
                        href={`/projects/${project.key.replace('www-project-', '')}`}
                        className="inline-flex items-center gap-1.5 rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-700/10 ring-inset hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-400 dark:ring-blue-400/30 dark:hover:bg-blue-900/30"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <span>{project.name}</span>
                        <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-semibold text-blue-800 dark:bg-blue-800/40 dark:text-blue-300">
                          {contributionCount === 0
                            ? 'no contributions'
                            : `${contributionCount} contributions`}
                        </span>
                      </Link>
                    )
                  })}
                </div>
              )}
            </div>
            {snapshot.repositoryContributions &&
              Object.keys(snapshot.repositoryContributions).length > 0 &&
              (() => {
                const sortedRepos = Object.entries(snapshot.repositoryContributions).sort(
                  ([, a], [, b]) => (b as number) - (a as number)
                )
                const topRepo = sortedRepos[0]
                const [topRepoName, topRepoCount] = topRepo

                return (
                  <div className="mt-4 w-full">
                    <div className="mb-3">
                      <h4 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Most Active Repositories
                      </h4>
                      <a
                        href={`https://github.com/${topRepoName}/commits?author=${candidate.member?.login}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-green-700/10 ring-inset hover:bg-green-100 dark:bg-green-900/20 dark:text-green-400 dark:ring-green-400/30 dark:hover:bg-green-900/30"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <span>{topRepoName}</span>
                        <span className="rounded bg-green-100 px-1.5 py-0.5 text-[10px] font-semibold text-green-800 dark:bg-green-800/40 dark:text-green-300">
                          {Number(topRepoCount)} commits
                        </span>
                      </a>
                    </div>
                    {sortedRepos.length > 1 && (
                      <div>
                        <div className="flex flex-wrap gap-2">
                          {sortedRepos.slice(1).map(([repoName, count]) => {
                            const commitCount = Number(count)
                            return (
                              <a
                                key={repoName}
                                href={`https://github.com/${repoName}/commits?author=${candidate.member?.login}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1.5 rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-700/10 ring-inset hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-400 dark:ring-blue-400/30 dark:hover:bg-blue-900/30"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <span>{repoName}</span>
                                <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-semibold text-blue-800 dark:bg-blue-800/40 dark:text-blue-300">
                                  {commitCount} commits
                                </span>
                              </a>
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })()}
          </div>
        )}

        {/* Slack Communications Heatmap */}
        {snapshot?.communicationHeatmapData &&
          Object.keys(snapshot.communicationHeatmapData).length > 0 && (
            <div className="mt-4 w-full border-t border-gray-200 pt-4 dark:border-gray-700">
              <ContributionHeatmap
                contributionData={snapshot.communicationHeatmapData}
                startDate={snapshot.startAt}
                endDate={snapshot.endAt}
                title="OWASP Community Communication"
                unit="message"
              />
            </div>
          )}

        {/* Most Active Channels */}
        {snapshot?.channelCommunications &&
          Object.keys(snapshot.channelCommunications).length > 0 &&
          (() => {
            const sortedChannels = Object.entries(snapshot.channelCommunications).sort(
              ([, a], [, b]) => (Number(b) || 0) - (Number(a) || 0)
            )

            if (sortedChannels.length === 0) return null

            const topChannel = sortedChannels[0]
            const [topChannelName, topChannelCount] = topChannel

            return (
              <div className="mt-4 w-full">
                <div className="mb-3">
                  <h4 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Most Active Channels
                  </h4>
                  <a
                    href={`https://owasp.slack.com/archives/${topChannelName}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-green-700/10 ring-inset hover:bg-green-100 dark:bg-green-900/20 dark:text-green-400 dark:ring-green-400/30 dark:hover:bg-green-900/30"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <span>#{topChannelName}</span>
                    <span className="rounded bg-green-100 px-1.5 py-0.5 text-[10px] font-semibold text-green-800 dark:bg-green-800/40 dark:text-green-300">
                      {Number(topChannelCount)} messages
                    </span>
                  </a>
                </div>
                {sortedChannels.length > 1 && (
                  <div>
                    <div className="flex flex-wrap gap-2">
                      {sortedChannels.slice(1).map(([channelName, messageCount]) => (
                        <a
                          key={channelName}
                          href={`https://owasp.slack.com/archives/${channelName}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-700/10 ring-inset hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-400 dark:ring-blue-400/30 dark:hover:bg-blue-900/30"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <span>#{channelName}</span>
                          <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-semibold text-blue-800 dark:bg-blue-800/40 dark:text-blue-300">
                            {Number(messageCount)} messages
                          </span>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )
          })()}

        {/* Additional Information */}
        {(candidate.member?.isOwaspBoardMember ||
          candidate.member?.isFormerOwaspStaff ||
          candidate.member?.isGsocMentor) && (
          <div className="mt-4 w-full border-t border-gray-200 pt-4 dark:border-gray-700">
            <h4 className="mb-2 text-sm text-gray-700 dark:text-gray-300">
              <span className="font-semibold">Additional Information</span>
            </h4>
            <div className="flex flex-wrap gap-2">
              {candidate.member.isOwaspBoardMember && (
                <span className="inline-flex items-center gap-1.5 rounded-md bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700 ring-1 ring-purple-700/10 ring-inset dark:bg-purple-900/20 dark:text-purple-400 dark:ring-purple-400/30">
                  Current OWASP Board of Directors Member
                </span>
              )}
              {candidate.member.isFormerOwaspStaff && (
                <span className="inline-flex items-center gap-1.5 rounded-md bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700 ring-1 ring-purple-700/10 ring-inset dark:bg-purple-900/20 dark:text-purple-400 dark:ring-purple-400/30">
                  Former OWASP Staff Member
                </span>
              )}
              {candidate.member.isGsocMentor && (
                <span className="inline-flex items-center gap-1.5 rounded-md bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700 ring-1 ring-purple-700/10 ring-inset dark:bg-purple-900/20 dark:text-purple-400 dark:ring-purple-400/30">
                  Google Summer of Code Mentor
                </span>
              )}
            </div>
          </div>
        )}
      </Button>
    )
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!graphQLData?.boardOfDirectors) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Board not found"
        message={`Sorry, the board information for ${year} doesn't exist`}
      />
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
          {year} Board of Directors Candidates
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Meet the candidates running for the OWASP Board of Directors
          {boardUrl && (
            <>
              {' '}
              (
              <Link
                href={boardUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline dark:text-blue-400"
              >
                view election details
              </Link>
              )
            </>
          )}
        </p>
        <p className="mt-3 text-sm text-gray-500 italic dark:text-gray-500">
          This page is built using publicly available data from the OWASP GitHub organization and
          OWASP Slack workspace. The code is open source and available as part of{' '}
          <Link
            href="https://github.com/OWASP/Nest"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline dark:text-blue-400"
          >
            OWASP Nest
          </Link>{' '}
          (contributions and improvement suggestions are always welcome).
        </p>
      </div>

      {candidates.length === 0 ? (
        <div className="rounded-lg bg-white p-8 text-center shadow-md dark:bg-gray-800">
          <p className="text-gray-600 dark:text-gray-400">No candidates found for {year}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          {candidates.map((candidate) => (
            <CandidateCard key={candidate.id} candidate={candidate} />
          ))}
        </div>
      )}
    </div>
  )
}

export default BoardCandidatesPage
