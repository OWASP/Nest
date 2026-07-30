import { gql } from '@apollo/client'

export const GET_CLAIM_EVIDENCES = gql`
  query GetBoardCandidateClaimEvidences($login: String!, $claimKey: String!, $year: Int!) {
    boardCandidateClaimEvidences(login: $login, claimKey: $claimKey, year: $year) {
      id
      createdAt
      description
      hasFile
      key
      name
      sourceUrl
      updatedAt
    }
  }
`
