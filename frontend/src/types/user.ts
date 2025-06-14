import type { Issue } from 'types/issue'
import type { RepositoryCardProps } from 'types/project'
import type { Release } from 'types/release'

export type RepositoryDetails = {
  key: string
  ownerKey: string
}

export type User<T = number> = {
  createdAt: T
  avatarUrl: string
  followersCount: number
  followingCount: number
  issues?: Issue[]
  key: string
  login: string
  publicRepositoriesCount: number
  releases?: Release[]
  url: string
  contributionsCount: number
  issuesCount?: number
  releasesCount?: number
  location?: string
  company?: string
  bio?: string
  email?: string
  name?: string
  topRepositories?: RepositoryCardProps[]
}

export type UserDetails = User<string>
