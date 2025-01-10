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
  idx_key: string
  objectID: string
}
export interface ProjectDataType {
  active_projects_count: number
  projects: project[]
  total_pages: number
}
