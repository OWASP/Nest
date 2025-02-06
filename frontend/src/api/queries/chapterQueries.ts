import { gql } from '@apollo/client'

export const GET_CHAPTER_DATA = gql`
  query GetChapter($key: String!) {
    chapter(key: $key) {
      createdAt
      isActive
      key
      leaders
      name
      region
      relatedUrls
      suggestedLocation
      topContributors {
        avatarUrl
        contributionsCount
        login
        name
      }
      summary
      updatedAt
      url
      geoLocation {
        lat
        lng
      }
    }
  }
`
