import { gql } from '@apollo/client'

export const UPDATE_PROGRAM = gql`
  mutation UpdateProgram($input: UpdateProgramInput!) {
    updateProgram(inputData: $input) {
      description
      domains
      endedAt
      experienceLevels
      id
      key
      menteesLimit
      name
      startedAt
      status
      tags
      admins {
        avatarUrl
        id
        login
        name
      }
    }
  }
`

export const CREATE_PROGRAM = gql`
  mutation CreateProgram($input: CreateProgramInput!) {
    createProgram(inputData: $input) {
      description
      domains
      endedAt
      experienceLevels
      id
      key
      menteesLimit
      name
      startedAt
      tags
      admins {
        avatarUrl
        login
        name
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
