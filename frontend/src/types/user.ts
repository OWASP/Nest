import { RepositoryCardProps } from 'types/project'

export interface user {
  avatar_url: string
  bio: string
  company: string
  contributions_count: number
  created_at: number
  email: string
  followers_count: number
  following_count: number
  key: string
  location: string
  login: string
  name: string
  objectID: string
  public_repositories_count: number
}

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

export interface UserBase<T = number> {
  createdAt: T
  avatarUrl: string
  bio?: string | null
  company?: string | null
  email?: string | null
  followersCount: number
  followingCount: number
  issues?: Issue[]
  issuesCount?: number
  key: string
  location?: string | null
  login: string
  name?: string | null
  publicRepositoriesCount: number
  releases?: Release[]
  releasesCount?: number
  url: string
  contributionsCount: number
}

export type User = UserBase<number>

export interface UserDetailsProps extends UserBase<string> {
  issuesCount: number
  releasesCount: number
  location: string | null
  company: string | null
  bio: string | null
  email: string | null
  name: string | null
  topRepositories: RepositoryCardProps[]
}

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
