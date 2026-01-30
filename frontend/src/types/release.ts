import type { RepositoryDetails, User } from 'types/user'

export type Release = {
  author?: User | null
  id: string
  isPreRelease?: boolean
  name: string
  organizationName?: string | null
  projectName?: string | null
  publishedAt: number
  repository?: RepositoryDetails
  repositoryName: string | null
  tagName: string
}
