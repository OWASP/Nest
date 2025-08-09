import { gql } from '@apollo/client'

export const GET_MAIN_PAGE_DATA = gql`
  query GetMainPageData($distinct: Boolean) {
    recentProjects(limit: 3) {
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
    recentChapters(limit: 3) {
      createdAt
      key
      leaders
      name
      suggestedLocation
    }
    topContributors(hasFullName: true, limit: 40) {
      avatarUrl
      login
      name
    }
    recentIssues(limit: 5, distinct: $distinct) {
      author {
        avatarUrl
        login
        name
      }
      createdAt
      organizationName
      repositoryName
      title
      url
    }
    recentPullRequests(limit: 5, distinct: $distinct) {
      author {
        avatarUrl
        login
        name
      }
      createdAt
      organizationName
      repositoryName
      title
      url
    }
    recentReleases(limit: 5, distinct: $distinct) {
      author {
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
      slackWorkspaceStats
    }
    upcomingEvents(limit: 9) {
      category
      endDate
      key
      name
      startDate
      summary
      suggestedLocation
      url
    }
    recentMilestones(limit: 5, state: "all", distinct: $distinct) {
      author {
        avatarUrl
        login
        name
      }
      title
      openIssuesCount
      closedIssuesCount
      repositoryName
      organizationName
      createdAt
      url
    }
  }
`
