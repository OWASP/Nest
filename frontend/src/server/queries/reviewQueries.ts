import { gql } from '@apollo/client'

export const GET_CLAIMS_AND_REVIEWS = gql`
  query GetClaimsAndReviews($sessionLogin: String!, $year: Int!) {
    boardCandidateClaims(year: $year) {
      id
      createdAt
      description
      key
      name
      status
      updatedAt
      candidate {
        member {
          login
          name
        }
      }
      reviews {
        id
        createdAt
        status
        reviewer {
          login
        }
      }
    }
    boardOfDirectors(year: $year) {
      id
      candidate(login: $sessionLogin) {
        id
      }
      reviewer(login: $sessionLogin) {
        id
      }
    }
  }
`
