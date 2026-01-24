import type { Session } from 'next-auth'

export type ExtendedProfile = {
  isLeader?: boolean
  login: string
}

export type ExtendedSession = Session & {
  accessToken?: string
  user?: Session['user'] & {
    email?: string
    expires?: string
    image?: string
    isLeader?: boolean
    isMentor?: boolean
    isOwaspStaff?: boolean
    login?: string
    name?: string
  }
}
