import { gql } from '@apollo/client'

export const GET_USER_DATA = gql`
  query GetUser($key: String!) {
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
        repository {
          key
        }
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
        repository {
          key
        }
        tagName
        url
      }
      releasesCount
      url
    }
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
  }
`
