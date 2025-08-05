export type ExtendedProfile = {
  login: string
}

export type ExtendedSession = {
  accessToken?: string
  user?: {
    isOwaspStaff?: boolean
    login?: string
  }
}
