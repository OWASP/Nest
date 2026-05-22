import { gql } from '@apollo/client'

export const CREATE_SPONSOR = gql`
  mutation CreateSponsor($input: CreateSponsorInput!) {
    createSponsor(inputData: $input) {
      id
      name
      url
    }
  }
`
