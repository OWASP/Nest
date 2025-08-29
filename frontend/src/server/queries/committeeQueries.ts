import { gql } from '@apollo/client'

export const GET_COMMITTEE_DATA = gql`
  query GetCommitteeData($key: String!) {
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
      updatedAt
      url
    }
    topContributors(committee: $key) {
      avatarUrl
      login
      name
    }
  }
`

export const GET_COMMITTEE_METADATA = gql`
  query GetCommitteeMetadata($key: String!) {
    committee(key: $key) {
      name
      summary
    }
  }
`
