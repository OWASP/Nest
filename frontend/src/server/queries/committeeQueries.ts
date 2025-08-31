import { gql } from '@apollo/client'

export const GET_COMMITTEE_DATA = gql`
  query GetCommittee($key: String!) {
    committee(key: $key) {
      id
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
      id
      avatarUrl
      login
      name
    }
  }
`

export const GET_COMMITTEE_METADATA = gql`
  query GetCommittee($key: String!) {
    committee(key: $key) {
      id
      name
      summary
    }
  }
`
