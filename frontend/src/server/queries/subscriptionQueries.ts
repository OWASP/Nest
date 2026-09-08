import { gql } from '@apollo/client'

const SNAPSHOT_SUBSCRIPTION_FIELDS = gql`
  fragment SnapshotSubscriptionFields on SnapshotSubscriptionNode {
    id
    name
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
    subscribedProjects {
      id
      key
      name
      repositoryNames
    }
    subscribedChapters {
      id
      key
      name
    }
    subscribedCommittees {
      id
      key
      name
    }
    createdAt
    updatedAt
  }
`

export const GET_MY_SNAPSHOT_SUBSCRIPTIONS = gql`
  query GetMySnapshotSubscriptions {
    mySnapshotSubscriptions {
      ...SnapshotSubscriptionFields
    }
  }
  ${SNAPSHOT_SUBSCRIPTION_FIELDS}
`

export const GET_SUBSCRIPTION_BY_TOKEN = gql`
  query GetSubscriptionByToken($token: String!, $snapshotKey: String!) {
    subscriptionByToken(token: $token) {
      ...SnapshotSubscriptionFields
      entitySections(snapshotKey: $snapshotKey) {
        entityKey
        entityName
        entityType
        pullRequests {
          id
          author {
            avatarUrl
            id
            login
            name
          }
          createdAt
          mergedAt
          organizationName
          repositoryName
          state
          title
          url
        }
        issues {
          id
          author {
            avatarUrl
            id
            login
            name
          }
          createdAt
          isMerged
          organizationName
          repositoryName
          state
          title
          url
        }
        releases {
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
      }
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
  mutation UpdateSnapshotSubscription(
    $subscriptionId: Int!
    $inputData: UpdateSnapshotSubscriptionInput!
  ) {
    updateSnapshotSubscription(subscriptionId: $subscriptionId, inputData: $inputData) {
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
  mutation CancelSnapshotSubscription($subscriptionId: Int!) {
    cancelSnapshotSubscription(subscriptionId: $subscriptionId) {
      ok
      message
      subscription {
        id
        isActive
      }
    }
  }
`

export const DELETE_SNAPSHOT_SUBSCRIPTION = gql`
  mutation DeleteSnapshotSubscription($subscriptionId: Int!) {
    deleteSnapshotSubscription(subscriptionId: $subscriptionId) {
      ok
      message
    }
  }
`

export const REACTIVATE_SNAPSHOT_SUBSCRIPTION = gql`
  mutation ReactivateSnapshotSubscription($subscriptionId: Int!) {
    reactivateSnapshotSubscription(subscriptionId: $subscriptionId) {
      ok
      message
      subscription {
        id
        isActive
      }
    }
  }
`

export const UNSUBSCRIBE_BY_TOKEN = gql`
  mutation UnsubscribeByToken($token: String!) {
    unsubscribeByToken(token: $token) {
      ok
      message
    }
  }
`
