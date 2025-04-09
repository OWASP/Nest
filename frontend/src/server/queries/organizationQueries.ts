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
    recentPullRequests(limit: 5, organization: $login) {
      title
      createdAt
      url
      author {
        login
        avatarUrl
      }
    }
    recentReleases(limit: 6, organization: $login) {
      name
      tagName
      publishedAt
      url
      repositoryName
      author {
        login
        avatarUrl
      }
    }
    organizationRepositories(organization: $login, limit: 12) {
      name
      url
      contributorsCount
      forksCount
      openIssuesCount
      starsCount
      key
    }
    recentIssues(limit: 5, organization: $login) {
      author {
        avatarUrl
        login
      }
      commentsCount
      createdAt
      title
      url
    }
  }
`
