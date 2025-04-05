import { gql } from '@apollo/client'

export const GET_PROJECT_DATA = gql`
  query GetProject($key: String!) {
    project(key: $key) {
      contributorsCount
      forksCount
      issuesCount
      isActive
      key
      languages
      leaders
      level
      name
      recentIssues {
        title
        commentsCount
        createdAt
        url
        author {
          avatarUrl
          login
          name
          url
        }
      }
      recentReleases {
        author {
          avatarUrl
          login
          name
        }
        name
        publishedAt
        tagName
        url
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
      repositoriesCount
      starsCount
      summary
      topContributors {
        avatarUrl
        contributionsCount
        login
        name
      }
      topics
      type
      updatedAt
      url
    }
  }
`
