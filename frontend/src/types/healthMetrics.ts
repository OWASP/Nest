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
  id: string
  createdAt: string
  contributorsCount: number
  forksCount: number
  lastCommitDays: number
  lastCommitDaysRequirement: number
  lastReleaseDays: number
  lastReleaseDaysRequirement: number
  openIssuesCount: number
  openPullRequestsCount: number
  projectName: string
  projectKey: string
  score: number
  starsCount: number
  unassignedIssuesCount: number
  unansweredIssuesCount: number
}

export type HealthMetricsFilter = {
  score?: {
    gt?: number
    gte?: number
    lt?: number
    lte?: number
  }
  level?: string
}

export type HealthMetricsOrdering = {
  scoreOrdering?: {
    score: 'ASC' | 'DESC'
  }
  starsCountOrdering?: {
    starsCount: 'ASC' | 'DESC'
  }
  forksCountOrdering?: {
    forksCount: 'ASC' | 'DESC'
  }
  contributorsCountOrdering?: {
    contributorsCount: 'ASC' | 'DESC'
  }
}
