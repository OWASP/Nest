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
      stats {
        totalContributors
        totalForks
        totalIssues
        totalRepositories
        totalStars
      }
      updatedAt
      url
    }
    topContributors(organization: $login) {
      avatarUrl
      contributionsCount
      login
      name
    }
    recentPullRequests(limit: 5, organization: $login, distinct: true) {
      author {
        avatarUrl
        login
        name
      }
      createdAt
      repositoryName
      title
      url
    }
    recentReleases(limit: 6, organization: $login, distinct: true) {
      author {
        avatarUrl
        login
        name
      }
      name
      publishedAt
      repositoryName
      tagName
      url
    }
    repositories(organization: $login, limit: 12) {
      contributorsCount
      forksCount
      key
      name
      openIssuesCount
      organization {
        login
      }
      starsCount
      url
    }
    recentIssues(limit: 5, organization: $login, distinct: true) {
      author {
        avatarUrl
        login
        name
      }
      createdAt
      repositoryName
      title
      url
    }
  }
`
