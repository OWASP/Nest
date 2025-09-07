import { gql } from '@apollo/client'

export const GET_MAIN_PAGE_DATA = gql`
  query GetMainPageData($distinct: Boolean) {
    recentProjects(limit: 3) {
      id
      createdAt
      key
      leaders
      name
      openIssuesCount
      repositoriesCount
      type
    }
    recentPosts(limit: 6) {
      id
      authorName
      authorImageUrl
      publishedAt
      title
      url
    }
    recentChapters(limit: 3) {
      id
      createdAt
      key
      leaders
      name
      suggestedLocation
    }
    topContributors(hasFullName: true, limit: 40) {
      id
      avatarUrl
      login
      name
    }
    recentIssues(limit: 5, distinct: $distinct) {
      id
      author {
        id
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
      id
      author {
        id
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
    sponsors {
      id
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
      id
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
      id
      author {
        id
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
