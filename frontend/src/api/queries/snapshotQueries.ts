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

export const GET_COMMUNITY_SNAPSHOTS = gql`
  query GetCommunitySnapshots {
    snapshots(limit: 24) {
      key
      title
      startAt
      endAt
    }
  }
`
