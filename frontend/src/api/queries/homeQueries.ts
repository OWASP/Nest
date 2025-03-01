import { gql } from '@apollo/client'

export const GET_MAIN_PAGE_DATA = gql`
  query GetMainPageData {
    recentProjects(limit: 5) {
      name
      type
      createdAt
      key
      openIssuesCount
      repositoriesCount
    }
    recentChapters(limit: 5) {
      name
      createdAt
      suggestedLocation
      region
      key
      topContributors {
        name
      }
    }
    topContributors(limit: 18) {
      name
      login
      contributionsCount
      avatarUrl
      repositoryName
      repositoryUrl
    }
    recentIssues(limit: 5) {
      commentsCount
      createdAt
      number
      title
      url
      author {
        avatarUrl
        login
        name
        url
      }
    }
    recentReleases(limit: 5) {
      author {
        avatarUrl
        name
      }
      isPreRelease
      name
      publishedAt
      tagName
    }
    statsOverview {
      activeChaptersStats
      activeProjectsStats
      contributorsStats
      countriesStats
    }
  }
`
