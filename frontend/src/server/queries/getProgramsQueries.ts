import { gql } from '@apollo/client'

export const GET_PROGRAM_DATA = gql`
  query GetPrograms($page: Int!, $search: String, $mentorUsername: String) {
    allPrograms(page: $page, search: $search, mentorUsername: $mentorUsername) {
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
  query GetProgramDetails($programId: ID!) {
    program(programId: $programId) {
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
export const GET_PROGRAM_AND_MODULES = gql`
  query GetProgramAndModules($programId: ID!) {
    program(programId: $programId) {
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
    modulesByProgram(programId: $programId) {
      id
      name
      description
      experienceLevel
      startedAt
      endedAt
    }
  }
`

export const UPDATE_PROGRAM = gql`
  mutation UpdateProgram($input: UpdateProgramInput!) {
    updateProgram(inputData: $input) {
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

export const CREATE_PROGRAM = gql`
  mutation CreateProgram($input: CreateProgramInput!) {
    createProgram(inputData: $input) {
      id
      name
      description
      menteesLimit
      startedAt
      endedAt
      experienceLevels
      tags
      domains
      status
      admins {
        login
        name
        avatarUrl
      }
    }
  }
`

export const GET_PROGRAM_MENTOR_DETAILS = gql`
  query GetProgramDetails($programId: ID!) {
    program(programId: $programId) {
      id
      name
      admins {
        login
        name
        avatarUrl
      }
    }
  }
`

export const UPDATE_PROGRAM_STATUS_MUTATION = gql`
  mutation UpdateProgram($inputData: UpdateProgramInput!) {
    updateProgram(inputData: $inputData) {
      id
      status
    }
  }
`
