'use client'
import { useQuery } from '@apollo/client/react'
import millify from 'millify'
import { useState, useEffect, FC } from 'react'
import type { IconType } from 'react-icons'
import {
  FaCheck,
  FaTriangleExclamation,
  FaRectangleXmark,
  FaChartLine,
  FaStar,
  FaCodeBranch,
  FaChartColumn,
  FaHeart,
} from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
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
  const {
    data,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetProjectHealthStatsDocument)

  useEffect(() => {
    if (data) {
      setStats(data.projectHealthStats)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
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
    icon: IconType
  }[] = [
    {
      type: 'healthy',
      count: stats.projectsCountHealthy,
      icon: FaCheck,
    },
    {
      type: 'needsAttention',
      count: stats.projectsCountNeedAttention,
      icon: FaTriangleExclamation,
    },
    {
      type: 'unhealthy',
      count: stats.projectsCountUnhealthy,
      icon: FaRectangleXmark,
    },
  ]
  const dashboardCardsItems: {
    title: string
    icon: IconType
    stats?: string
  }[] = [
    {
      title: 'Average Score',
      icon: FaChartLine,
      stats: `${stats.averageScore.toFixed(1)}`,
    },
    {
      title: 'Contributors',
      icon: HiUserGroup,
      stats: millify(stats.totalContributors),
    },
    {
      title: 'Forks',
      icon: FaCodeBranch,
      stats: millify(stats.totalForks),
    },
    {
      title: 'Stars',
      icon: FaStar,
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
          icon={FaChartColumn}
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
          icon={FaHeart}
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
