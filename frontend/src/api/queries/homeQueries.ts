import { gql } from '@apollo/client'

export const GET_MAIN_PAGE_DATA = gql`
  query GetMainPageData {
    recentProjects(limit: 5) {
      createdAt
      key
      leaders
      name
      openIssuesCount
      repositoriesCount
      type
    }
    recentPosts(limit: 6) {
      authorName
      authorImageUrl
      publishedAt
      title
      url
    }
    recentChapters(limit: 5) {
      createdAt
      key
      leaders
      name
      suggestedLocation
    }
    topContributors(limit: 18) {
      name
      login
      avatarUrl
      projectName
      projectUrl
    }
    recentIssues(limit: 5) {
      commentsCount
      createdAt
      title
      url
      author {
        avatarUrl
        login
        name
      }
    }
    recentReleases(limit: 5) {
      author {
        avatarUrl
        login
        name
      }
      name
      publishedAt
      tagName
      url
    }
    recentPullRequests(limit: 5) {
      author {
        avatarUrl
        login
        name
      }
      createdAt
      title
      url
    }
    sponsors {
      imageUrl
      name
      sponsorType
      url
    }
    statsOverview {
      activeChaptersStats
      activeProjectsStats
      contributorsStats
      countriesStats
    }
    upcomingEvents(limit: 6) {
      category
      endDate
      key
      name
      startDate
      summary
      suggestedLocation
      url
    }
  }
`
