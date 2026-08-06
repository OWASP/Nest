import { gql } from '@apollo/client'

const SNAPSHOT_SUBSCRIPTION_FIELDS = gql`
  fragment SnapshotSubscriptionFields on SnapshotSubscriptionNode {
    id
    frequency
    isActive
    includeChapters
    includeEvents
    includeIssues
    includePosts
    includeProjects
    includePullRequests
    includeReleases
    includeUsers
    createdAt
    updatedAt
  }
`

const ENTITY_SUBSCRIPTION_FIELDS = gql`
  fragment EntitySubscriptionFields on EntitySubscriptionNode {
    id
    frequency
    isActive
    chapter {
      id
      name
    }
    committee {
      id
      name
    }
    project {
      id
      name
    }
    createdAt
    updatedAt
  }
`

export const GET_MY_SNAPSHOT_SUBSCRIPTION = gql`
  query GetMySnapshotSubscription {
    mySnapshotSubscription {
      ...SnapshotSubscriptionFields
    }
  }
  ${SNAPSHOT_SUBSCRIPTION_FIELDS}
`

export const CREATE_SNAPSHOT_SUBSCRIPTION = gql`
  mutation CreateSnapshotSubscription($inputData: CreateSnapshotSubscriptionInput!) {
    createSnapshotSubscription(inputData: $inputData) {
      ok
      message
      subscription {
        ...SnapshotSubscriptionFields
      }
    }
  }
  ${SNAPSHOT_SUBSCRIPTION_FIELDS}
`

export const UPDATE_SNAPSHOT_SUBSCRIPTION = gql`
  mutation UpdateSnapshotSubscription($inputData: UpdateSnapshotSubscriptionInput!) {
    updateSnapshotSubscription(inputData: $inputData) {
      ok
      message
      subscription {
        ...SnapshotSubscriptionFields
      }
    }
  }
  ${SNAPSHOT_SUBSCRIPTION_FIELDS}
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

export const GET_MY_ENTITY_SUBSCRIPTIONS = gql`
  query GetMyEntitySubscriptions {
    myEntitySubscriptions {
      ...EntitySubscriptionFields
    }
  }
  ${ENTITY_SUBSCRIPTION_FIELDS}
`

export const CREATE_ENTITY_SUBSCRIPTION = gql`
  mutation CreateEntitySubscription($inputData: CreateEntitySubscriptionInput!) {
    createEntitySubscription(inputData: $inputData) {
      ok
      message
      subscription {
        ...EntitySubscriptionFields
      }
    }
  }
  ${ENTITY_SUBSCRIPTION_FIELDS}
`

export const UPDATE_ENTITY_SUBSCRIPTION = gql`
  mutation UpdateEntitySubscription(
    $subscriptionId: Int!
    $inputData: UpdateEntitySubscriptionInput!
  ) {
    updateEntitySubscription(subscriptionId: $subscriptionId, inputData: $inputData) {
      ok
      message
      subscription {
        ...EntitySubscriptionFields
      }
    }
  }
  ${ENTITY_SUBSCRIPTION_FIELDS}
`

export const CANCEL_ENTITY_SUBSCRIPTION = gql`
  mutation CancelEntitySubscription($subscriptionId: Int!) {
    cancelEntitySubscription(subscriptionId: $subscriptionId) {
      ok
      message
      subscription {
        id
        isActive
      }
    }
  }
`

export const DELETE_ENTITY_SUBSCRIPTION = gql`
  mutation DeleteEntitySubscription($subscriptionId: Int!) {
    deleteEntitySubscription(subscriptionId: $subscriptionId) {
      ok
      message
    }
  }
`

export const REACTIVATE_ENTITY_SUBSCRIPTION = gql`
  mutation ReactivateEntitySubscription($subscriptionId: Int!) {
    reactivateEntitySubscription(subscriptionId: $subscriptionId) {
      ok
      message
      subscription {
        id
        isActive
      }
    }
  }
`
