import { TopContributors } from 'types/contributor'

export type Author = {
  avatarUrl: string
  key: string
  login: string
  name: string
}

export type ProjectIssuesType = {
  author: Author
  createdAt: number
  organizationName?: string
  repositoryName?: string
  title: string
  url: string
}

export type ProjectPullRequestsType = {
  author: Author
  createdAt: string
  organizationName: string
  repositoryName?: string
  title: string
  url: string
}

export type ProjectMilestonesType = {
  author: Author
  body: string
  closedIssuesCount: number
  createdAt: string
  openIssuesCount: number
  organizationName?: string
  progress?: number
  repositoryName: string
  state: string
  title: string
  url?: string
}

export type ProjectStatsType = {
  contributors: number
  forks: number
  issues: number
  repositories: number
  stars: number
}

export interface ProjectType {
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
  organizations: string
  repositoriesCount: number
  starsCount: number
  summary: string
  topics: string[]
  topContributors: TopContributors[]
  type: string
  updatedAt: number
  url: string
  recentIssues?: ProjectIssuesType[]
  recentPullRequests?: ProjectPullRequestsType[]
  recentReleases?: ProjectReleaseType[]
  repositories?: RepositoryCardProps[]
  recentMilestones?: ProjectMilestonesType[]
}

export interface RepositoriesCardProps {
  repositories?: RepositoryCardProps[]
}

export interface RepositoryCardProps {
  contributorsCount: number
  forksCount: number
  key?: string
  name: string
  openIssuesCount: number
  organization?: {
    login: string
  }
  starsCount: number
  subscribersCount: number
  url: string
}

export type ProjectReleaseType = {
  author: Author
  isPreRelease: boolean
  name: string
  organizationName?: string
  publishedAt: number
  repositoryName: string
  tagName: string
  url: string
}
