export type user = {
  email: string
  login: string
  name: string
  company: string
  location: string
  bio: string
  followers_count: number
  created_at: number
  avatar_url: string
  following_count: number
  key: string
  public_repositories_count: number
  title: string
  updated_at: number
  url: string
  objectID: string
}

export interface UserDetailsProps {
  avatarUrl: string
  bio: string
  company: string
  email: string
  followersCount: number
  followingCount: number
  location: string
  login: string
  name: string
  publicRepositoriesCount: number
  title: string
  url: string
  createdAt: string
  updatedAt: string
}
