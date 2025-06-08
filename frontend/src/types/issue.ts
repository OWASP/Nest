export type IssuesDataType = {
  issues: IssueType[]
  open_issues_count: number
  total_pages: number
}

export interface IssueType {
  createdAt: number
  hint: string
  labels: string[]
  projectName: string
  projectUrl: string
  repositoryLanguages: string[]
  summary: string
  title: string
  updatedAt: number
  url: string
  objectID: string
}
