import { gql } from '@apollo/client'

export const GET_SPONSORS = gql`
  query GetSponsorsData {
    activeSponsors {
      id
      name
      url
      description
      imageUrl
    }
  }
`
