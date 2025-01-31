export type RepositoryDetails = {
  key: string
  owner_key: string
}

export type Issue = {
  created_at: number
  comments_count: number
  number: number
  title: string
  repository: RepositoryDetails
}

export type Release = {
  is_pre_release: boolean
  name: string
  published_at: number
  tag_name: string
  repository: RepositoryDetails
}

export type User = {
  email: string
  login: string
  name: string
  company: string
  location: string
  bio: string
  followers_count: number
  following_count: number
  avatar_url: string
  public_repositories_count: number
  title: string
  twitter_username: string
  url: string
  created_at: number
  updated_at: number
  objectID: string
  issues?: Issue[]
  releases?: Release[]
}

export interface UserDetailsProps {
  email: string
  login: string
  name: string
  company: string
  location: string
  bio: string
  followers_count: number
  following_count: number
  avatar_url: string
  public_repositories_count: number
  title: string
  twitter_username: string
  url: string
  created_at: number
  updated_at: number
  objectID: string
  issues?: Issue[]
  releases?: Release[]
}
