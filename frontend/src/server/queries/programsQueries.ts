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

export const GET_PROGRAM_DETAILS = gql`
  query GetProgramDetails($programKey: String!) {
    program(programKey: $programKey) {
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
    program(programKey: $programKey) {
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
    modulesByProgram(programKey: $programKey) {
      id
      key
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
      key
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
      key
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

export const GET_PROGRAM_ADMIN_DETAILS = gql`
  query GetProgramDetails($programKey: String!) {
    program(programKey: $programKey) {
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

export const UPDATE_PROGRAM_STATUS_MUTATION = gql`
  mutation updateProgramStatus($inputData: UpdateProgramStatusInput!) {
    updateProgramStatus(inputData: $inputData) {
      key
      status
    }
  }
`
