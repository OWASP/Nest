import { TopContributorsType } from './contributor'

export interface ProjectStatsType {
  contributors: number
  forks: number
  issues: number
  repositories: number
  stars: number
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

export interface RepositoriesCardProps {
  repositories: RepositoryCardProps[]
}

export interface Project {
  contributorsCount: number
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
  type: string
  updatedAt: number
  url: string
  recentIssues: ProjectIssuesType[]
  recentReleases: ProjectReleaseType[]
  repositories: RepositoryCardProps[]
  topContributors: TopContributorsType[]
}

export interface ProjectDataType {
  active_projects_count: number
  projects: Project[]
  total_pages: number
}

export interface ProjectIssuesType {
  author: { avatarUrl: string; key: string; name: string }
  commentsCount: number
  createdAt: string
  number: number
  repository: { key: string; owner_key: string }
  title: string
}

export type ProjectReleaseType = {
  author: {
    avatarUrl: string
    key: string
    name: string
  }
  isPreRelease: boolean
  name: string
  publishedAt: number
  repository: {
    key: string
    owner_key: string
  }
  tagName: string
}
