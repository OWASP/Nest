import { gql } from '@apollo/client'

export const GET_SPONSORS_DATA = gql`
  query GetSponsorsData {
    sponsors {
      description
      id
      imageUrl
      name
      sponsorType
      url
    }
  }
`
