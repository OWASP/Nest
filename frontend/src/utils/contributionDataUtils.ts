export interface ContributionStats {
  commits: number
  pullRequests: number
  issues: number
  releases?: number
  total: number
}

export function getContributionStats(
  contributionStats?: ContributionStats,
  contributionData?: Record<string, number>
): ContributionStats | undefined {
  if (contributionStats) {
    return contributionStats
  }
  if (contributionData && Object.keys(contributionData).length > 0) {
    const total = Object.values(contributionData).reduce((sum, count) => sum + count, 0)

    return {
      commits: 0,
      pullRequests: 0,
      issues: 0,
      releases: 0,
      total,
    }
  }
  return undefined
}

export function hasDetailedBreakdown(stats?: ContributionStats): boolean {
  if (!stats) return false

  return (
    stats.commits > 0 || stats.pullRequests > 0 || stats.issues > 0 || (stats.releases || 0) > 0
  )
}

export function formatContributionStats(stats?: ContributionStats) {
  const hasBreakdown = hasDetailedBreakdown(stats)

  return {
    stats: stats || { commits: 0, pullRequests: 0, issues: 0, releases: 0, total: 0 },
    hasBreakdown,
    isLegacyData: stats ? stats.total > 0 && !hasBreakdown : false,
  }
}
