export type ExtendedSession = {
  accessToken?: string
  user?: {
    login?: string
  }
}

export type UserRolesData = {
  currentUserRoles: {
    roles: string[]
  }
}
