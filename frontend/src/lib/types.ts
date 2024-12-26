export interface ProjectDataType {
  active_projects_count: number
  projects: project[]
  total_pages: number
}

export type project = {
  idx_top_contributors: {
    avatar_url: string
    contributions_count: number
    login: string
    name: string
  }[]
  idx_contributors_count: number
  idx_forks_count: number
  idx_leaders: string[]
  idx_level: string
  idx_name: string
  idx_stars_count: number
  idx_summary: string
  idx_topics: string[]
  idx_type: string
  idx_updated_at: number
  idx_url: string
  objectID: string
}

export interface IssuesDataType {
  issues: IssueType[]
  open_issues_count: number
  total_pages: number
}

export interface IssueType {
  idx_comments_count: number
  idx_created_at: number
  idx_hint: string
  idx_labels: string[]
  idx_project_name: string
  idx_project_url: string
  idx_repository_languages: string[]
  idx_summary: string
  idx_title: string
  idx_updated_at: number
  idx_url: string
  objectID: string
}

export interface ChapterType {
  idx_created_at: number
  idx_leaders: string[]
  idx_name: string
  idx_related_urls: string[]
  idx_top_contributors: {
    avatar_url: string
    contributions_count: number
    login: string
    name: string
  }[]
  idx_summary: string
  idx_updated_at: number
  idx_url: string
  objectID: string
}

export interface ChapterDataType {
  active_committees_count: number
  chapters: ChapterType[]
  total_pages: number
}

export interface CommitteeType {
  idx_created_at: number
  idx_leaders: string[]
  idx_name: string
  idx_related_urls: string[]
  idx_top_contributors: {
    avatar_url: string
    contributions_count: number
    login: string
    name: string
  }[]
  idx_summary: string
  idx_updated_at: number
  idx_url: string
  objectID: string
}

export interface CommitteeDataType {
  active_committees_count: number
  committees: CommitteeType[]
  total_pages: number
}

export interface AlgoliaResponseType<T> {
  hits: T[]
  totalPages: number
}

export type ErrorSource = 'algolia' | 'runtime' | 'network' | 'http' | 'routing'

export interface ErrorConfig {
  code: string
  statusCode?: number
  title: string
  message: string
  source: ErrorSource
  action?: 'retry' | 'home'
  technical?: string
}
