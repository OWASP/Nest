export type ExtendedProfile = {
  isLeader?: boolean
  login: string
}

export type ExtendedSession = {
  accessToken?: string
  user?: {
    isLeader?: boolean
    login?: string
  }
}

export type UserRolesData = {
  currentUserRoles: {
    roles: string[]
  }
}
