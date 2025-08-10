import { gql } from '@apollo/client'

export const LOGOUT_DJANGO_MUTATION = gql`
  mutation LogoutDjango {
    logoutUser {
      code
      message
      ok
    }
  }
`

export const SYNC_DJANGO_SESSION_MUTATION = gql`
  mutation SyncDjangoSession($accessToken: String!) {
    githubAuth(accessToken: $accessToken) {
      message
      ok
      user {
        isOwaspStaff
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
