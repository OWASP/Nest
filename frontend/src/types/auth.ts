import type { Session } from 'next-auth'

export type ExtendedProfile = {
  isLeader?: boolean
  login: string
}

export type ExtendedSession = Session & {
  accessToken?: string
  user?: Session['user'] & {
    isLeader?: boolean
    login?: string
  }
}

export type UserRolesData = {
  currentUserRoles: {
    roles: string[]
  }
}
