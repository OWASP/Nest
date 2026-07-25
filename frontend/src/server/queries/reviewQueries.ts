import { gql } from '@apollo/client'

export const GET_BOARD_CANDIDATE_CLAIM_REVIEWS = gql`
  query GetBoardCandidateClaimReviews($login: String!, $year: Int!) {
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
      candidate(login: $login) {
        id
      }
      reviewer(login: $login) {
        id
      }
    }
  }
`
