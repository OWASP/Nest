export type user = {
  avatar_url: string
  bio: string
  company: string
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
  commentsCount: number
  createdAt: number
  number: number
  repository: RepositoryDetails
  title: string
}

export type Release = {
  isPreRelease: boolean
  name: string
  publishedAt: number
  repository: RepositoryDetails
  tagName: string
}

export type User = {
  avatar_url: string
  bio?: string | null
  company?: string | null
  created_at: number
  email?: string | null
  followers_count: number
  following_count: number
  issues?: Issue[]
  issues_count?: number
  key: string
  location?: string | null
  login: string
  name?: string | null
  public_repositories_count: number
  releases?: Release[]
  releases_count?: number
  url: string
}

export interface UserDetailsProps {
  name: string
  email?: string
  avatarUrl?: string
  bio?: string
  github?: string
  linkedin?: string
  twitter?: string
  location?: string
  company?: string
}
