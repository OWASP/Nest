import { gql } from '@apollo/client'

export const CREATE_CLAIM_EVIDENCE = gql`
  mutation CreateBoardCandidateClaimEvidence($input: CreateEvidenceInput!) {
    createBoardCandidateClaimEvidence(inputData: $input) {
      ok
      code
      message
      evidence {
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
  }
`

export const REMOVE_CLAIM_EVIDENCE = gql`
  mutation RemoveBoardCandidateClaimEvidence($input: RemoveEvidenceInput!) {
    removeBoardCandidateClaimEvidence(inputData: $input) {
      ok
      code
      message
      evidence {
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
  }
`

export const UPDATE_CLAIM_EVIDENCE = gql`
  mutation UpdateBoardCandidateClaimEvidence($input: UpdateEvidenceInput!) {
    updateBoardCandidateClaimEvidence(inputData: $input) {
      ok
      code
      message
      evidence {
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
  }
`
