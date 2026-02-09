import { gql } from '@apollo/client'

export const GET_COMMUNITY_PAGE_DATA = gql`
  query GetCommunityPageData {
    recentChapters(limit: 6) {
      id
      createdAt
      key
      leaders
      name
      suggestedLocation
    }
    recentOrganizations(limit: 5) {
      id
      avatarUrl
      login
      name
    }
    snapshots(limit: 5) {
      id
      key
      title
      startAt
      endAt
    }
    topContributors(hasFullName: true, limit: 12) {
      id
      avatarUrl
      login
      name
    }
    statsOverview {
      activeChaptersStats
      activeProjectsStats
      contributorsStats
      countriesStats
    }
  }
`
