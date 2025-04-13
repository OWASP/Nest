import { gql } from '@apollo/client'

export const GET_ORGANIZATION_DATA = gql`
  query GetOrganization($login: String!) {
    organization(login: $login) {
      avatarUrl
      collaboratorsCount
      company
      createdAt
      description
      email
      followersCount
      location
      login
      name
      updatedAt
      url
      stats {
        totalRepositories
        totalContributors
        totalStars
        totalForks
        totalIssues
      }
    }
    topContributors(organization: $login) {
      contributionsCount
      login
      name
      avatarUrl
    }
    recentPullRequests(limit: 5, organization: $login, distinct: true) {
      author {
        login
        avatarUrl
      }
      createdAt
      repositoryName
      title
      url
    }
    recentReleases(limit: 6, organization: $login, distinct: true) {
      author {
        login
        avatarUrl
      }
      name
      publishedAt
      repositoryName
      tagName
      url
    }
    repositories(organization: $login, limit: 12) {
      name
      url
      contributorsCount
      forksCount
      openIssuesCount
      starsCount
      key
    }
    recentIssues(limit: 5, organization: $login, distinct: true) {
      author {
        avatarUrl
        login
      }
      commentsCount
      createdAt
      repositoryName
      title
      url
    }
  }
`
