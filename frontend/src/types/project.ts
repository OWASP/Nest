import { TopContributorsType } from 'types/contributor'

export type Author = {
  avatarUrl: string
  key: string
  login: string
  name: string
}

export interface ProjectIssuesType {
  author: Author
  createdAt: number
  organizationName?: string
  repositoryName?: string
  title: string
  url: string
}

export interface ProjectPullRequestsType {
  author: Author
  createdAt: string
  organizationName: string
  repositoryName?: string
  title: string
  url: string
}

export interface ProjectMilestonesType {
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

export interface ProjectStatsType {
  contributors: number
  forks: number
  issues: number
  repositories: number
  stars: number
}

export interface ProjectBase {
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
  topContributors: TopContributorsType[]
  type: string
  updatedAt: number
  url: string
}

export interface ProjectType extends ProjectBase {
  recentIssues: ProjectIssuesType[]
  recentPullRequests: ProjectPullRequestsType[]
  recentReleases: ProjectReleaseType[]
  repositories: RepositoryCardProps[]
  topContributors: TopContributorsType[]
  recentMilestones: ProjectMilestonesType[]
}

export interface RepositoriesCardProps {
  repositories: RepositoryCardProps[]
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
