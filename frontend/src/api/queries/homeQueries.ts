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
      suggestedLocation
      region
      key
      topContributors {
        name
      }
    }
    topContributors(limit: 15) {
      name
      login
      contributionsCount
      avatarUrl
    }
    recentIssue(limit: 5) {
      commentsCount
      createdAt
      number
      title
      author {
        avatarUrl
        name
      }
    }
    recentRelease(limit: 5) {
      author {
        avatarUrl
        name
      }
      isPreRelease
      name
      publishedAt
      tagName
    }
    countsOverview {
      chaptersCount
      countriesCount
      activeProjectsCount
      contributorsCount
    }
  }
`
