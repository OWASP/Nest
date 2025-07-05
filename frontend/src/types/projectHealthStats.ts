export type ProjectHealthStats = {
  averageScore: number
  monthlyOverallScores: number[]
  monthlyOverallScoresMonths: number[]
  projectsCountHealthy: number
  projectsCountNeedAttention: number
  projectsCountUnhealthy: number
  projectsPercentageHealthy: number
  projectsPercentageNeedAttention: number
  projectsPercentageUnhealthy: number
  totalContributors: number
  totalForks: number
  totalStars: number
}
