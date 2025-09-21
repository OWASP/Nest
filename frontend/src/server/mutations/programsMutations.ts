import { gql } from '@apollo/client'

export const UPDATE_PROGRAM = gql`
  mutation UpdateProgram($input: UpdateProgramInput!) {
    updateProgram(inputData: $input) {
      id
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
        id
        login
        name
        avatarUrl
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
      experienceLevels
      startedAt
      endedAt
      tags
      domains
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
      id
      key
      status
    }
  }
`
