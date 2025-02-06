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
  title: string
  updated_at: number
  url: string
}

export interface UserDetailsProps {
  avatarUrl: string
  bio: string
  company: string
  createdAt: string
  email: string
  followersCount: number
  followingCount: number
  location: string
  login: string
  name: string
  publicRepositoriesCount: number
  url: string
}
