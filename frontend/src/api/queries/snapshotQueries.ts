import { gql } from '@apollo/client'

export const GET_SNAPSHOT_DETAILS = gql`
  query GetSnapshotDetails($key: String!) {
    snapshot(key: $key) {
      title
      key
      updatedAt
      createdAt
      startAt
      endAt
      status
      errorMessage
      newReleases {
        name
        publishedAt
        tagName
        projectName
      }
      newProjects {
        key
        name
        summary
        starsCount
        forksCount
        contributorsCount
        level
        isActive
        repositoriesCount
        topContributors {
          avatarUrl
          contributionsCount
          login
          name
        }
      }
      newChapters {
        key
        name
        createdAt
        suggestedLocation
        region
        summary
        topContributors {
          avatarUrl
          contributionsCount
          login
          name
        }
        updatedAt
        url
        relatedUrls
        geoLocation {
          lat
          lng
        }
        isActive
      }
    }
  }
`
