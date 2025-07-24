export type ExtendedProfile = {
  login: string
}

export type ExtendedSession = {
  accessToken?: string
  user?: {
    login?: string
  }
}
