import { gql } from '@apollo/client'

export const GET_LEADER_DATA = gql`
  query GetLeaderData($key: String!) {
    user(login: $key) {
      id
      avatarUrl
      company
      location
      login
      name
      badges {
        id
        name
        description
        cssClass
        weight
      }
      badgeCount
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
      id
      avatarUrl
      bio
      company
      contributionsCount
      createdAt
      email
      followersCount
      followingCount
      issuesCount
      location
      login
      name
      badges {
        cssClass
        description
        id
        name
        weight
      }
      badgeCount
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
      id
      bio
      login
      name
      badgeCount
    }
  }
`
