import { gql } from '@apollo/client'

export const GET_LEADER_DATA = gql`
  query GetLeaderData($key: String!) {
    user(login: $key) {
      id
      avatarUrl
      login
      name
      badgeCount
      badges {
        cssClass
        description
        id
        name
        weight
      }
    }
  }
`

export const GET_USER_DATA = gql`
  query GetUserData($key: String!) {
    recentIssues(limit: 5, login: $key) {
      id
      createdAt
      organizationName
      repositoryName
      title
      url
    }
    recentMilestones(limit: 5, login: $key) {
      id
      title
      openIssuesCount
      closedIssuesCount
      repositoryName
      organizationName
      createdAt
      url
    }
    recentPullRequests(limit: 5, login: $key) {
      id
      createdAt
      organizationName
      repositoryName
      title
      url
    }
    recentReleases(limit: 5, login: $key) {
      id
      isPreRelease
      name
      publishedAt
      organizationName
      repositoryName
      tagName
      url
    }
    topContributedRepositories(login: $key) {
      id
      contributorsCount
      forksCount
      isArchived
      key
      name
      openIssuesCount
      organization {
        id
        login
      }
      starsCount
      subscribersCount
      url
    }
    user(login: $key) {
      avatarUrl
      badgeCount
      badges {
        cssClass
        description
        id
        name
        weight
      }
      bio
      company
      contributionsCount
      createdAt
      email
      followersCount
      followingCount
      id
      issuesCount
      location
      login
      name
      publicRepositoriesCount
      releasesCount
      updatedAt
      url
    }
  }
`
export const GET_USER_METADATA = gql`
  query GetUserMetadata($key: String!) {
    user(login: $key) {
      badgeCount
      bio
      id
      login
      name
    }
  }
`
