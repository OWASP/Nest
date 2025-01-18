export interface IssuesDataType {
  issues: IssueType[]
  open_issues_count: number
  total_pages: number
}

export interface IssueType {
  comments_count: number
  created_at: number
  hint: string
  labels: string[]
  project_name: string
  project_url: string
  repository_languages: string[]
  summary: string
  title: string
  updated_at: number
  url: string
  objectID: string
}
