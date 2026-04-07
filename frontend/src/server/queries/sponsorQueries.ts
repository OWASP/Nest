import { gql } from '@apollo/client'

export const GET_SPONSORS_PAGE_DATA = gql`
  query GetSponsorsPageData {
    sponsors {
      id
      description
      imageUrl
      name
      sponsorType
      url
    }
  }
`
