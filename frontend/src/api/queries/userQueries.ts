import { gql } from '@apollo/client'

export const GET_USER_DATA = gql`
  query GetUser($key: String!) {
    recentIssues(login: $key) {
      commentsCount
      createdAt
      title
      url
    }
    recentPullRequests(login: $key) {
      createdAt
      title
      url
    }
    recentReleases(login: $key) {
      isPreRelease
      name
      publishedAt
      tagName
      url
    }
    topContributedRepositories(login: $key) {
      contributorsCount
      forksCount
      key
      name
      openIssuesCount
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
