import { gql } from '@apollo/client'

export const GET_CANDIDATE_CLAIM = gql`
  query GetBoardCandidateClaim($login: String!, $key: String!, $year: Int!) {
    boardCandidateClaim(login: $login, key: $key, year: $year) {
      id
      createdAt
      description
      key
      name
      status
      updatedAt
    }
  }
`

export const GET_CANDIDATE_CLAIMS = gql`
  query GetBoardCandidateClaims($login: String!, $year: Int!) {
    boardCandidateClaims(login: $login, year: $year) {
      id
      createdAt
      description
      hasEvidence
      key
      name
      order
      status
      updatedAt
    }
  }
`

export const GET_CANDIDATE_AND_CLAIMS = gql`
  query GetBoardCandidateAndClaims($login: String!, $year: Int!) {
    boardCandidateClaims(login: $login, year: $year) {
      id
      createdAt
      description
      hasEvidence
      key
      name
      order
      status
      updatedAt
    }
    boardOfDirectors(year: $year) {
      candidate(login: $login) {
        id
      }
    }
  }
`

export const GET_CLAIM_AND_EVIDENCES = gql`
  query GetClaimAndEvidences(
    $login: String!
    $key: String!
    $year: Int!
    $currentUserLogin: String!
  ) {
    boardCandidateClaim(login: $login, key: $key, year: $year) {
      id
      createdAt
      description
      key
      name
      status
      updatedAt
      reviews {
        id
        createdAt
        notes
        status
        reviewer {
          login
        }
      }
    }
    boardCandidateClaimEvidences(login: $login, claimKey: $key, year: $year) {
      id
      createdAt
      description
      hasFile
      key
      name
      sourceUrl
      updatedAt
    }
    boardOfDirectors(year: $year) {
      reviewer(login: $currentUserLogin) {
        id
      }
    }
  }
`
