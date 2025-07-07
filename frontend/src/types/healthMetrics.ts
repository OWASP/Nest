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
  forksCount: number
  lastCommitDays: number
  lastCommitDaysRequirement: number
  lastReleaseDays: number
  lastReleaseDaysRequirement: number
  openIssuesCount: number
  openPullRequestsCount: number
  score: number
  starsCount: number
  unassignedIssuesCount: number
  unansweredIssuesCount: number
}
