import type { User } from 'types/user'

export type Milestone = {
  author: User
  body: string
  closedIssuesCount: number
  createdAt: string
  openIssuesCount: number
  organizationName?: string
  progress?: number
  repositoryName: string
  state: string
  title: string
  url?: string
}
