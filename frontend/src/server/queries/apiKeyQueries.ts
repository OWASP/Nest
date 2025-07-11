import { gql } from '@apollo/client'

export const GET_API_KEYS = gql`
  query GetApiKeys($includeRevoked: Boolean!) {
    apiKeys(includeRevoked: $includeRevoked) {
      id
      name
      isRevoked
      createdAt
      expiresAt
      keySuffix
    }
  }
`

export const CREATE_API_KEY = gql`
  mutation CreateApiKey($name: String!, $expiresAt: DateTime) {
    createApiKey(name: $name, expiresAt: $expiresAt) {
      apiKey {
        id
        name
        isRevoked
        createdAt
        expiresAt
        keySuffix
      }
      rawKey
    }
  }
`

export const REVOKE_API_KEY = gql`
  mutation RevokeApiKey($keyId: Int!) {
    revokeApiKey(keyId: $keyId) {
      ok
      code
      message
    }
  }
`
