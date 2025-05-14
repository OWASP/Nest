import { TopContributorsTypeAlgolia, TopContributorsTypeGraphql } from './contributor'

export interface ProjectDataType {
  active_projects_count: number
  total_pages: number
  projects: ProjectTypeAlgolia[]
}

export interface ProjectIssuesType {
  author: { avatarUrl: string; key: string; name: string }
  createdAt: number
  organizationName?: string
  repositoryName?: string
  title: string
  url: string
}

export interface ProjectPullRequestsType {
  author: {
    avatarUrl: string
    key: string
    name: string
    login: string
  }
  createdAt: string
  organizationName: string
  repositoryName?: string
  title: string
  url: string
}

export interface ProjectStatsType {
  contributors: number
  forks: number
  issues: number
  repositories: number
  stars: number
}

export interface ProjectTypeAlgolia {
  contributors_count: number
  description: string
  forks_count: number
  is_active: boolean
  issues_count: number
  key: string
  languages: string[]
  leaders: string[]
  level: string
  name: string
  objectID: string
  organizations: string
  repositories_count: number
  stars_count: number
  summary: string
  topics: string[]
  top_contributors: TopContributorsTypeAlgolia[]
  type: string
  updated_at: number
  url: string
}

export interface ProjectTypeGraphql {
  contributorsCount: number
  forksCount: number
  isActive: boolean
  issuesCount: number
  key: string
  languages: string[]
  leaders: string[]
  level: string
  name: string
  repositoriesCount: number
  starsCount: number
  summary: string
  topics: string[]
  type: string
  updatedAt: number
  url: string
  recentIssues: ProjectIssuesType[]
  recentPullRequests: ProjectPullRequestsType[]
  recentReleases: ProjectReleaseType[]
  repositories: RepositoryCardProps[]
  topContributors: TopContributorsTypeGraphql[]
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
  author: {
    avatarUrl: string
    key: string
    login: string
    name: string
  }
  isPreRelease: boolean
  name: string
  organizationName?: string
  publishedAt: number
  repositoryName: string
  tagName: string
  url: string
}
