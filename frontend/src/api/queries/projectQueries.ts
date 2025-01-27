import { gql } from '@apollo/client'

export const GET_PROJECT_DATA = gql`
  query GetProject($key: String!) {
    project(key: $key) {
      recentReleases {
        name
        tagName
        isPreRelease
        publishedAt
        author {
          avatarUrl
          name
        }
      }
      recentIssues {
        title
        commentsCount
        createdAt
        author {
          avatarUrl
          name
        }
      }
    }
  }
`
