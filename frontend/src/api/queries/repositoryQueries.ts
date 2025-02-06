import { gql } from '@apollo/client'

export const GET_REPOSITORY_DATA = gql`
  query GetRepository($projectKey: String!, $repoKey: String!) {
    project(key: $projectKey, repoKey: $repoKey) {
      repositories {
        commitsCount
        contributorsCount
        createdAt
        description
        forksCount
        key
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
  }
`
