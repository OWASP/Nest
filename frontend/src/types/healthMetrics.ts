export type HealthMetricsProps = {
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

export type ApexChartLabelSeries = {
  name: string
  data: number[]
}
