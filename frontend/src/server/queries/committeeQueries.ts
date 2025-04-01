import { gql } from '@apollo/client'

export const GET_COMMITTEE_DATA = gql`
  query GetCommittee($key: String!) {
    committee(key: $key) {
      contributorsCount
      createdAt
      forksCount
      issuesCount
      leaders
      name
      relatedUrls
      repositoriesCount
      starsCount
      summary
      topContributors {
        avatarUrl
        contributionsCount
        login
        name
      }
      updatedAt
      url
    }
  }
`
