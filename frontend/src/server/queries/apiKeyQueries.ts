import { gql } from '@apollo/client'

export const GET_API_KEYS = gql`
  query GetApiKeys($includeRevoked: Boolean!) {
    apiKeys(includeRevoked: $includeRevoked) {
      name
      isRevoked
      createdAt
      expiresAt
      publicId
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
        publicId
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
  mutation RevokeApiKey($publicId: UUID!) {
    revokeApiKey(publicId: $publicId) {
      ok
      code
      message
    }
  }
`
