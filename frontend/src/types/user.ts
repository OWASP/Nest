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
  avatar_url: string
  bio: string
  company: string
  email: string
  followers_count: number
  following_count: number
  location: string
  login: string
  name: string
  public_repositories_count: number
  title: string
  twitter_username: string
  url: string
  created_at: string
  updated_at: string
}
