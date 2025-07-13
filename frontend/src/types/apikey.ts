export type CreateApiKeyResult = {
  ok: boolean
  apiKey: ApiKey
  rawKey: string
  code?: string
  message?: string
}

export type ApiKey = {
  name: string
  isRevoked: boolean
  createdAt: string
  expiresAt: string
  uuid: string
}

export type ApiKeyPageContentProps = {
  readonly isGitHubAuthEnabled: boolean
}
