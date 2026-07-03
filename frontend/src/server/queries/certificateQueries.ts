import { gql } from '@apollo/client'

export const GET_CERTIFICATE = gql`
  query GetCertificate($id: String!) {
    certificate(certificateId: $id) {
      id
      tier
      issuedAt
      score
      isVerified
      githubUser {
        name
        login
        avatarUrl
      }
    }
  }
`

export const GET_MY_CERTIFICATE = gql`
  query GetMyCertificate {
    myCertificate {
      id
      tier
      issuedAt
      score
      isVerified
      githubUser {
        login
        name
        avatarUrl
      }
    }
  }
`
