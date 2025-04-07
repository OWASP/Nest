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
      repositories {
        name
        url
        contributorsCount
        forksCount
        openIssuesCount
        starsCount
        key
      }
      issues {
        title
        state
        createdAt
        url
        author {
          login
          avatarUrl
        }
      }
      releases {
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
      topContributors {
        contributionsCount
        login
        name
        avatarUrl
      }
    }
  }
`
