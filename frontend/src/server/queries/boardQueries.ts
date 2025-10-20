import { gql } from '@apollo/client'

export const GET_BOARD_CANDIDATES = gql`
  query GetBoardCandidates($year: Int!) {
    boardOfDirectors(year: $year) {
      id
      year
      owaspUrl
      candidates {
        id
        memberName
        memberEmail
        description
        member {
          id
          login
          name
          avatarUrl
          bio
          createdAt
          firstOwaspContributionAt
        }
      }
    }
  }
`

export const GET_MEMBER_SNAPSHOT = gql`
  query GetMemberSnapshot($userLogin: String!) {
    memberSnapshot(userLogin: $userLogin) {
      id
      startAt
      endAt
      commitsCount
      pullRequestsCount
      issuesCount
      totalContributions
      contributionHeatmapData
      chapterContributions
      projectContributions
      githubUser {
        login
      }
    }
  }
`

export const GET_CHAPTER_BY_KEY = gql`
  query GetChapterByKey($key: String!) {
    chapter(key: $key) {
      id
      key
      name
      url
    }
  }
`

export const GET_PROJECT_BY_KEY = gql`
  query GetProjectByKey($key: String!) {
    project(key: $key) {
      id
      key
      name
      level
      type
      url
    }
  }
`
