import type { PullRequest } from 'types/pullRequest'
import type { RepositoryDetails, User } from 'types/user'

export type Issue = {
  author?: User
  createdAt: string | number
  hint?: string
  labels?: string[]
  number?: string | number
  organizationName?: string | null
  repositoryName?: string | null
  projectName?: string
  projectUrl?: string
  pullRequests?: PullRequest[]
  repository?: RepositoryDetails
  repositoryLanguages?: string[]
  body?: string
  title: string
  state?: string
  summary?: string
  updatedAt?: string | number
  url: string
  objectID?: string
}
