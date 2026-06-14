'use client'
import { useQuery, useLazyQuery, useApolloClient } from '@apollo/client/react'
import { useRouter, useParams } from 'next/navigation'
import React, { useEffect, useState, useMemo } from 'react'
import { FaCalendarAlt, FaMapMarkerAlt } from 'react-icons/fa'
import {
  FaCalendar,
  FaChevronDown,
  FaChevronUp,
  FaCircleExclamation,
  FaCodePullRequest,
  FaFolder,
  FaNewspaper,
  FaRightToBracket,
  FaTag,
} from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import {
  GetSnapshotDetailsDocument,
  GetSnapshotPullRequestsDocument,
  GetSnapshotIssuesDocument,
} from 'types/__generated__/snapshotQueries.generated'
import type { GetSnapshotDetailsQuery } from 'types/__generated__/snapshotQueries.generated'
import type { Chapter } from 'types/chapter'
import type { Contributor } from 'types/contributor'
import type { Issue } from 'types/issue'
import type { Project } from 'types/project'
import type { PullRequest } from 'types/pullRequest'
import type { Release as ReleaseType } from 'types/release'
import { level } from 'utils/data'
import { formatDate } from 'utils/dateFormatter'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import Card from 'components/Card'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import ContributorsList from 'components/ContributorsList'
import EventCard from 'components/EventCard'
import LoadingSpinner from 'components/LoadingSpinner'
import PostCard from 'components/PostCard'
import RecentIssues from 'components/RecentIssues'
import RecentPullRequests from 'components/RecentPullRequests'
import SecondaryCard from 'components/SecondaryCard'
import ShowMoreButton from 'components/ShowMoreButton'
import { ReleasesSection } from 'components/SnapshotReleaseSection'

const PR_LIMIT = 6
const ISSUE_LIMIT = 6
const CHAPTERS_INITIAL = 5
const EVENTS_INITIAL = 5
const PROJECTS_INITIAL = 5
const CONTRIBUTORS_INITIAL = 12
const POSTS_INITIAL = 5

