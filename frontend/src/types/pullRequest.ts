import type { User } from 'types/user'

export type PullRequest = {
  author?: User | null
  createdAt: string
  id?: string
  mergedAt?: string
  organizationName?: string | null
  repositoryName?: string | null
  state?: string
  title: string
  url: string
}
