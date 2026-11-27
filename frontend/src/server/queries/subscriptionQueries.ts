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
    projects {
      id
      key
      name
      repositoryNames
    }
    chapters {
      id
      key
      name
    }
    committees {
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

export const DELETE_SNAPSHOT_SUBSCRIPTION = gql`
  mutation DeleteSnapshotSubscription($subscriptionId: Int!) {
    deleteSnapshotSubscription(subscriptionId: $subscriptionId) {
      ok
      message
    }
  }
`

export const UNSUBSCRIBE_BY_TOKEN = gql`
  mutation UnsubscribeByToken($inputData: UnsubscribeTokenInput!) {
    unsubscribeByToken(inputData: $inputData) {
      ok
      message
    }
  }
`

export const GET_SUBSCRIPTION_NAME_BY_TOKEN = gql`
  query GetSubscriptionNameByToken($token: String!) {
    subscriptionByToken(token: $token) {
      name
    }
  }
`
