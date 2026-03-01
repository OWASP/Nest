import type { Badge } from 'types/badge'
import type { Issue } from 'types/issue'
import type { RepositoryCardProps } from 'types/project'
import type { Release } from 'types/release'

export type RepositoryDetails = {
  key: string
  ownerKey: string
}

export type User = {
  avatarUrl: string
  badgeCount?: number
  badges?: Badge[]
  bio?: string
  company?: string
  contributionsCount?: number
  createdAt?: string
  email?: string
  followersCount?: number
  followingCount?: number
  isOwaspStaff?: boolean
  issues?: Issue[]
  issuesCount?: number
  key?: string
  location?: string
  login: string
  name?: string
  publicRepositoriesCount?: number
  releases?: Release[]
  releasesCount?: number
  topRepositories?: RepositoryCardProps[]
  updatedAt?: string
  url?: string
}
