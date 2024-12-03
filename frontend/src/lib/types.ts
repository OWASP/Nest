export interface ProjectDataType {
  active_projects_count: number
  projects: project[]
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
  idx_updated_at: number // UNIX timestamp
  idx_url: string
  objectID: string
}

export interface IssuesDataType {
  issues: IssueType[]
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

export interface ChapterDataType {
  active_chapters_count: number
  chapters: {
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
  }[]
}

export interface CommitteeDataType {
  active_committees_count: number
  committees: {
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
  }[]
}
