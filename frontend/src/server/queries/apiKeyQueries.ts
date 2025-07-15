import { gql } from '@apollo/client'

export const GET_API_KEYS = gql`
  query GetApiKeys {
    activeApiKeyCount
    apiKeys {
      createdAt
      expiresAt
      isRevoked
      name
      uuid
    }
  }
`

export const CREATE_API_KEY = gql`
  mutation CreateApiKey($name: String!, $expiresAt: DateTime!) {
    createApiKey(name: $name, expiresAt: $expiresAt) {
      apiKey {
        createdAt
        expiresAt
        isRevoked
        name
        uuid
      }
      code
      message
      ok
      rawKey
    }
  }
`

export const REVOKE_API_KEY = gql`
  mutation RevokeApiKey($uuid: UUID!) {
    revokeApiKey(uuid: $uuid) {
      code
      message
      ok
    }
  }
`
