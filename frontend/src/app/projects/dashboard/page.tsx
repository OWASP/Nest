'use client'
import { useQuery } from '@apollo/client/react'
import type { IconProp } from '@fortawesome/fontawesome-svg-core'
import {
  faCheck,
  faWarning,
  faRectangleXmark,
  faChartLine,
  faUsers,
  faStar,
  faCodeBranch,
  faChartColumn,
  faHeart,
} from '@fortawesome/free-solid-svg-icons'
import millify from 'millify'
import { useState, useEffect, FC } from 'react'
import { handleAppError } from 'app/global-error'
import { GetProjectHealthStatsDocument } from 'types/__generated__/projectsHealthDashboardQueries.generated'
import type { ProjectHealthStats } from 'types/projectHealthStats'
import DashboardCard from 'components/DashboardCard'
import DonutBarChart from 'components/DonutBarChart'
import LineChart from 'components/LineChart'
import LoadingSpinner from 'components/LoadingSpinner'
import MetricsPDFButton from 'components/MetricsPDFButton'
import ProjectTypeDashboardCard from 'components/ProjectTypeDashboardCard'

const ProjectsDashboardPage: FC = () => {
  const [stats, setStats] = useState<ProjectHealthStats>()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const { data, error: graphQLRequestError } = useQuery(GetProjectHealthStatsDocument)

  useEffect(() => {
    if (data) {
      setStats(data.projectHealthStats)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [data, graphQLRequestError])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!stats) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-lg text-gray-500">No project health data available</p>
      </div>
    )
  }
  const projectsCardsItems: {
    type: 'healthy' | 'needsAttention' | 'unhealthy'
    count: number
    icon: IconProp
  }[] = [
    {
      type: 'healthy',
      count: stats.projectsCountHealthy,
      icon: faCheck,
    },
    {
      type: 'needsAttention',
      count: stats.projectsCountNeedAttention,
      icon: faWarning,
    },
    {
      type: 'unhealthy',
      count: stats.projectsCountUnhealthy,
      icon: faRectangleXmark,
    },
  ]
  const dashboardCardsItems = [
    {
      title: 'Average Score',
      icon: faChartLine,
      stats: `${stats.averageScore.toFixed(1)}`,
    },
    {
      title: 'Contributors',
      icon: faUsers,
      stats: millify(stats.totalContributors),
    },
    {
      title: 'Forks',
      icon: faCodeBranch,
      stats: millify(stats.totalForks),
    },
    {
      title: 'Stars',
      icon: faStar,
      stats: millify(stats.totalStars),
    },
  ]
  return (
    <>
      <div className="mb-4 flex items-center justify-start">
        <h1 className="font-semibold">Project Health Dashboard Overview</h1>
        <MetricsPDFButton path="overview/pdf" fileName="owasp-project-health-metrics-overview" />
      </div>
      <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
        {projectsCardsItems.map((item) => (
          <ProjectTypeDashboardCard
            key={item.type}
            type={item.type}
            count={item.count}
            icon={item.icon}
          />
        ))}
      </div>
      <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-4">
        {dashboardCardsItems.map((item) => (
          <DashboardCard key={item.title} title={item.title} icon={item.icon} stats={item.stats} />
        ))}
      </div>
      <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-[2fr_1fr]">
        <LineChart
          title="Overall Project Health Monthly Trend"
          icon={faChartColumn}
          series={[
            {
              name: 'Project Health Score',
              data: stats.monthlyOverallScores,
            },
          ]}
          labels={stats.monthlyOverallScoresMonths.map((month) => {
            const date = new Date(2025, month - 1, 1)
            return date.toLocaleString('default', { month: 'short' })
          })}
        />
        <DonutBarChart
          title="Project Health Distribution"
          icon={faHeart}
          series={[
            stats.projectsPercentageHealthy,
            stats.projectsPercentageNeedAttention,
            stats.projectsPercentageUnhealthy,
          ]}
        />
      </div>
    </>
  )
}

export default ProjectsDashboardPage
