import { topContributorsType } from './contributor'

export interface project {
  top_contributors: topContributorsType[]
  contributors_count: number
  forks_count: number
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

export interface ProjectStatsType {
  Contributors: number
  Forks: number
  Stars: number
  Repositories: number
}

export interface ProjectIssuesType {
  createdAt: string
  commentsCount: number
  number: number
  repository: { key: string; owner_key: string }
  title: string
  author: { avatar_url: string; key: string; name: string }
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
