import { parseISO } from 'date-fns/parseISO'

export interface ContributionStats {
  commits: number
  pullRequests: number
  issues: number
  releases?: number
  total: number
  startAt?: string
  endAt?: string
}

const DATE_ONLY = /^\d{4}-\d{2}-\d{2}$/
const TIMESTAMP_WITH_ZONE =
  /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)$/

/** Parse valid calendar dates or timestamps with an explicit timezone; reject other values. */
const parseContributionDate = (value: unknown): Date | undefined => {
  // Timestamps need an explicit timezone; date-only values represent UTC days.
  if (typeof value !== 'string' || !(DATE_ONLY.test(value) || TIMESTAMP_WITH_ZONE.test(value))) {
    return undefined
  }
  const parsed = parseISO(value.length === 10 ? `${value}T00:00:00Z` : value)
  return Number.isNaN(parsed.getTime()) ? undefined : parsed
}

/** Prefer a valid saved UTC period, then daily-date bounds; return nothing without usable dates. */
export function getContributionDateRange(
  stats?: ContributionStats,
  contributionData?: Record<string, number>
): { startDate: string; endDate: string } | undefined {
  const start = parseContributionDate(stats?.startAt)
  const end = parseContributionDate(stats?.endAt)
  if (start && end && start <= end) {
    return {
      startDate: start.toISOString().slice(0, 10),
      endDate: end.toISOString().slice(0, 10),
    }
  }
  let startDate: string | undefined
  let endDate: string | undefined
  for (const day of Object.keys(contributionData ?? {})) {
    if (day.length !== 10 || !parseContributionDate(day)) continue
    if (!startDate || day < startDate) startDate = day
    if (!endDate || day > endDate) endDate = day
  }
  return startDate && endDate ? { startDate, endDate } : undefined
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
      issues: 0,
      pullRequests: 0,
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

/**
 * Count contributions for an entity key, trying the legacy www- prefix when needed.
 */
export function contributionCount(
  contributions: Record<string, number> | undefined,
  key: string,
  legacyPrefix: string
): number {
  if (!contributions) {
    return 0
  }
  if (Object.hasOwn(contributions, key)) {
    return contributions[key]
  }
  const alternate = key.toLowerCase().startsWith(legacyPrefix)
    ? key.slice(legacyPrefix.length)
    : `${legacyPrefix}${key}`
  if (Object.hasOwn(contributions, alternate)) {
    return contributions[alternate]
  }
  return 0
}
