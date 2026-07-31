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

export const GET_CLAIM_EVIDENCE = gql`
  query GetBoardCandidateClaimEvidence(
    $login: String!
    $claimKey: String!
    $key: String!
    $year: Int!
  ) {
    boardCandidateClaimEvidence(login: $login, claimKey: $claimKey, key: $key, year: $year) {
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

export const GET_CLAIM_EVIDENCE_FILE_URL = gql`
  query GetBoardCandidateClaimEvidenceFileUrl(
    $login: String!
    $claimKey: String!
    $key: String!
    $year: Int!
  ) {
    boardCandidateClaimEvidenceFileUrl(login: $login, claimKey: $claimKey, key: $key, year: $year)
  }
`
