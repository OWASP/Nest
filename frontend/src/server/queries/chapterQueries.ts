import { gql } from '@apollo/client'

export const GET_CHAPTER_DATA = gql`
  query GetChapterData($key: String!) {
    chapter(key: $key) {
      id
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
      entityLeaders {
        id
        description
        memberName
        member {
          id
          login
          name
          avatarUrl
        }
      }
    }
    topContributors(chapter: $key) {
      id
      avatarUrl
      login
      name
    }
  }
`

export const GET_CHAPTER_METADATA = gql`
  query GetChapterMetadata($key: String!) {
    chapter(key: $key) {
      id
      name
      summary
    }
  }
`
