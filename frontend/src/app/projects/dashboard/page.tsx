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
import { useState, useEffect } from 'react'
import React from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROJECT_HEALTH_STATS } from 'server/queries/projectsHealthDashboardQueries'
import type { ProjectHealthStats } from 'types/projectHealthStats'
import DashboardCard from 'components/DashboardCard'
import DonutBarChart from 'components/DonutBarChart'
import LineChart from 'components/LineChart'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const ProjectsDashboardPage: React.FC = () => {
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
  return (
    <>
      <h1 className="font-semibold">Project Health Dashboard Overview</h1>
      <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
        <SecondaryCard
          title="Healthy Projects"
          icon={faCheck}
          className="bg-green-100 bg-opacity-30 text-green-800 transition-colors duration-300 hover:bg-green-200 dark:bg-green-800 dark:bg-opacity-30 dark:text-green-400 dark:hover:bg-green-700"
        >
          <p className="text-3xl font-bold">{stats.projectsCountHealthy}</p>
        </SecondaryCard>
        <SecondaryCard
          title="Projects Needing Attention"
          icon={faWarning}
          className="bg-yellow-100 bg-opacity-30 text-yellow-800 transition-colors duration-300 hover:bg-yellow-200 dark:bg-yellow-800 dark:bg-opacity-30 dark:text-yellow-400 dark:hover:bg-yellow-700"
        >
          <p className="text-3xl font-bold">{stats.projectsCountNeedAttention}</p>
        </SecondaryCard>
        <SecondaryCard
          title="Unhealthy Projects"
          icon={faRectangleXmark}
          className="bg-red-100 bg-opacity-30 text-red-800 transition-colors duration-300 hover:bg-red-200 dark:bg-red-800 dark:bg-opacity-30 dark:text-red-400 dark:hover:bg-red-700"
        >
          <p className="text-3xl font-bold">{stats.projectsCountUnhealthy}</p>
        </SecondaryCard>
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
