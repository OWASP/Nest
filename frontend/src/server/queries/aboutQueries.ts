import { gql } from '@apollo/client'

export const GET_ABOUT_PAGE_DATA = gql`
  query GetAboutPageData(
    $key: String!
    $leaderLogins: [String!]!
    $hasFullName: Boolean = false
    $limit: Int = 20
  ) {
    project(key: $key) {
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
      excludedUsernames: $leaderLogins
      hasFullName: $hasFullName
      limit: $limit
      project: $key
    ) {
      id
      avatarUrl
      login
      name
    }

    users(logins: $leaderLogins) {
      id
      avatarUrl
      login
      name
      badgeCount
      badges {
        cssClass
        description
        id
        name
        weight
      }
    }
  }
`
