import type { User } from 'types/user'

export type Certificate = {
  id: string
  githubUser: User
  issuedAt: string
  isVerified: boolean
  score: number
  tier: string
}
