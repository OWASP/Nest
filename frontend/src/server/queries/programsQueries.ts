import { gql } from '@apollo/client'

export const GET_MY_PROGRAMS = gql`
  query GetMyPrograms($search: String, $page: Int, $limit: Int) {
    myPrograms(search: $search, page: $page, limit: $limit) {
      currentPage
      totalPages
      programs {
        id
        key
        name
        status
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
        id
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
        id
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
      domains
      tags
      labels
      mentors {
        id
        login
        name
        avatarUrl
      }
      mentees {
        id
        login
        name
        avatarUrl
      }
    }
  }
`

export const GET_PROGRAM_ADMIN_DETAILS = gql`
  query GetProgramAdminDetails($programKey: String!) {
    getProgram(programKey: $programKey) {
      id
      key
      name
      startedAt
      endedAt
      admins {
        id
        login
        name
        avatarUrl
      }
    }
  }
`
