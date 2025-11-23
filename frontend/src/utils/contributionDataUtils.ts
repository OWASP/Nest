/**
 * Utility functions for handling contribution data in both legacy and new formats
 */

export interface ContributionStats {
  commits: number
  pullRequests: number
  issues: number
  releases?: number
  total: number
}

/**
 * Gets contribution statistics with fallback for legacy data
 * @param contributionStats - New detailed stats from API
 * @param contributionData - Legacy heatmap data
 * @returns ContributionStats object with proper fallbacks
 */
export function getContributionStats(
  contributionStats?: ContributionStats,
  contributionData?: Record<string, number>
): ContributionStats | undefined {
  // If we have the new detailed stats, use them
  if (contributionStats) {
    return contributionStats
  }

  // If we only have legacy heatmap data, show total with zeros for breakdown
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

  // No data available
  return undefined
}

/**
 * Checks if detailed contribution breakdown is available
 * @param stats - ContributionStats object
 * @returns true if breakdown data is available (not just total)
 */
export function hasDetailedBreakdown(stats?: ContributionStats): boolean {
  if (!stats) return false

  // If any individual stat is greater than 0, we have detailed data
  return (
    stats.commits > 0 || stats.pullRequests > 0 || stats.issues > 0 || (stats.releases || 0) > 0
  )
}

/**
 * Formats contribution stats for display with proper fallback messaging
 * @param stats - ContributionStats object
 * @returns object with formatted values and metadata
 */
export function formatContributionStats(stats?: ContributionStats) {
  const hasBreakdown = hasDetailedBreakdown(stats)

  return {
    stats: stats || { commits: 0, pullRequests: 0, issues: 0, releases: 0, total: 0 },
    hasBreakdown,
    isLegacyData: stats ? stats.total > 0 && !hasBreakdown : false,
  }
}
