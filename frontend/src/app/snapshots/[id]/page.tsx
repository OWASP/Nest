'use client'

import { useQuery } from '@apollo/client'
import {
  faCalendar,
  faUsers,
  faFolder,
  faBook,
  faBug,
  faTag,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter, useParams } from 'next/navigation'
import React, { useState, useEffect } from 'react'

import { GET_SNAPSHOT_DETAILS } from 'server/queries/snapshotQueries'
import { ChapterTypeGraphQL } from 'types/chapter'
import { ProjectTypeGraphql } from 'types/project'
import { SnapshotDetailsProps } from 'types/snapshot'
import { level } from 'utils/data'
import { formatDate } from 'utils/dateFormatter'
import { getFilteredIconsGraphql, handleSocialUrls } from 'utils/utility'

import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import LoadingSpinner from 'components/LoadingSpinner'
import { handleAppError, ErrorDisplay } from 'app/global-error'

type ParsedSummary = {
  users: { count: number; examples: string[] }
  projects: { count: number; examples: string[] }
  chapters: { count: number; examples: string[] }
  issues: { count: number; examples: string[] }
  releases: { count: number; examples: string[] }
}

const parseSnapshotSummary = (summary: string): ParsedSummary => {
  const result: ParsedSummary = {
    users: { count: 0, examples: [] },
    projects: { count: 0, examples: [] },
    chapters: { count: 0, examples: [] },
    issues: { count: 0, examples: [] },
    releases: { count: 0, examples: [] },
  }

  if (!summary) return result

  const sections = [
    { key: 'users', pattern: /(\d+) users \(e\.g\.,\s*([^)]+)\)/i },
    { key: 'projects', pattern: /(\d+) projects \(e\.g\.,\s*([^)]+)\)/i },
    { key: 'chapters', pattern: /(\d+) chapters \(e\.g\.,\s*([^)]+)\)/i },
    { key: 'issues', pattern: /(\d+) issues \(e\.g\.,\s*([^)]+)\)/i },
    { key: 'releases', pattern: /(\d+) releases \(e\.g\.,\s*([^)]+)\)/i },
  ]

  sections.forEach((section) => {
    const match = summary.match(section.pattern)
    if (match && match.length >= 3) {
      result[section.key as keyof ParsedSummary] = {
        count: parseInt(match[1], 10),
        examples: match[2].split(',').map((s) => s.trim()),
      }
    }
  })

  return result
}

