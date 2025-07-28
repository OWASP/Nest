export type CreateApiKeyResult = {
  apiKey: ApiKey
  code?: string
  message?: string
  ok: boolean
  rawKey: string
}

export type ApiKey = {
  createdAt: string
  expiresAt: string
  isRevoked: boolean
  name: string
  uuid: string
}

export type ApiKeyPageContentProps = {
  readonly isGitHubAuthEnabled: boolean
}
