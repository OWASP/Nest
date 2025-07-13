import { gql } from '@apollo/client'
export const SYNC_DJANGO_SESSION_MUTATION = gql`
  mutation SyncDjangoSession($accessToken: String!) {
    githubAuth(accessToken: $accessToken) {
      authUser {
        username
      }
    }
  }
`
export const GET_USER_ROLES = gql`
  query GetUserRoles {
    currentUserRoles {
      roles
    }
  }
`
