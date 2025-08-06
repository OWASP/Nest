import { gql } from '@apollo/client'

export const GET_LEADER_DATA = gql`
  query GetUser($key: String!) {
    user(login: $key) {
      avatarUrl
      login
      name
    }
  }
`

export const GET_USER_DATA = gql`
  query GetUser($key: String!) {
    recentIssues(limit: 5, login: $key) {
      createdAt
      organizationName
      repositoryName
      title
      url
    }
    recentMilestones(limit: 5, login: $key) {
      title
      openIssuesCount
      closedIssuesCount
      repositoryName
      organizationName
      createdAt
      url
    }
    recentPullRequests(limit: 5, login: $key) {
      createdAt
      organizationName
      repositoryName
      title
      url
    }
    recentReleases(limit: 5, login: $key) {
      isPreRelease
      name
      publishedAt
      organizationName
      repositoryName
      tagName
      url
    }
    topContributedRepositories(login: $key) {
      contributorsCount
      forksCount
      key
      name
      openIssuesCount
      organization {
        login
      }
      starsCount
      subscribersCount
      url
    }
    user(login: $key) {
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
      publicRepositoriesCount
      releasesCount
      updatedAt
      url
    }
  }
`
export const GET_USER_METADATA = gql`
  query GetUser($key: String!) {
    user(login: $key) {
      bio
      login
      name
    }
  }
`
