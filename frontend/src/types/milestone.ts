import type { User } from 'types/user'

export type Milestone = {
  author?: User | null
  body?: string
  closedIssuesCount?: number
  createdAt?: string
  openIssuesCount?: number
  organizationName?: string | null
  progress?: number
  repositoryName?: string | null
  state?: string
  title: string
  url?: string
}
