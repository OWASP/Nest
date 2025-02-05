import { gql } from '@apollo/client'

export const GET_REPOSITORY_DATA = gql`
  query GetRepositoryData($key: String!) {
    repository(key: $key) {
      commitsCount
      contributorsCount
      createdAt
      description
      forksCount
      issues {
        title
        commentsCount
        createdAt
        author {
          avatarUrl
          name
          login
        }
      }
      languages
      license
      name
      openIssuesCount
      releases {
        name
        tagName
        isPreRelease
        publishedAt
        author {
          avatarUrl
          name
          login
        }
      }
      size
      starsCount
      topContributors {
        avatarUrl
        contributionsCount
        login
        name
      }
      topics
      updatedAt
      url
    }
  }
`
