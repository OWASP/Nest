export type HealthMetricsProps = {
  forksCount: number
  lastCommitDays: number
  lastReleaseDays: number
  openIssuesCount: number
  openPullRequestsCount: number
  score: number
  starsCount: number
  unassignedIssuesCount: number
  unansweredIssuesCount: number
}

export type ApexChartSeries = {
  name: string
  data: number[]
}
