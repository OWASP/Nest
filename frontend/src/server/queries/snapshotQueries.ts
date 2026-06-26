import { gql } from '@apollo/client'

export const SNAPSHOT_PULL_REQUEST_FIELDS = gql`
  fragment SnapshotPullRequestFields on PullRequestNode {
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
`

export const SNAPSHOT_ISSUE_FIELDS = gql`
  fragment SnapshotIssueFields on IssueNode {
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
`

export const GET_SNAPSHOT_DETAILS = gql`
  query GetSnapshotDetails(
    $key: String!
    $prLimit: Int = 6
    $prOffset: Int = 0
    $issueLimit: Int = 6
    $issueOffset: Int = 0
    $eventsLimit: Int = 100
    $postsLimit: Int = 100
    $usersLimit: Int = 100
  ) {
    snapshot(key: $key) {
      id
      endAt
      key
      startAt
      title
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
      projects {
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
      chapters {
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
      events(limit: $eventsLimit) {
        id
        category
        endDate
        key
        name
        startDate
        suggestedLocation
        summary
        url
      }
      posts(limit: $postsLimit) {
        id
        authorImageUrl
        authorName
        publishedAt
        title
        url
      }
      pullRequests(limit: $prLimit, offset: $prOffset) {
        ...SnapshotPullRequestFields
      }
      issues(limit: $issueLimit, offset: $issueOffset) {
        ...SnapshotIssueFields
      }
      users(limit: $usersLimit) {
        id
        avatarUrl
        login
        name
        createdAt
      }
    }
  }
  ${SNAPSHOT_PULL_REQUEST_FIELDS}
  ${SNAPSHOT_ISSUE_FIELDS}
`

export const GET_SNAPSHOT_DETAILS_METADATA = gql`
  query GetSnapshotDetailsMetadata($key: String!) {
    snapshot(key: $key) {
      id
      title
    }
  }
`

export const GET_SNAPSHOT_PULL_REQUESTS = gql`
  query GetSnapshotPullRequests($key: String!, $limit: Int = 6, $offset: Int = 0) {
    snapshot(key: $key) {
      id
      pullRequests(limit: $limit, offset: $offset) {
        ...SnapshotPullRequestFields
      }
    }
  }
  ${SNAPSHOT_PULL_REQUEST_FIELDS}
`

export const GET_SNAPSHOT_ISSUES = gql`
  query GetSnapshotIssues($key: String!, $limit: Int = 6, $offset: Int = 0) {
    snapshot(key: $key) {
      id
      issues(limit: $limit, offset: $offset) {
        ...SnapshotIssueFields
      }
    }
  }
  ${SNAPSHOT_ISSUE_FIELDS}
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
