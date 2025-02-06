import { topContributorsType } from './contributor'

export interface project {
  contributors_count: number
  description: string
  forks_count: number
  issues_count: number
  is_active: boolean
  languages: string[]
  leaders: string[]
  level: string
  name: string
  organizations: string
  repositories_count: number
  stars_count: number
  summary: string
  topics: string[]
  top_contributors: topContributorsType[]
  type: string
  updated_at: number
  url: string
  key: string
  objectID: string
}
export interface ProjectDataType {
  active_projects_count: number
  projects: project[]
  total_pages: number
}

export interface ProjectIssuesType {
  author: { avatar_url: string; key: string; name: string }
  commentsCount: number
  createdAt: string
  number: number
  repository: { key: string; owner_key: string }
  title: string
}

export type ProjectReleaseType = {
  author: {
    avatar_url: string
    key: string
    name: string
  }
  is_pre_release: boolean
  name: string
  published_at: number
  repository: {
    key: string
    owner_key: string
  }
  tag_name: string
}

export type RepositoryCardProps = {
  contributorsCount: number
  forksCount: number
  name: string
  key: string
  openIssuesCount: number
  starsCount: number
  subscribersCount: number
}

export interface RepositoriesCardProps {
  repositories: RepositoryCardProps[]
}
