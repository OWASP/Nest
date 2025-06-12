import { User } from 'types/user'

export type MilestonesType = {
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
