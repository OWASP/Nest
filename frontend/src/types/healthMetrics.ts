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
  createdAt: string
  contributorsCount: number
  forksCount: number
  isFundingRequirementsCompliant: boolean
  isLeaderRequirementsCompliant: boolean
  lastCommitDays: number
  lastCommitDaysRequirement: number
  lastReleaseDays: number
  lastReleaseDaysRequirement: number
  openIssuesCount: number
  openPullRequestsCount: number
  owaspPageLastUpdateDays: number
  projectName: string
  recentReleasesCount: number
  score: number
  starsCount: number
  totalIssuesCount: number
  totalReleasesCount: number
  unassignedIssuesCount: number
  unansweredIssuesCount: number
}
