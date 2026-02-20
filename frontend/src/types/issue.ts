import type { PullRequest } from 'types/pullRequest'
import type { RepositoryDetails, User } from 'types/user'

export type Issue = {
  author?: User
  body?: string
  createdAt: number
  hint?: string
  labels?: string[]
  number?: string | number
  objectID?: string
  organizationName?: string | null
  projectName?: string
  projectUrl?: string
  pullRequests?: PullRequest[]
  repository?: RepositoryDetails
  repositoryLanguages?: string[]
  repositoryName?: string | null
  state?: string
  summary?: string
  title: string
  updatedAt?: number
  url: string
}
