import type { RepositoryDetails, User } from 'types/user'

export type ReleaseType = {
  author: User
  isPreRelease: boolean
  name: string
  organizationName?: string
  projectName?: string
  publishedAt: number
  repository?: RepositoryDetails
  repositoryName: string
  tagName: string
  url: string
}
