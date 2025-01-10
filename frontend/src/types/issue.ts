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
