import type { User } from 'types/user'

export type Milestone = {
  __typename?: string
  author?: User | null
  body?: string
  closedIssuesCount?: number
  createdAt?: string
  id?: string
  openIssuesCount?: number
  organizationName?: string | null
  progress?: number
  repositoryName?: string | null
  state?: string
  title: string
  url?: string
}