const SnapshotDetailsPage: React.FC = () => {
  const { id: snapshotKey } = useParams()
  const [snapshot, setSnapshot] = useState<SnapshotDetailsProps | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const router = useRouter()
  const [summaryData, setSummaryData] = useState<ParsedSummary | null>(null)

  const { data: graphQLData, error: graphQLRequestError } = useQuery(GET_SNAPSHOT_DETAILS, {
    variables: { key: snapshotKey },
  })

  useEffect(() => {
    if (graphQLData) {
      setSnapshot(graphQLData.snapshot)
      setSummaryData(parseSnapshotSummary(graphQLData.snapshot.summary))
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [graphQLData, graphQLRequestError, snapshotKey])

  const renderProjectCard = (project: ProjectTypeGraphql) => {
    const params: string[] = ['forksCount', 'starsCount', 'contributorsCount']
    const filteredIcons = getFilteredIconsGraphql(project, params)

    const handleButtonClick = () => {
      router.push(`/projects/${project.key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        button={SubmitButton}
        icons={filteredIcons}
        key={project.key}
        level={level[`${project.level.toLowerCase() as keyof typeof level}`]}
        summary={project.summary}
        title={project.name}
        topContributors={project.topContributors}
        url={`/projects/${project.key}`}
      />
    )
  }

  const renderChapterCard = (chapter: ChapterTypeGraphQL) => {
    const params: string[] = ['updatedAt']
    const filteredIcons = getFilteredIconsGraphql(chapter, params)
    const formattedUrls = handleSocialUrls(chapter.relatedUrls)

    const handleButtonClick = () => {
      router.push(`/chapters/${chapter.key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        key={chapter.key}
        title={chapter.name}
        url={`/chapters/${chapter.key}`}
        summary={chapter.summary}
        icons={filteredIcons}
        topContributors={chapter.topContributors}
        button={SubmitButton}
        social={formattedUrls}
      />
    )
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!isLoading && snapshot == null) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Snapshot not found"
        message="Sorry, the snapshot you're looking for doesn't exist"
      />
    )
  }

  return (
    <div className="mx-auto mt-16 min-h-screen max-w-6xl p-4">
      <div className="mb-8 mt-8 rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="mb-2 text-3xl font-bold text-gray-700 dark:text-gray-200">
              {snapshot?.title}
            </h1>
            <div className="flex flex-wrap items-center gap-2 text-gray-600 dark:text-gray-300">
              <div className="flex items-center">
                <FontAwesomeIcon icon={faCalendar} className="mr-1 h-4 w-4" />
                <span>
                  {formatDate(snapshot?.startAt ?? '')} - {formatDate(snapshot?.endAt ?? '')}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {summaryData && (
        <div className="mb-8 rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <h2 className="mb-4 text-2xl font-semibold text-gray-700 dark:text-gray-200">
            Snapshot Summary
          </h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { label: 'Users', data: summaryData.users, icon: faUsers },
              { label: 'Projects', data: summaryData.projects, icon: faFolder },
              { label: 'Chapters', data: summaryData.chapters, icon: faBook },
              { label: 'Issues', data: summaryData.issues, icon: faBug },
              { label: 'Releases', data: summaryData.releases, icon: faTag },
            ].map(({ label, data, icon }) => (
              <div
                key={label}
                className="flex items-start gap-4 rounded-lg border p-4 shadow-sm dark:border-gray-700"
              >
                <FontAwesomeIcon icon={icon} className="h-6 w-6 text-blue-500" />
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                    {data.count} {label}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    e.g., {data.examples.join(', ')}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {snapshot?.newChapters && snapshot?.newChapters.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-6 text-2xl font-semibold text-gray-700 dark:text-gray-200">
            New Chapters
          </h2>
          <div className="mb-4">
            <ChapterMapWrapper
              geoLocData={snapshot?.newChapters}
              showLocal={false}
              style={{ height: '400px', width: '100%', zIndex: '0' }}
            />
          </div>
          <div className="flex flex-col gap-6">
            {snapshot?.newChapters.filter((chapter) => chapter.isActive).map(renderChapterCard)}
          </div>
        </div>
      )}

      {snapshot?.newProjects && snapshot?.newProjects.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-4 text-2xl font-semibold text-gray-700 dark:text-gray-200">
            New Projects
          </h2>
          <div className="flex flex-col gap-6">
            {snapshot?.newProjects.filter((project) => project.isActive).map(renderProjectCard)}
          </div>
        </div>
      )}

      {snapshot?.newReleases && snapshot?.newReleases.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-4 text-2xl font-semibold">New Releases</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {snapshot?.newReleases.map((release, index) => (
              <div
                key={`${release.tagName}-${index}`}
                className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
              >
                <div className="p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <div className="truncate text-lg font-medium text-gray-700 dark:text-gray-200">
                      {release.name}
                    </div>
                  </div>
                  <div className="mb-3 flex items-center gap-2">
                    <span className="truncate text-sm font-medium text-gray-700 dark:text-gray-300">
                      {release.projectName}
                    </span>
                    <span className="shrink-0 px-2.5 py-0.5 text-xs font-medium text-gray-500 dark:bg-transparent dark:text-blue-200">
                      {release.tagName}
                    </span>
                  </div>
                  <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                    <FontAwesomeIcon icon={faCalendar} className="mr-1.5 h-3 w-3" />
                    Released: {formatDate(release.publishedAt)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default SnapshotDetailsPage
