import type { TopContributors } from 'types/contributor'
import type { IssueType } from 'types/issue'
import { MilestonesType } from 'types/milestone'
import { OrganizationType } from 'types/organization'
import { PullRequestType } from 'types/pullRequest'
import type { ReleaseType } from 'types/release'

export type ProjectStatsType = {
  contributors: number
  forks: number
  issues: number
  repositories: number
  stars: number
}

export type ProjectType = {
  createdAt?: string
  contributorsCount: number
  description: string
  forksCount: number
  isActive: boolean
  issuesCount: number
  key: string
  languages: string[]
  leaders: string[]
  level: string
  name: string
  openIssuesCount?: number
  organizations: string
  repositoriesCount: number
  starsCount: number
  summary: string
  topics: string[]
  topContributors: TopContributors[]
  type: string
  updatedAt: number
  url: string
  recentIssues?: IssueType[]
  recentPullRequests?: PullRequestType[]
  recentReleases?: ReleaseType[]
  repositories?: RepositoryCardProps[]
  recentMilestones?: MilestonesType[]
}

export type RepositoriesCardProps = {
  repositories?: RepositoryCardProps[]
}

export type RepositoryCardProps = {
  contributorsCount: number
  forksCount: number
  key?: string
  name: string
  openIssuesCount: number
  organization?: OrganizationType
  starsCount: number
  subscribersCount: number
  url: string
}
