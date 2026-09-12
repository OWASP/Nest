import { gql } from '@apollo/client'

export const ISSUE_CERTIFICATE = gql`
  mutation IssueCertificate($inputData: IssueCertificateInput!) {
    issueCertificate(inputData: $inputData) {
      id
      title
      issuedAt
      recipient {
        login
      }
    }
  }
`
