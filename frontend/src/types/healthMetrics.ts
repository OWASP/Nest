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

export type ApexChartLabelSeries = {
  name: string
  data: number[]
}
