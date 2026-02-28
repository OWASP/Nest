import { gql } from '@apollo/client'

export const GET_ABOUT_PAGE_DATA = gql`
  query GetAboutPageData(
    $projectKey: String!
    $excludedUsernames: [String!]
    $hasFullName: Boolean = false
    $limit: Int = 20
    $leader1: String!
    $leader2: String!
    $leader3: String!
  ) {
    project(key: $projectKey) {
      id
      contributorsCount
      forksCount
      issuesCount
      name
      starsCount
      summary
      recentMilestones(limit: 25) {
        id
        title
        url
        body
        progress
        state
      }
    }
    topContributors(
      project: $projectKey
      excludedUsernames: $excludedUsernames
      hasFullName: $hasFullName
      limit: $limit
    ) {
      id
      avatarUrl
      login
      name
    }
    leader1: user(login: $leader1) {
      id
      avatarUrl
      login
      name
    }
    leader2: user(login: $leader2) {
      id
      avatarUrl
      login
      name
    }
    leader3: user(login: $leader3) {
      id
      avatarUrl
      login
      name
    }
  }
`
