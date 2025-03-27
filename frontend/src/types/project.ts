import { TopContributorsTypeAlgolia, TopContributorsTypeGraphql } from './contributor'

export interface ProjectDataType {
  active_projects_count: number
  total_pages: number
  projects: ProjectTypeAlgolia[]
}

export interface ProjectIssuesType {
  author: { avatarUrl: string; key: string; name: string }
  commentsCount: number
  createdAt: number
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
  name: string
  openIssuesCount: number
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
  publishedAt: number
  tagName: string
  url: string
}
