import { gql } from '@apollo/client'

export const GET_CERTIFICATE = gql`
  query GetCertificate($id: String!) {
    certificate(certificateId: $id) {
      id
      githubUser {
        avatarUrl
        login
        name
      }
      issuedAt
      isVerified
      score
      tier
    }
  }
`

export const GET_MY_CERTIFICATE = gql`
  query GetMyCertificate {
    myCertificates {
      id
      githubUser {
        avatarUrl
        login
        name
      }
      issuedAt
      isVerified
      score
      tier
    }
  }
`
