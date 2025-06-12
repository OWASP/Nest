import type { User } from 'types/user'

export type ReleaseType = {
  author: User
  isPreRelease: boolean
  name: string
  organizationName?: string
  projectName?: string
  publishedAt: number
  repositoryName: string
  tagName: string
  url: string
}
