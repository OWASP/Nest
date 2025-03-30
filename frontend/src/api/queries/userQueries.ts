import { gql } from '@apollo/client'

export const GET_USER_DATA = gql`
  query GetUser($key: String!) {
    recentPullRequests(login: $key) {
      createdAt
      title
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
      issues {
        commentsCount
        createdAt
        title
        url
      }
      issuesCount
      location
      login
      name
      publicRepositoriesCount
      releases {
        isPreRelease
        name
        publishedAt
        tagName
        url
      }
      releasesCount
      url
      contributionsCount
    }
  }
`
