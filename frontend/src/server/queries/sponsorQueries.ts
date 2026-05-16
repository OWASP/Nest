import { gql } from '@apollo/client'

export const GET_SPONSORS = gql`
  query GetSponsors {
    sponsors {
      id
      description
      imageUrl
      name
      sponsorType
      status
      url
    }
  }
`
