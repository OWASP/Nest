'use client'
import { useQuery } from '@apollo/client'
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
import { GET_PROJECT_HEALTH_STATS } from 'server/queries/projectsHealthDashboardQueries'
import type { ProjectHealthStats } from 'types/projectHealthStats'
import DashboardCard from 'components/DashboardCard'
import DonutBarChart from 'components/DonutBarChart'
import LineChart from 'components/LineChart'
import LoadingSpinner from 'components/LoadingSpinner'
import ProjectTypeDashboardCard from 'components/ProjectTypeDashboardCard'

const ProjectsDashboardPage: FC = () => {
  const [stats, setStats] = useState<ProjectHealthStats>()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const { data, error: graphQLRequestError } = useQuery(GET_PROJECT_HEALTH_STATS)

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
  const projectsCardsItems = [
    {
      type: 'healthy',
      count: stats.projectsCountHealthy,
      icon: faCheck,
      color: 'green',
    },
    {
      type: 'needsAttention',
      count: stats.projectsCountNeedAttention,
      icon: faWarning,
      color: 'yellow',
    },
    {
      type: 'unhealthy',
      count: stats.projectsCountUnhealthy,
      icon: faRectangleXmark,
      color: 'red',
    },
  ]
  return (
    <>
      <h1 className="font-semibold">Project Health Dashboard Overview</h1>
      <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
        {projectsCardsItems.map((item) => (
          <ProjectTypeDashboardCard
            key={item.type}
            type={item.type}
            count={item.count}
            icon={item.icon}
            color={item.color}
          />
        ))}
      </div>
      <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-4">
        <DashboardCard
          title="Average Score"
          icon={faChartLine}
          stats={`%${stats.averageScore.toFixed(1)}`}
        />
        <DashboardCard
          title="Total Contributors"
          icon={faUsers}
          stats={millify(stats.totalContributors)}
        />
        <DashboardCard title="Total Forks" icon={faCodeBranch} stats={millify(stats.totalForks)} />
        <DashboardCard title="Total Stars" icon={faStar} stats={millify(stats.totalStars)} />
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
            const date = new Date()
            date.setMonth(month - 1) // Adjust month to 0-indexed
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
