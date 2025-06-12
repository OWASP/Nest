import type { RepositoryDetails, User } from 'types/user'

export type IssuesDataType = {
  issues: IssueType[]
  open_issues_count: number
  total_pages: number
}

export type IssueType = {
  author: User
  createdAt: number
  hint: string
  labels: string[]
  number?: string
  organizationName?: string
  projectName: string
  projectUrl: string
  repository?: RepositoryDetails
  repositoryLanguages: string[]
  summary: string
  title: string
  updatedAt: number
  url: string
  objectID: string
}
