import { RepositoryCardProps } from 'types/project'

export type RepositoryDetails = {
  key: string
  ownerKey: string
}

export type Issue = {
  createdAt: number
  number: number
  repository: RepositoryDetails
  title: string
  url: string
}

export type Release = {
  isPreRelease: boolean
  name: string
  publishedAt: number
  repository: RepositoryDetails
  tagName: string
  url: string
}

export interface UserType<T = number> {
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

export type User = UserType<number>

export type UserDetails = UserType<string>

export type PullRequestsType = {
  createdAt: string
  organizationName: string
  repositoryName?: string
  title: string
  url: string
}

export type ItemCardPullRequests = {
  createdAt: string
  title: string
  author: {
    login: string
    avatarUrl: string
    key: string
    name: string
  }
  organizationName: string
  url: string
}
