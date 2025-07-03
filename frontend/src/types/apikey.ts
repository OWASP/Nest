export type CreateApiKeyResult = {
  apiKey: ApiKey
  rawKey: string
}

export type ApiKey = {
  id: number
  name: string
  revoked: boolean
  createdAt: string
  expiresAt: string
  keySuffix: string
}

export type ApiKeyPageContentProps = {
  readonly isGitHubAuthEnabled: boolean
}
