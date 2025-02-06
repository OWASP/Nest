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
      organizations
      repositoriesIndexed {
        contributorsCount
        description
        forksCount
        key
        latestRelease
        license
        name
        ownerKey
        starsCount
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
      repositories {
        contributorsCount
        forksCount
        name
        openIssuesCount
        url
        starsCount
        subscribersCount
      }
    }
  }
`
