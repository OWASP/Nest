import { gql } from '@apollo/client'

export const GET_CHAPTER_DATA = gql`
  query GetChapterData($key: String!) {
    chapter(key: $key) {
      id
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
      contributionData
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
