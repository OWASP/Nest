export type user = {
  idx_email: string
  idx_login: string
  idx_name: string
  idx_company: string
  idx_location: string
  idx_bio: string
  idx_followers_count: number
  idx_created_at: number
  idx_avatar_url: string
  idx_following_count: number
  idx_key: string
  idx_public_repositories_count: number
  idx_title: string
  idx_updated_at: number
  idx_url: string
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
