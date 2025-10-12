import type { User } from 'types/user'

export type PullRequest = {
  id: string
  author: User
  createdAt: string
  organizationName: string
  repositoryName?: string
  title: string
  url: string
  state: string
  mergedAt?: string
}
