import { gql } from '@apollo/client'

export const GET_SNAPSHOT_DETAILS = gql`
  query GetSnapshotDetails($key: String!) {
    snapshot(key: $key) {
      title
      key
      createdAt
      updatedAt
      startAt
      endAt
      newReleases {
        name
        version
        releaseDate
      }
      newProjects {
        key
        name
        summary
        starsCount
        forksCount
        repositoriesCount
        topContributors {
          name
          login
          contributionsCount
        }
      }
      newChapters {
        key
        name
        geoLocation {
          lat
          lng
        }
      }
    }
  }
`
