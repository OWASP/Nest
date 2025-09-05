import { gql } from '@apollo/client'

export const GET_SNAPSHOT_DETAILS = gql`
  query GetSnapshotDetails($key: String!) {
    snapshot(key: $key) {
      id
      endAt
      key
      startAt
      title
      newReleases {
        id
        name
        organizationName
        projectName
        publishedAt
        repositoryName
        tagName
        author {
          avatarUrl
          id
          login
          name
        }
      }
      newProjects {
        id
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
          id
          avatarUrl
          login
          name
        }
      }
      newChapters {
        id
        key
        name
        createdAt
        suggestedLocation
        region
        summary
        topContributors {
          id
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
      id
      title
    }
  }
`

export const GET_COMMUNITY_SNAPSHOTS = gql`
  query GetCommunitySnapshots {
    snapshots(limit: 12) {
      id
      key
      title
      startAt
      endAt
    }
  }
`
