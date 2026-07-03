import type { User } from 'types/user'

export type Certificate = {
  id: string
  tier: string
  issuedAt: string
  score: number
  isVerified: boolean
  githubUser: User
}
