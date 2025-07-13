import { gql } from '@apollo/client'

export const GET_API_KEYS = gql`
  query GetApiKeys {
    apiKeys {
      name
      isRevoked
      createdAt
      expiresAt
      uuid
    }
    activeApiKeyCount
  }
`

export const CREATE_API_KEY = gql`
  mutation CreateApiKey($name: String!, $expiresAt: DateTime!) {
    createApiKey(name: $name, expiresAt: $expiresAt) {
      ok
      code
      message
      apiKey {
        uuid
        name
        isRevoked
        createdAt
        expiresAt
      }
      rawKey
    }
  }
`

export const REVOKE_API_KEY = gql`
  mutation RevokeApiKey($uuid: UUID!) {
    revokeApiKey(uuid: $uuid) {
      ok
      code
      message
    }
  }
`
