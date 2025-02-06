import { gql } from '@apollo/client'

export const GET_CHAPTER_DATA = gql`
  query GetChapter($key: String!) {
    chapter(key: $key) {
      geoLocation {
        lat
        lng
      }
      isActive
      key
      name
      region
      relatedUrls
      suggestedLocation
      summary
      topContributors {
        avatarUrl
        contributionsCount
        login
        name
      }
      updatedAt
      url
    }
  }
`
