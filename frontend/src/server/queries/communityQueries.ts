import { gql } from '@apollo/client'

export const GET_COMMUNITY_PAGE_DATA = gql`
  query GetCommunityPageData(
    $distinct: Boolean
    $recentReleasesLimit: Int = 6
    $topContributorsLimit: Int = 10
  ) {
    topContributors(hasFullName: true, limit: $topContributorsLimit) {
      id
      avatarUrl
      login
      name
    }
    recentReleases(limit: $recentReleasesLimit, distinct: $distinct) {
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
    statsOverview {
      activeChaptersStats
      activeProjectsStats
      contributorsStats
      countriesStats
      slackWorkspaceStats
    }
  }
`
