import type { RepositoryDetails, User } from 'types/user'

export type Release = {
  __typename?: string
  author?: User | null
  id: string
  isPreRelease?: boolean
  name: string
  organizationName?: string | null
  projectName?: string
  publishedAt: number
  repository?: RepositoryDetails
  repositoryName?: string | null
  tagName: string
  url?: string
}
