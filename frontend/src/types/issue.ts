import type { PullRequest } from 'types/pullRequest'
import type { RepositoryDetails, User } from 'types/user'

export type Issue = {
  author: User
  createdAt: number
  hint: string
  labels: string[]
  number?: string
  organizationName?: string
  projectName: string
  projectUrl: string
  pullRequests?: PullRequest[]
  repository?: RepositoryDetails
  repositoryLanguages?: string[]
  body: string
  title: string
  updatedAt: number
  url: string
  objectID: string
}
