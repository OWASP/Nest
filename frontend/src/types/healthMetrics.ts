export type ApexLineChartSeries = {
  name: string
  data: number[]
}

export type ApexBarChartDataSeries = {
  x: string
  y: number
  fill?
  fillColor?: string
  strokeColor?: string
  meta?
  goals?: {
    barHeightOffset?: number
    columnWidthOffset?: number
    name?: string
    value: number
    strokeColor?: string
    strokeDashArray?: number
    strokeHeight?: number
    strokeWidth?: number
    strokeLineCap?: 'butt' | 'round' | 'square'
  }[]
}

export type HealthMetricsProps = {
  ageDays?: number
  ageDaysRequirement?: number
  id: string
  createdAt?: string
  contributorsCount?: number
  forksCount?: number
  isFundingRequirementsCompliant?: boolean
  isLeaderRequirementsCompliant?: boolean
  lastCommitDays?: number
  lastCommitDaysRequirement?: number
  lastPullRequestDays?: number
  lastPullRequestDaysRequirement?: number
  lastReleaseDays?: number
  lastReleaseDaysRequirement?: number
  openIssuesCount?: number
  openPullRequestsCount?: number
  owaspPageLastUpdateDays?: number
  owaspPageLastUpdateDaysRequirement?: number
  projectName?: string
  projectKey?: string
  recentReleasesCount?: number
  score?: number
  starsCount?: number
  totalIssuesCount?: number
  totalReleasesCount?: number
  unassignedIssuesCount?: number
  unansweredIssuesCount?: number
}

export type HealthMetricsFilter = {
  level?: string
  score?: {
    gt?: number
    gte?: number
    lt?: number
    lte?: number
  }
}
