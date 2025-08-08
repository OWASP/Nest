export type ExtendedProfile = {
  login: string
}

export type ExtendedSession = {
  accessToken?: string
  expires?: string
  user?: {
    email?: string
    image?: string
    isOwaspStaff?: boolean
    name?: string
    login?: string
  }
}
