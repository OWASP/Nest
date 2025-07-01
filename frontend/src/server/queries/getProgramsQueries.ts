import { gql } from '@apollo/client'

export const GET_PROGRAM_DATA = gql`
  query GetPrograms($page: Int!, $search: String) {
    allPrograms(page: $page, search: $search) {
      totalPages
      currentPage
      programs {
        id
        name
        description
        status
        startedAt
        endedAt
      }
    }
  }
`

export const GET_PROGRAM_DETAILS = gql`
  query GetProgramDetails($id: ID!) {
    program(id: $id) {
      id
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

export const UPDATE_PROGRAM = gql`
  mutation UpdateProgram($input: UpdateProgramInput!) {
    updateProgram(input: $input) {
      id
      name
      description
      status
      menteesLimit
      experienceLevels
      startedAt
      endedAt
      tags
      domains
      admins {
        login
      }
    }
  }
`