const SnapshotDetailsPage: React.FC = () => {
  const { id: snapshotKey } = useParams<{ id: string }>()
  const router = useRouter()

  const [showAllReleases, setShowAllReleases] = useState(false)
  const [showAllChapters, setShowAllChapters] = useState(false)
  const [showAllEvents, setShowAllEvents] = useState(false)
  const [showAllProjects, setShowAllProjects] = useState(false)
  const [showAllPosts, setShowAllPosts] = useState(false)

  // PR pagination state
  const [prVisibleCount, setPrVisibleCount] = useState(PR_LIMIT)
  const [hasMorePRs, setHasMorePRs] = useState(true)
  const [isFetchingMorePRs, setIsFetchingMorePRs] = useState(false)

  // Issue pagination state
  const [issueVisibleCount, setIssueVisibleCount] = useState(ISSUE_LIMIT)
  const [hasMoreIssues, setHasMoreIssues] = useState(true)
  const [isFetchingMoreIssues, setIsFetchingMoreIssues] = useState(false)

  const {
    data,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetSnapshotDetailsDocument, {
    variables: {
      key: snapshotKey,
      prLimit: PR_LIMIT,
      prOffset: 0,
      issueLimit: ISSUE_LIMIT,
      issueOffset: 0,
    },
    fetchPolicy: 'cache-and-network',
  })

  const client = useApolloClient()

  const [fetchMorePRs] = useLazyQuery(GetSnapshotPullRequestsDocument, {
    fetchPolicy: 'network-only',
  })

  const [fetchMoreIssues] = useLazyQuery(GetSnapshotIssuesDocument, {
    fetchPolicy: 'network-only',
  })

  const snapshot = data?.snapshot
  useEffect(() => {
    setShowAllReleases(false)
    setShowAllChapters(false)
    setShowAllEvents(false)
    setShowAllProjects(false)
    setShowAllPosts(false)
    setPrVisibleCount(PR_LIMIT)
    setHasMorePRs((snapshot?.pullRequests?.length ?? 0) >= PR_LIMIT)
    setIssueVisibleCount(ISSUE_LIMIT)
    setHasMoreIssues((snapshot?.issues?.length ?? 0) >= ISSUE_LIMIT)
    // Reset pagination when snapshot key changes (not on array updates)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [snapshot?.key])

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError, snapshotKey])

  const sortedEvents = useMemo(() => {
    if (!snapshot?.events) return []
    return [...snapshot.events].sort((a, b) => {
      const priority: Record<string, number> = {
        global: 0,
        appsecdays: 1,
        partner: 2,
        other: 3,
      }
      const normalize = (cat: string) => cat.toLowerCase().replaceAll('_', '')
      return (
        (priority[normalize(a.category ?? '')] ?? 4) - (priority[normalize(b.category ?? '')] ?? 4)
      )
    })
  }, [snapshot?.events])

  const renderProjectCard = (project: Project) => {
    const params: string[] = ['forksCount', 'starsCount', 'contributorsCount']
    const filteredIcons = getFilteredIcons(project, params)

    const handleButtonClick = () => {
      router.push(`/projects/${project.key}`)
    }

    const submitButton = {
      label: 'View Details',
      icon: <FaRightToBracket className="h-4 w-4" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        button={submitButton}
        cardKey={project.key ?? project.name}
        className="border-0! bg-gray-200! dark:bg-gray-700!"
        icons={filteredIcons}
        level={
          project.level ? level[`${project.level.toLowerCase() as keyof typeof level}`] : undefined
        }
        summary={project.summary ?? ''}
        title={project.name}
        topContributors={project.topContributors}
        url={`/projects/${project.key}`}
      />
    )
  }

  const renderChapterCard = (chapter: Chapter) => {
    const params: string[] = ['updatedAt']
    const filteredIcons = getFilteredIcons(chapter, params)
    const formattedUrls = handleSocialUrls(chapter.relatedUrls ?? [])

    const handleButtonClick = () => {
      router.push(`/chapters/${chapter.key}`)
    }

    const submitButton = {
      label: 'View Details',
      icon: <FaRightToBracket className="h-4 w-4" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        button={submitButton}
        cardKey={chapter.key}
        className="border-0! bg-gray-200! dark:bg-gray-700!"
        icons={filteredIcons}
        social={formattedUrls}
        summary={chapter.summary ?? ''}
        title={chapter.name}
        url={`/chapters/${chapter.key}`}
      />
    )
  }

  if (isLoading && !snapshot) {
    return <LoadingSpinner />
  }

  if (graphQLRequestError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading snapshot"
        message="An error occurred while loading the snapshot data"
      />
    )
  }

  if (!data || !snapshot) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Snapshot not found"
        message="Sorry, the snapshot you're looking for doesn't exist"
      />
    )
  }

  return (
    <div className="mx-auto min-h-screen max-w-6xl p-4">
      <div className="mt-8 mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="mb-2 text-3xl font-bold text-gray-700 dark:text-gray-200">
              {snapshot.title}
            </h1>
            <div className="flex flex-wrap items-center gap-2 text-gray-600 dark:text-gray-300">
              <div className="flex items-center">
                <FaCalendar className="mr-1 h-4 w-4" />
                <span>
                  {formatDate(snapshot.startAt)} - {formatDate(snapshot.endAt)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Community Impact */}
      {snapshot.chapters && snapshot.chapters.length > 0 && (
        <SecondaryCard icon={FaMapMarkerAlt} title="New Chapters">
          <div className="mb-4">
            <ChapterMapWrapper
              geoLocData={snapshot.chapters as unknown as Chapter[]}
              showLocal={false}
              showLocationSharing={true}
              style={{ height: '400px', width: '100%', zIndex: '0' }}
            />
          </div>
          <div className="flex flex-col gap-6">
            {snapshot.chapters
              .filter((chapter) => chapter.isActive)
              .slice(0, showAllChapters ? undefined : CHAPTERS_INITIAL)
              .map((chapter) => (
                <React.Fragment key={chapter.key}>
                  {renderChapterCard(chapter as unknown as Chapter)}
                </React.Fragment>
              ))}
          </div>
          {snapshot.chapters.filter((chapter) => chapter.isActive).length > CHAPTERS_INITIAL && (
            <ShowMoreButton
              expanded={showAllChapters}
              onToggle={() => setShowAllChapters((prev) => !prev)}
            />
          )}
        </SecondaryCard>
      )}

      {snapshot.events && snapshot.events.length > 0 && (
        <SecondaryCard icon={FaCalendarAlt} title="New Events">
          <div className="flex flex-col gap-4">
            {sortedEvents.slice(0, showAllEvents ? undefined : EVENTS_INITIAL).map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
          {snapshot.events.length > EVENTS_INITIAL && (
            <ShowMoreButton
              expanded={showAllEvents}
              onToggle={() => setShowAllEvents((prev) => !prev)}
            />
          )}
        </SecondaryCard>
      )}

      {/* Deliverables */}
      {snapshot.projects && snapshot.projects.length > 0 && (
        <SecondaryCard icon={FaFolder} title="New Projects">
          <div className="flex flex-col gap-6">
            {snapshot.projects
              .filter((project) => project.isActive)
              .slice(0, showAllProjects ? undefined : PROJECTS_INITIAL)
              .map((project) => (
                <React.Fragment key={project.key}>{renderProjectCard(project)}</React.Fragment>
              ))}
          </div>
          {snapshot.projects.filter((project) => project.isActive).length > PROJECTS_INITIAL && (
            <ShowMoreButton
              expanded={showAllProjects}
              onToggle={() => setShowAllProjects((prev) => !prev)}
            />
          )}
        </SecondaryCard>
      )}

      {snapshot.releases && snapshot.releases.length > 0 && (
        <SecondaryCard icon={FaTag} title="New Releases">
          <ReleasesSection
            releases={snapshot.releases as ReleaseType[]}
            showAll={showAllReleases}
            onToggle={() => setShowAllReleases((p) => !p)}
          />
        </SecondaryCard>
      )}

      {/* Activity */}
      {snapshot.users && snapshot.users.length > 0 && (
        <ContributorsList
          contributors={snapshot.users as Contributor[]}
          title="New Contributors"
          icon={HiUserGroup}
          maxInitialDisplay={CONTRIBUTORS_INITIAL}
          variant="card"
          getUrl={(login) => `https://github.com/${login}`}
        />
      )}

      {snapshot.pullRequests && snapshot.pullRequests.length > 0 && (
        <SecondaryCard icon={FaCodePullRequest} title="New Pull Requests">
          <RecentPullRequests
            data={snapshot.pullRequests.slice(0, prVisibleCount) as PullRequest[]}
            variant="full"
          />
          {(hasMorePRs ||
            snapshot.pullRequests.length > prVisibleCount ||
            prVisibleCount > PR_LIMIT) && (
            <div className="mt-4 flex justify-start gap-4">
              {(hasMorePRs || snapshot.pullRequests.length > prVisibleCount) && (
                <button
                  disabled={isFetchingMorePRs}
                  onClick={() => {
                    if (isFetchingMorePRs) return
                    const currentLength = snapshot.pullRequests?.length || 0
                    if (hasMorePRs && currentLength < prVisibleCount + PR_LIMIT) {
                      setIsFetchingMorePRs(true)
                      fetchMorePRs({
                        variables: {
                          key: snapshotKey,
                          offset: currentLength,
                          limit: PR_LIMIT,
                        },
                      })
                        .then(({ data: prData }) => {
                          const newPRs = prData?.snapshot?.pullRequests || []
                          if (newPRs.length < PR_LIMIT) setHasMorePRs(false)
                          if (newPRs.length > 0) {
                            client.cache.updateQuery(
                              {
                                query: GetSnapshotDetailsDocument,
                                variables: {
                                  key: snapshotKey,
                                  prLimit: PR_LIMIT,
                                  prOffset: 0,
                                  issueLimit: ISSUE_LIMIT,
                                  issueOffset: 0,
                                },
                              },
                              (prev: GetSnapshotDetailsQuery | null) =>
                                prev?.snapshot
                                  ? {
                                      ...prev,
                                      snapshot: {
                                        ...prev.snapshot,
                                        pullRequests: [
                                          ...(prev.snapshot.pullRequests || []),
                                          ...newPRs,
                                        ],
                                      },
                                    }
                                  : prev
                            )
                            setPrVisibleCount((prev) => prev + newPRs.length)
                          }
                        })
                        .catch((err) => handleAppError(err))
                        .finally(() => setIsFetchingMorePRs(false))
                      return
                    }
                    setPrVisibleCount((prev) =>
                      Math.min(snapshot.pullRequests.length, prev + PR_LIMIT)
                    )
                  }}
                  type="button"
                  className={`flex items-center bg-transparent px-2 py-1 text-sm text-blue-400 ${isFetchingMorePRs ? 'cursor-not-allowed opacity-50' : 'hover:underline'}`}
                >
                  {isFetchingMorePRs ? 'Loading...' : 'Show more'}{' '}
                  <FaChevronDown aria-hidden="true" className="ml-2 text-sm" />
                </button>
              )}
              {!isFetchingMorePRs &&
                prVisibleCount > PR_LIMIT &&
                snapshot.pullRequests.length > PR_LIMIT && (
                  <button
                    disabled={isFetchingMorePRs}
                    onClick={() => setPrVisibleCount(PR_LIMIT)}
                    type="button"
                    className={`flex items-center bg-transparent px-2 py-1 text-sm text-blue-400 hover:underline ${isFetchingMorePRs ? 'cursor-not-allowed opacity-50' : ''}`}
                  >
                    Show less <FaChevronUp aria-hidden="true" className="ml-2 text-sm" />
                  </button>
                )}
            </div>
          )}
        </SecondaryCard>
      )}

      {snapshot.issues && snapshot.issues.length > 0 && (
        <SecondaryCard icon={FaCircleExclamation} title="New Issues">
          <RecentIssues
            data={snapshot.issues.slice(0, issueVisibleCount) as Issue[]}
            variant="full"
          />
          {(hasMoreIssues ||
            snapshot.issues.length > issueVisibleCount ||
            issueVisibleCount > ISSUE_LIMIT) && (
            <div className="mt-4 flex justify-start gap-4">
              {(hasMoreIssues || snapshot.issues.length > issueVisibleCount) && (
                <button
                  disabled={isFetchingMoreIssues}
                  onClick={() => {
                    if (isFetchingMoreIssues) return
                    const currentLength = snapshot.issues?.length || 0
                    if (hasMoreIssues && currentLength < issueVisibleCount + ISSUE_LIMIT) {
                      setIsFetchingMoreIssues(true)
                      fetchMoreIssues({
                        variables: {
                          key: snapshotKey,
                          offset: currentLength,
                          limit: ISSUE_LIMIT,
                        },
                      })
                        .then(({ data: issueData }) => {
                          const newIssues = issueData?.snapshot?.issues || []
                          if (newIssues.length < ISSUE_LIMIT) setHasMoreIssues(false)
                          if (newIssues.length > 0) {
                            client.cache.updateQuery(
                              {
                                query: GetSnapshotDetailsDocument,
                                variables: {
                                  key: snapshotKey,
                                  prLimit: PR_LIMIT,
                                  prOffset: 0,
                                  issueLimit: ISSUE_LIMIT,
                                  issueOffset: 0,
                                },
                              },
                              (prev: GetSnapshotDetailsQuery | null) =>
                                prev?.snapshot
                                  ? {
                                      ...prev,
                                      snapshot: {
                                        ...prev.snapshot,
                                        issues: [...(prev.snapshot.issues || []), ...newIssues],
                                      },
                                    }
                                  : prev
                            )
                            setIssueVisibleCount((prev) => prev + newIssues.length)
                          }
                        })
                        .catch((err) => handleAppError(err))
                        .finally(() => setIsFetchingMoreIssues(false))
                      return
                    }
                    setIssueVisibleCount((prev) =>
                      Math.min(snapshot.issues.length, prev + ISSUE_LIMIT)
                    )
                  }}
                  type="button"
                  className={`flex items-center bg-transparent px-2 py-1 text-sm text-blue-400 ${isFetchingMoreIssues ? 'cursor-not-allowed opacity-50' : 'hover:underline'}`}
                >
                  {isFetchingMoreIssues ? 'Loading...' : 'Show more'}{' '}
                  <FaChevronDown aria-hidden="true" className="ml-2 text-sm" />
                </button>
              )}
              {!isFetchingMoreIssues &&
                issueVisibleCount > ISSUE_LIMIT &&
                snapshot.issues.length > ISSUE_LIMIT && (
                  <button
                    disabled={isFetchingMoreIssues}
                    onClick={() => setIssueVisibleCount(ISSUE_LIMIT)}
                    type="button"
                    className={`flex items-center bg-transparent px-2 py-1 text-sm text-blue-400 hover:underline ${isFetchingMoreIssues ? 'cursor-not-allowed opacity-50' : ''}`}
                  >
                    Show less <FaChevronUp aria-hidden="true" className="ml-2 text-sm" />
                  </button>
                )}
            </div>
          )}
        </SecondaryCard>
      )}

      {snapshot.posts && snapshot.posts.length > 0 && (
        <SecondaryCard icon={FaNewspaper} title="New Posts">
          <div className="flex flex-col gap-4">
            {snapshot.posts.slice(0, showAllPosts ? undefined : POSTS_INITIAL).map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
          {snapshot.posts.length > POSTS_INITIAL && (
            <ShowMoreButton
              expanded={showAllPosts}
              onToggle={() => setShowAllPosts((prev) => !prev)}
            />
          )}
        </SecondaryCard>
      )}
    </div>
  )
}

export default SnapshotDetailsPage
