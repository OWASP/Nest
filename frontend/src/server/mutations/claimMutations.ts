import { gql } from '@apollo/client'

export const CREATE_CLAIM = gql`
  mutation CreateBoardCandidateClaim($input: CreateClaimInput!) {
    createBoardCandidateClaim(inputData: $input) {
      ok
      code
      message
      claim {
        createdAt
        description
        hasEvidence
        id
        key
        name
        order
        status
        updatedAt
      }
    }
  }
`

export const UPDATE_CLAIM = gql`
  mutation UpdateBoardCandidateClaim($input: UpdateClaimInput!) {
    updateBoardCandidateClaim(inputData: $input) {
      ok
      code
      message
      claim {
        createdAt
        description
        hasEvidence
        id
        key
        name
        order
        status
        updatedAt
      }
    }
  }
`

export const DISCARD_CLAIM = gql`
  mutation DiscardBoardCandidateClaim($input: DiscardClaimInput!) {
    discardBoardCandidateClaim(inputData: $input) {
      ok
      code
      message
      claim {
        createdAt
        description
        hasEvidence
        id
        key
        name
        order
        status
        updatedAt
      }
    }
  }
`

export const SUBMIT_CLAIM = gql`
  mutation SubmitBoardCandidateClaim($input: SubmitClaimInput!) {
    submitBoardCandidateClaim(inputData: $input) {
      ok
      code
      message
      claim {
        createdAt
        description
        hasEvidence
        id
        key
        name
        order
        status
        updatedAt
      }
    }
  }
`

export const WITHDRAW_CLAIM = gql`
  mutation WithdrawBoardCandidateClaim($input: WithdrawClaimInput!) {
    withdrawBoardCandidateClaim(inputData: $input) {
      ok
      code
      message
      claim {
        createdAt
        description
        hasEvidence
        id
        key
        name
        order
        status
        updatedAt
      }
    }
  }
`

export const REORDER_CLAIMS = gql`
  mutation ReorderBoardCandidateClaims($input: ReorderClaimsInput!) {
    reorderBoardCandidateClaims(inputData: $input) {
      ok
      code
      message
      claims {
        createdAt
        description
        hasEvidence
        id
        key
        name
        order
        status
        updatedAt
      }
    }
  }
`
