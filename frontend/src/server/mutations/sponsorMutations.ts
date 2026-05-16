import { gql } from '@apollo/client'

export const CREATE_SPONSOR_APPLICATION = gql`
  mutation CreateSponsorApplication(
    $name: String!
    $contactEmail: String!
    $sponsorshipInterest: String!
    $website: String
  ) {
    createSponsorApplication(
      name: $name
      contactEmail: $contactEmail
      sponsorshipInterest: $sponsorshipInterest
      website: $website
    ) {
      ok
      code
      message
      sponsor {
        id
        description
        name
        sponsorType
        status
        url
      }
    }
  }
`
