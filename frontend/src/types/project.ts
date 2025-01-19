export type project = {
  top_contributors: {
    avatar_url: string
    contributions_count: number
    login: string
    name: string
  }[]
  contributors_count: number
  forks_count: number
  leaders: string[]
  level: string
  name: string
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
