import type { User } from 'types/user'

export type PullRequestType = {
  author: User
  createdAt: string
  organizationName: string
  repositoryName?: string
  title: string
  url: string
}
