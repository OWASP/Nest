import type { User } from 'types/user'

export type PullRequest = {
  id?: string
  author?: User
  createdAt: string | number
  organizationName?: string | null
  repositoryName?: string | null
  title: string
  url: string
  state?: string
  mergedAt?: string
}
