import { gql } from '@apollo/client'

export const GET_SNAPSHOT_DETAILS = gql`
  query GetSnapshotDetails($key: String!) {
    snapshot(key: $key) {
      endAt
      key
      startAt
      title
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

export const GET_SNAPSHOT_DETAILS_METADATA = gql`
  query GetSnapshotDetailsMetadata($key: String!) {
    snapshot(key: $key) {
      title
    }
  }
`

export const GET_COMMUNITY_SNAPSHOTS = gql`
  query GetCommunitySnapshots {
    snapshots(limit: 12) {
      key
      title
      startAt
      endAt
    }
  }
`
