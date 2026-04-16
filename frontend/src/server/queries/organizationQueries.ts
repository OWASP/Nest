import { gql } from '@apollo/client'

export const GET_ORGANIZATION_DATA = gql`
  query GetOrganizationData($login: String!) {
    organization(login: $login) {
      id
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
      id
      avatarUrl
      login
      name
    }
    recentPullRequests(limit: 5, organization: $login, distinct: true) {
      id
      author {
        id
        avatarUrl
        login
        name
      }
      createdAt
      organizationName
      repositoryName
      title
      url
    }
    recentReleases(limit: 5, organization: $login, distinct: true) {
      id
      author {
        id
        avatarUrl
        login
        name
      }
      name
      organizationName
      publishedAt
      repositoryName
      tagName
      url
    }
    recentMilestones(limit: 5, organization: $login, distinct: true) {
      id
      author {
        id
        avatarUrl
        login
        name
      }
      title
      openIssuesCount
      closedIssuesCount
      repositoryName
      organizationName
      createdAt
      url
    }
    repositories(organization: $login, limit: 12) {
      id
      contributorsCount
      forksCount
      isArchived
      key
      name
      openIssuesCount
      organization {
        id
        login
      }
      starsCount
      url
    }
    recentIssues(limit: 5, organization: $login, distinct: true) {
      id
      author {
        id
        avatarUrl
        login
        name
      }
      createdAt
      organizationName
      repositoryName
      title
      url
    }
  }
`

export const GET_ORGANIZATION_METADATA = gql`
  query GetOrganizationMetadata($login: String!) {
    organization(login: $login) {
      id
      description
      login
      name
    }
  }
`
