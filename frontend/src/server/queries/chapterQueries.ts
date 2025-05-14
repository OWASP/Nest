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
      updatedAt
      url
    }
    topContributors(chapter: $key) {
      avatarUrl
      contributionsCount
      login
      name
    }
  }
`

export const GET_CHAPTER_METADATA = gql`
  query GetChapter($key: String!) {
    chapter(key: $key) {
      name
      summary
    }
  }
`
