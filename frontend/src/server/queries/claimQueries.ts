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
      key
      name
      order
      status
      updatedAt
    }
  }
`
