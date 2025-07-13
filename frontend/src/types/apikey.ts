export type CreateApiKeyResult = {
  apiKey: ApiKey
  rawKey: string
}

export type ApiKey = {
  name: string
  isRevoked: boolean
  createdAt: string
  expiresAt: string
  publicId: string
}

export type ApiKeyPageContentProps = {
  readonly isGitHubAuthEnabled: boolean
}
