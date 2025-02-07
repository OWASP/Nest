import { gql } from '@apollo/client'

export const GET_COMMITTEE_DATA = gql`
  query GetCommittee($key: String!) {
    committee(key: $key) {
      createdAt
      leaders
      name
      relatedUrls
      topContributors {
        avatarUrl
        contributionsCount
        login
        name
      }
      summary
      updatedAt
      url
    }
  }
`
