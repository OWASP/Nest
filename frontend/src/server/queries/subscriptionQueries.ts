import { gql } from '@apollo/client'

export const GET_MY_SUBSCRIPTION = gql`
  query GetMySubscription {
    mySubscription {
      id
      frequency
      isActive
      includeChapters
      includeEvents
      includePosts
      includeUsers
      projectPreferences {
        id
        project {
          id
          name
        }
        includeIssues
        includePullRequests
        includeReleases
      }
      chapters {
        id
        name
      }
      createdAt
      updatedAt
    }
  }
`

export const CREATE_SNAPSHOT_SUBSCRIPTION = gql`
  mutation CreateSnapshotSubscription($inputData: CreateSnapshotSubscriptionInput!) {
    createSnapshotSubscription(inputData: $inputData) {
      ok
      message
      subscription {
        id
        frequency
        isActive
        includeChapters
        includeEvents
        includePosts
        includeUsers
        projectPreferences {
          id
          project {
            id
            name
          }
          includeIssues
          includePullRequests
          includeReleases
        }
        chapters {
          id
          name
        }
        createdAt
        updatedAt
      }
    }
  }
`

export const UPDATE_SNAPSHOT_SUBSCRIPTION = gql`
  mutation UpdateSnapshotSubscription($inputData: UpdateSnapshotSubscriptionInput!) {
    updateSnapshotSubscription(inputData: $inputData) {
      ok
      message
      subscription {
        id
        frequency
        isActive
        includeChapters
        includeEvents
        includePosts
        includeUsers
        projectPreferences {
          id
          project {
            id
            name
          }
          includeIssues
          includePullRequests
          includeReleases
        }
        chapters {
          id
          name
        }
        createdAt
        updatedAt
      }
    }
  }
`

export const CANCEL_SNAPSHOT_SUBSCRIPTION = gql`
  mutation CancelSnapshotSubscription {
    cancelSnapshotSubscription {
      ok
      message
      subscription {
        id
        isActive
      }
    }
  }
`
