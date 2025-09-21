import { gql } from '@apollo/client'
import { CONTRIBUTOR_FIELDS, PROJECT_METADATA_FIELDS } from 'server/fragments/projectFragments'

export const GET_PROJECT_DATA = gql`
  ${CONTRIBUTOR_FIELDS}
  query GetProject($key: String!) {
    project(key: $key) {
      id
      contributorsCount
      forksCount
      issuesCount
      isActive
      key
      languages
      leaders
      level
      name
      healthMetricsList(limit: 30) {
        id
        createdAt
        forksCount
        lastCommitDays
        lastCommitDaysRequirement
        lastReleaseDays
        lastReleaseDaysRequirement
        openIssuesCount
        openPullRequestsCount
        score
        starsCount
        unassignedIssuesCount
        unansweredIssuesCount
      }
      recentIssues {
        author {
          id
          avatarUrl
          login
          name
          url
        }
        createdAt
        organizationName
        repositoryName
        title
        url
      }
      recentReleases {
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
      repositories {
        id
        contributorsCount
        forksCount
        key
        name
        openIssuesCount
        organization {
          login
        }
        starsCount
        subscribersCount
        url
      }
      repositoriesCount
      starsCount
      summary
      topics
      type
      updatedAt
      url
      recentMilestones(limit: 5) {
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
      recentPullRequests {
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
    }
    topContributors(project: $key) {
      ...ContributorFields
    }
  }
`

export const GET_PROJECT_METADATA = gql`
  ${PROJECT_METADATA_FIELDS}
  query GetProjectMetadata($key: String!) {
    project(key: $key) {
      ...ProjectMetadataFields
    }
  }
`

export const GET_TOP_CONTRIBUTORS = gql`
  ${CONTRIBUTOR_FIELDS}
  query GetTopContributors(
    $excludedUsernames: [String!]
    $hasFullName: Boolean = false
    $key: String!
    $limit: Int = 20
  ) {
    topContributors(
      excludedUsernames: $excludedUsernames
      hasFullName: $hasFullName
      limit: $limit
      project: $key
    ) {
      ...ContributorFields
    }
  }
`

export const SEARCH_PROJECTS = gql`
  query SearchProjectNames($query: String!) {
    searchProjects(query: $query) {
      id
      name
    }
  }
`
