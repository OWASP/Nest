import { gql } from '@apollo/client'

export const CREATE_CLAIM_REVIEW = gql`
  mutation CreateBoardCandidateClaimReview($input: CreateReviewInput!) {
    createBoardCandidateClaimReview(inputData: $input) {
      ok
      code
      message
      fieldErrors {
        field
        message
      }
      review {
        id
        createdAt
        notes
        status
      }
    }
  }
`
