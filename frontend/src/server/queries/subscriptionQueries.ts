import { gql } from '@apollo/client'

const SUBSCRIPTION_FIELDS = gql`
  fragment SubscriptionFields on SnapshotSubscriptionNode {
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
`

export const GET_MY_SUBSCRIPTION = gql`
  query GetMySubscription {
    mySubscription {
      ...SubscriptionFields
    }
  }
  ${SUBSCRIPTION_FIELDS}
`

export const CREATE_SNAPSHOT_SUBSCRIPTION = gql`
  mutation CreateSnapshotSubscription($inputData: CreateSnapshotSubscriptionInput!) {
    createSnapshotSubscription(inputData: $inputData) {
      ok
      message
      subscription {
        ...SubscriptionFields
      }
    }
  }
  ${SUBSCRIPTION_FIELDS}
`

export const UPDATE_SNAPSHOT_SUBSCRIPTION = gql`
  mutation UpdateSnapshotSubscription($inputData: UpdateSnapshotSubscriptionInput!) {
    updateSnapshotSubscription(inputData: $inputData) {
      ok
      message
      subscription {
        ...SubscriptionFields
      }
    }
  }
  ${SUBSCRIPTION_FIELDS}
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
