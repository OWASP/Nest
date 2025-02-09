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
          login
          name
        }
      }
      recentIssues {
        title
        commentsCount
        createdAt
        author {
          avatarUrl
          login
          name
        }
      }
      repositories {
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
  }
`
