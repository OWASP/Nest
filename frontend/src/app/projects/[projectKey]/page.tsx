'use client'
import { useQuery } from '@apollo/client/react'
import {
  faCodeFork,
  faExclamationCircle,
  faFolderOpen,
  faStar,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import upperFirst from 'lodash/upperFirst'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import { FaCodeFork, FaFolderOpen, FaStar } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetProjectDocument } from 'types/__generated__/projectQueries.generated'
import type { Contributor } from 'types/contributor'
import type { Project } from 'types/project'
import { getContributionStats } from 'utils/contributionDataUtils'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import ContributionHeatmap from 'components/ContributionHeatmap'
import ContributionStats from 'components/ContributionStats'
import LoadingSpinner from 'components/LoadingSpinner'

const ProjectDetailsPage = () => {
  const { projectKey } = useParams<{ projectKey: string }>()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [project, setProject] = useState<Project | null>(null)
  const [topContributors, setTopContributors] = useState<Contributor[]>([])
  const { data, error: graphQLRequestError } = useQuery(GetProjectDocument, {
    variables: { key: projectKey },
  })
  useEffect(() => {
    if (data) {
      setProject(data.project)
      setTopContributors(data.topContributors)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [data, graphQLRequestError, projectKey])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!project)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Project not found"
        message="Sorry, the project you're looking for doesn't exist"
      />
    )
  const projectDetails = [
    { label: 'Last Updated', value: formatDate(project.updatedAt) },
    { label: 'Leaders', value: project.leaders.join(', ') },
    {
      label: 'Level',
      value: upperFirst(project.level),
    },
    { label: 'Type', value: upperFirst(project.type) },
    {
      label: 'URL',
      value: (
        <Link href={project.url} className="hover:underline dark:text-sky-600">
          {project.url}
        </Link>
      ),
    },
  ]
  const projectStats = [
    { icon: FaStar, value: project.starsCount, unit: 'Star' },
    { icon: FaCodeFork, value: project.forksCount, unit: 'Fork' },
    {
      icon: HiUserGroup,
      value: project.contributorsCount,
      unit: 'Contributor',
    },
    {
      icon: FaExclamationCircle,
      value: project.issuesCount,
      unit: 'Issue',
    },
    {
      icon: FaFolderOpen,
      value: project.repositoriesCount,
      unit: 'Repository',
      pluralizedName: 'Repositories',
    },
  ]

  // Calculate contribution heatmap date range (1 year back)
  const today = new Date()
  const oneYearAgo = new Date(today)
  oneYearAgo.setFullYear(today.getFullYear() - 1)
  const startDate = oneYearAgo.toISOString().split('T')[0]
  const endDate = today.toISOString().split('T')[0]

  // Use real contribution stats from API with fallback to legacy data
  const contributionStats = getContributionStats(
    project.contributionStats,
    project.contributionData
  )

  return (
    <>
      <DetailsCard
        details={projectDetails}
        entityKey={project.key}
        entityLeaders={project.entityLeaders}
        healthMetricsData={project.healthMetricsList}
        isActive={project.isActive}
        languages={project.languages}
        pullRequests={project.recentPullRequests}
        recentIssues={project.recentIssues}
        recentMilestones={project.recentMilestones}
        recentReleases={project.recentReleases}
        repositories={project.repositories}
        stats={projectStats}
        summary={project.summary}
        title={project.name}
        topContributors={topContributors}
        topics={project.topics}
        type="project"
      />
      {project.contributionData && Object.keys(project.contributionData).length > 0 && (
        <div className="bg-white pb-10 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
          <div className="mx-auto max-w-6xl">
            <div className="rounded-lg bg-gray-100 px-14 pt-6 shadow-md dark:bg-gray-800">
              <ContributionStats title="Project Contribution Activity" stats={contributionStats} />
              <div className="flex w-full items-center justify-center">
                <ContributionHeatmap
                  contributionData={project.contributionData}
                  startDate={startDate}
                  endDate={endDate}
                  unit="contribution"
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default ProjectDetailsPage
