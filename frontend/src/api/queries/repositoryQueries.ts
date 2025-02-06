import { gql } from '@apollo/client'

export const GET_REPOSITORY_DATA = gql`
  query GetRepository($projectKey: String!, $repositoryKey: String!) {
    repository(projectKey: $projectKey, repositoryKey: $repositoryKey) {
      commitsCount
      contributorsCount
      createdAt
      description
      forksCount
      key
      issues {
        author {
          avatarUrl
          login
          name
        }
        commentsCount
        createdAt
        title
      }
      languages
      license
      name
      openIssuesCount
      releases {
        author {
          avatarUrl
          name
          login
        }
        isPreRelease
        name
        publishedAt
        tagName
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
