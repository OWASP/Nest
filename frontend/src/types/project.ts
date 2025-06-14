import type { Contributor } from 'types/contributor'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { Organization } from 'types/organization'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'

export type ProjectStats = {
  contributors: number
  forks: number
  issues: number
  repositories: number
  stars: number
}

export type Project = {
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
  topContributors: Contributor[]
  type: string
  updatedAt: number
  url: string
  recentIssues?: Issue[]
  recentPullRequests?: PullRequest[]
  recentReleases?: Release[]
  repositories?: RepositoryCardProps[]
  recentMilestones?: Milestone[]
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
  organization?: Organization
  starsCount: number
  subscribersCount: number
  url: string
}
