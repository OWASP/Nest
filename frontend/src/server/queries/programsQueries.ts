import { gql } from '@apollo/client'

export const GET_PROGRAM_DATA = gql`
  query GetPrograms($page: Int!, $search: String, $mentorUsername: String) {
    allPrograms(page: $page, search: $search, mentorUsername: $mentorUsername) {
      totalPages
      currentPage
      programs {
        id
        key
        name
        description
        status
        startedAt
        endedAt
      }
    }
  }
`

export const GET_MY_PROGRAMS = gql`
  query GetMyPrograms($search: String, $page: Int, $limit: Int) {
    myPrograms(search: $search, page: $page, limit: $limit) {
      currentPage
      totalPages
      programs {
        id
        key
        name
        description
        startedAt
        endedAt
        userRole
      }
    }
  }
`

export const GET_PROGRAM_DETAILS = gql`
  query GetProgramDetails($programKey: String!) {
    getProgram(programKey: $programKey) {
      id
      key
      name
      description
      status
      menteesLimit
      experienceLevels
      startedAt
      endedAt
      domains
      tags
      admins {
        login
        name
        avatarUrl
      }
    }
  }
`
export const GET_PROGRAM_AND_MODULES = gql`
  query GetProgramAndModules($programKey: String!) {
    getProgram(programKey: $programKey) {
      id
      key
      name
      description
      status
      menteesLimit
      experienceLevels
      startedAt
      endedAt
      domains
      tags
      admins {
        login
        name
        avatarUrl
      }
    }
    getProgramModules(programKey: $programKey) {
      id
      key
      name
      description
      experienceLevel
      startedAt
      endedAt
      mentors {
        login
        name
        avatarUrl
      }
    }
  }
`

export const GET_PROGRAM_ADMIN_DETAILS = gql`
  query GetProgramDetails($programKey: String!) {
    getProgram(programKey: $programKey) {
      id
      key
      name
      admins {
        login
        name
        avatarUrl
      }
    }
  }
`
