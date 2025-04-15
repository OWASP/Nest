import { gql } from '@apollo/client'

export const GET_USER_DATA = gql`
  query GetUser($key: String!) {
    recentIssues(limit: 5, login: $key) {
      createdAt
      repositoryName
      title
      url
    }
    recentPullRequests(limit: 5, login: $key) {
      createdAt
      repositoryName
      title
      url
    }
    recentReleases(limit: 6, login: $key) {
      isPreRelease
      name
      publishedAt
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
      url
    }
  }
`
