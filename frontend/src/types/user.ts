import type { IssueType } from 'types/issue'
import type { RepositoryCardProps } from 'types/project'
import { ReleaseType } from 'types/release'

export type RepositoryDetails = {
  key: string
  ownerKey: string
}

export type UserType<T = number> = {
  createdAt: T
  avatarUrl: string
  followersCount: number
  followingCount: number
  issues?: IssueType[]
  key: string
  login: string
  publicRepositoriesCount: number
  releases?: ReleaseType[]
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

export type User = UserType<number>

export type UserDetails = UserType<string>
